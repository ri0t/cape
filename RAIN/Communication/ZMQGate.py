#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#    Prototype of the RAIN Operating Software
#    Copyright (C) 2011-2012 riot <riot@hackerfleet.org>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Preliminary testing ZMQ gateway component.

The intention of this component is to integrate ZMQ as node-to-node communication protocol
into RAIN.
"""

from RAIN.Messages import Message
from RAIN.System import Identity
from RAIN.System import Registry
from RAIN.System.RPCComponent import RPCComponentThreaded
from RAIN.System.NodeConnector import NodeConnector

from time import sleep

import jsonpickle
import zmq

from collections import deque

class ZMQConnector(RPCComponentThreaded, NodeConnector):
    """Exemplary and experimental ZMQ node interconnector class."""

    routeraddress = "192.168.1.42" # Fixed for testing purposes.
    separator = b"\r\n"

    def __init__(self):
        print "BEGIN INIT"
        self.MR['rpc_transmit'] = {'msg':
                                   [Message, 'Message to transmit via ZMQ.']}
        self.MR['rpc_discoverNode'] = {'ip': [str, 'IP to discover']}
        self.MR['rpc_listconnectedNodes'] = {}
        super(ZMQConnector, self).__init__()

        self.buflist = deque()

        # Schema:
        # {NodeUUID: ['IP-Address', ZMQ-Socket]}
        self.probednodes = {}
        self.nodes = {} #Identity.SystemUUID: {'ip': '127.0.0.1', 'socket': None}}
        
        self.url = "tcp://%s:55555" % ZMQConnector.routeraddress

        self.listening = False

        self.loginfo("Setting up socket '%s'" % self.url)
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.ROUTER)
        try:
            self.socket.bind(self.url)
            self.listening = True
            self.loginfo("Socket bound")
        except zmq.core.error.ZMQError:
            self.logcritical("Couldn't bind socket: Already in use!")
        print "END INIT"

    def rpc_transmit(self, msg):
        if msg.recipientNode == Identity.SystemUUID:
            errmsg = "(Unsent) message to ourself received for distribution: '%s'" % msg
            self.logerror(errmsg)
            return (False, errmsg)

        if not msg.recipientNode in self.nodes:
            errmsg = "Node '%s' unknown."
            self.logwarning(errmsg)
            return (False, errmsg)

        socket = self.nodes[msg.recipientNode]['socket']

        if not socket:
            # Connection not already established, so connect and store for later
            return (False, "Node not connected. Why?")

        socket.send(msg)
        return True

    def rpc_discoverNode(self, ip):
        if ip not in self.probednodes:
            msg = "Probing new node: '%s'" % ip
            self.logdebug(msg)
            self._discoverNode(ip)
            return True, msg
        else:
            self.logerror("Node has already been discovered: '%s'" % ip)
            return False

    def _discoverNode(self, ip):
        self.loginfo("Discovering node '%s'" % ip)
        socket = self.context.socket(zmq.DEALER)
        socket.connect('tcp://%s:55555' % ip)
        # TODO: Is this smart, sending discovery data upon first message?
        # Maybe better in the reply...
        msg = Message(sendernode=Identity.SystemUUID,
                      sender=self.name,
                      recipient='ZMQConnector',
                      func="discover",
                      arg={'ip': ZMQConnector.routeraddress,
                           'registry': str(self.systemregistry),
                           'dispatcher': str(self.systemdispatcher),
                           }
                      )
        socket.send(jsonpickle.encode(msg))
        
        self.probednodes[ip] = socket
        
        self.logdebug("Discovery sent to '%s'" % ip)

    def rpc_listconnectedNodes(self):
        return str(self.nodes.keys())

    def mainthread(self):
        #self.logdebug("BEGIN THREAD")
        msg = incoming = None        
        
        # If listening, collect incoming buffer
        if self.listening:
            try:
                incoming = self.socket.recv(zmq.NOBLOCK)
                self.logdebug("Received '%s'" % incoming)
            except zmq.core.error.ZMQError as e:
                if not "Resource temporarily unavailable" in str(e):
                    self.logerror(e)
                    
        # Split buffer, if we have some
        if incoming:
            #self.logdebug("Splitting")
            # new piece of a message arrived
            parts = incoming.split(ZMQConnector.separator)
            
            self.logdebug("Length of incoming: %i" % len(parts))
            
            for part in parts:
                self.logdebug(part)
                if len(part) > 0:
                    self.buflist.append(part.rstrip(ZMQConnector.separator))
        
        # If there are messages, decode and process them
        if len(self.buflist) > 0:
            jsonmsg = self.buflist.popleft()
            #self.logdebug("DECODING (%i left)" % len(self.buflist))
            try:
                msg = jsonpickle.decode(jsonmsg)
            except Exception as e:
                self.logdebug(jsonmsg)
                self.logerror("JSON decoding failed: '%s'" % e)

            if msg:
                self.loginfo("ANALYSING '%s'" % msg )

                if (msg.recipient == "ZMQConnector" and msg.type == 'request'):
                    if msg.func == "discover":
                        if msg.sendernode in self.nodes:
                            self.loginfo("Node already connected: '%s'" % msg.sendernode)
                        elif msg.arg['ip'] in self.probednodes:
                            # Node is already known.
                            # This boils down to: We probed it, it now probes us
                            self.loginfo("Storing probed node '%s' @ '%s'" % (msg.sendernode, msg.arg['ip']))
                            self.nodes[msg.sendernode] = {'ip': msg.arg['ip'], 
                                                          'socket': self.probednodes[msg.arg['ip']]}
                        else:
                            self.loginfo("Replying discovery request to '%s'" % msg.arg['ip'])
                            msg = msg.response(str(self.systemregistry))
                            self._discoverNode(msg.arg['ip'])
                            
                # Oh, nothing for us, but someone else.
                # TODO: Now, we'd better check for security and auth.
                elif msg.recipientnode == Identity.SystemUUID:
                    self.loginfo("Publishing Message from '%s': '%s'" % (msg.sendernode, msg))
                    self.send(msg, "outbox")
                else:
                    self.logwarning("Message for another node received - WTF?!")
        else:
            self.logdebug("Sleeping.")
            sleep(1)
        self.logdebug("END THREAD")

Registry.ComponentTemplates['ZMQConnector'] = [ZMQConnector, "Node-to-node ØMQ Connector"]
