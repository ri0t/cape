#!/usr/bin/python3
# -*- coding: utf-8 -*-

#    Prototype of the MS0x00 cape Operating Software
#      - Dispatcher Component
#    Copyright (C) 2011-2012  riot <riot@hackerfleet.org>
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

import Axon
from Axon.AdaptiveCommsComponent import AdaptiveCommsComponent

from cape.system.rpccomponent import RPCMixin
from cape.system.basecomponent import basecomponent
from cape.system.loggablecomponent import LoggableComponent
from cape.system import registry
from cape.system import identity
from cape.messages import Message

class Dispatcher(AdaptiveCommsComponent, basecomponent, RPCMixin):
    inboxes = {'inbox': 'Dispatcher Inbox',
               'control': 'Not used yet.'}
    outboxes = {'outbox': 'Dispatcher Outbox',
                'signal': 'Not used yet.'}
    Components = []

    def __init__(self):
        AdaptiveCommsComponent.__init__(self)

        basecomponent.__init__(self)

        self.MR['rpc_addgateway'] = {'remotenode': [(str, unicode), 'UUID of remote node'],
                                     'connector': [str, 'Name of connector']}
        self.MR['rpc_listgateways'] = {}
        RPCMixin.__init__(self)

        # TODO: Evaluate renaming, gateway maybe hella confusing..
        self.gateways = {}

    def rpc_addgateway(self, remotenode, connector):
        self.gateways[remotenode] = connector
        self.loginfo(self.gateways)
        return True

    def rpc_listgateways(self):
        self.loginfo("Gatewaylist requested.")
        return self.gateways.keys() if (len(self.gateways) > 0) else False

    def RegisterComponent(self, thecomponent):
        self.logdebug("Trying to register new component")
        self.addChildren(thecomponent)

        newIn = self.addInbox(thecomponent.name)
        newOut = self.addOutbox(thecomponent.name)

        newState = "WAITING"
        linkToComponent = self.link((self, newOut), (thecomponent, "inbox"))
        linkFromComponent = self.link((thecomponent, "outbox"), (self, "inbox"))

        resource = thecomponent

        inboxes = [newIn]
        outboxes = [newOut]
        info = (newState, linkToComponent, linkFromComponent)
        self.trackResourceInformation(resource, inboxes, outboxes, info)

        self.trackResource(resource, newIn)

        thecomponent.activate()
        if isinstance(thecomponent, Axon.ThreadedComponent.threadedcomponent):
            pass

        self.Components.append(thecomponent)

        self.loginfo("Registered new component '%s'" % thecomponent.name)

        return True

    def main(self):
        def handleMessage(msg):
            if not msg.localRecipient:
                self.logcritical("Remote node message received for '%s'" % msg.recipientnode)
                if msg.recipientnode in self.gateways:
                    gateway = self.gateways[msg.recipientnode]
                    msg.sendernode = str(identity.SystemUUID)
                    forward = Message(sender=self.name,
                                      recipient=self.gateways[msg.recipientnode],
                                      func="transmit",
                                      arg={'msg': msg})
                    self.send(forward, gateway)
                else:
                    self.logwarning("Remote node '%s' not available." % msg.recipientnode)
                    self.logdebug("Offending sender: '%s'" % msg.sender)
            else:
                if msg.recipient in self.directory:
                    # Replace with real name
                    msg.recipient = self.directory[msg.recipient]
                if msg.recipient in self.inboxes:
                    self.send(msg, msg.recipient)
                else:
                    self.logerror('MESSAGE WITH ERRONEOUS RECIPIENT RECIEVED: %s\n%s\n' % (msg, self.inboxes))



        while True:
            while not self.anyReady():
                yield 1 # Twiddle thumbs.

            msg = self.recv()
            # Input! We have to act.

            if isinstance(msg, Message):
                response = None
                if msg.recipient == self.name:
                    self.loginfo("Handling incoming rpc messages.")

                    response = self.handleRPC(msg)
                    if response:
                        self.loginfo("Sending response to '%s'" % response.recipient)
                        handleMessage(response)

                else:
                    handleMessage(msg)


#                if response:
#                    if response.recipient in self.inboxes:
#                        self.logdebug("Responding to '%s'" % response.recipient)
#                        self.send(response, response.recipient)
#                    else:
#                        self.logerror("Response to '%s' can't be sent, not available." % response.recipient)
            else:
                self.logerror("Received something weird non-message: '%s'" % msg)

    def shutdown(self):
        # TODO: Handle correct shutdown
        if self.dataReady("control"):
            msg = self.recv("control")
            return isinstance(msg, Axon.Ipc.producerFinished)

registry.ComponentTemplates['Dispatcher'] = [Dispatcher, "Basic Dispatcher"]
