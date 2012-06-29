#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

#    Prototype of the MS0x00 ANRV Operating Software 
#      - Basic RPC Component Class
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

import inspect

from pprint import pprint

from ANRV.System.Registry import ComponentTemplates
from ANRV.System.ConfigurableComponent import ConfigurableComponent

from ANRV.Messages import Message

class RPCComponent(ConfigurableComponent):
    """Basic RPC Component.

    Has no real function but:
    * Automated Method register via
     * Method annotations
     * Docstrings
     * Only registers methods beginning with "rpc_"
    * realized by _buildMethodRegister

    See these examples about the annotations necessary to complete this:
    
    def rpc_set(self, val: [int, 'New integer value to set']):
        "Sets the internal integer to a given value."
        self.value = val

    def rpc_complex(self, summandA: [int, 'Primary summand'], summandB: [int, 'Secondary summand']):
        "Adds to given integer summands together to the stored value."
        self.value += summandA + summandB

    def rpc_reset(self):
        "Resets the internal integer to the specified reset value."
        self._reset()

    TODO: 
    * Correct documentation
    * Automate RPC calling somehow, somewhere (smart)
    * RPC Variables? (With automatic getters and setters - by config?)
    * Security! (Here?)
    """
    Inboxes = {"inbox": "RPC commands",
               "control": "Signaling to this Protocol"}
    Outboxes = {"outbox": "RPC Responses",
                "signal": "Signaling from this Protocol"}
    MethodRegister = {}

#    def rpc_default(self, arg):
#       """Default Method"""
#        # TODO: Do we need a default rpc method? Why? What could we do with it?
#        pass

    def rpc_updateComponentInfo(self, arg):
        """RPC Function '''updateComponentInfo'''

        Updates this RPCComponent's methodregister.

        Returns True upon completion.
        """

        return self._buildMethodRegister()

    def rpc_getComponentInfo(self, arg):
        """RPC Function '''getComponentInfo'''

        Returns this RPCComponent's methodregister.
        """

        return self._getComponentInfo()

    def rpc_getConfiguration(self, arg):
        """RPC wrapper for ConfigurableComponent"""
        return self.GetConfiguration()

    def rpc_writeConfiguration(self, arg):
        """RPC wrapper for ConfigurableComponent"""
        return self.WriteConfiguration()

    def rpc_readConfiguration(self, arg):
        """RPC wrapper for ConfigurableComponent"""
        return self.ReadConfiguration()

    def rpc_hasConfiguration(self, arg):
        """RPC wrapper for ConfigurableComponent"""
        return self.HasConfiguration()


    def handleRPC(self, msg):
        """Handles RPC requests by
        * first checking for the correct recipient
        * looking up wether the RPC Method actually exists
        * trying to get a hold on to the actual function
        * calling it
        * returning the methods result as RPC Response

        = Important Requirement =
        For every component that intends to do RPC and react to requests,
        the function 'main' has to call '''handleRPC(msg)''' upon message
        reception.
        """
        # TODO: Grand unified error responses everywhere, needs a well documented standard.

        if msg.recipient == self.name:
            # TODO: Type checking!
            if msg.func in self.MethodRegister:
                method = getattr(self, "rpc_" + msg.func)
                if method:
                    result = method(msg.arg)
                    return msg.response(result)
                else:
                    self.logerror("Requested Method in register, but not found.")
                    return msg.response(["ERROR", "Method not found."])
            else:
                self.logwarning("Requested Method not found: %s" % msg.func)
                return msg.response(["ERROR", "Method not found."])
        else:
            self.logwarning("Received a message without being the recipient!")

    def _getComponentInfo(self):
        """Returns this component's metadescription including its MethodRegister"""

        return [self.name, self.__doc__, self.MethodRegister]

    def _buildMethodRegister(self):
        """Builds the RPC register by analyzing all methods beginning with "rpc_".
        Every found method will be added to the register together with its annotations.
        """
        # TODO: This has to be thrown out in a higher subclass of Axon.Component, it is not only relevant to RPC
        # TODO: Consider a tiny datastructure to store the data in a conveniently addressable way.
        self.MethodRegister = {}
        self.loginfo("Building method register.")
        for method in inspect.getmembers(self):
            if method[0].startswith("rpc_") or method[0] == "__init__":
                if method[0] == "__init__":
                    name = "initialization"
                else:
                    name = method[0][4:]
                params = inspect.getfullargspec(method[1]).annotations
                doc = inspect.getdoc(method[1])
                self.MethodRegister[name] = [params, doc]
        return True

    def __init__(self):
        """Initializes this RPC Component. Don't forget to call super(RPCComponent, self).__init__()"""
        super(RPCComponent, self).__init__()
        self._buildMethodRegister()

    def main(self):
        """Start the already initialized component and wait for messages.
        Manually (currently) process each RPC request and call the appropriate function.
        Send back the response of the function call as RPC answer.
        """
        while True:
            while not self.anyReady():
                yield 1
            msg = None
            response = None

            if self.dataReady("inbox"):
                self.logdebug("Handling incoming rpc messages.")
                msg = self.recv("inbox")
                response = self.handleRPC(msg)
            if response:
                self.logdebug("Sending response to '%s'" % response.recipient)
                self.send(response, "outbox")
            yield 1

    def shutdown(self):
        """Shutdown of RPC Components is heavy WiP!"""
        # TODO: Handle correct shutdown
        if self.dataReady("control"):
            msg = self.recv("control")
            return isinstance(msg, Axon.Ipc.producerFinished)

# TODO: These (and other baseclass components) shouldn't be listed unless being tested
# * ConfigurableComponent
# * Dispatcher
ComponentTemplates["RPCComponent"] = [RPCComponent, "RPC capable Component"]
