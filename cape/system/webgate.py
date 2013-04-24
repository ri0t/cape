#!/usr/bin/env python
# -*- coding: UTF-8 -*-


from cape.system.rpccomponent import RPCComponent
from cape.messages import Message

import cherrypy
from cherrypy import Tool
import jsonpickle
import os, time

from pprint import pprint

class WebGate(RPCComponent):
    """Cherrypy based Web Gateway Component for user interaction."""

    directory_name = "WebGate"

    class WebClient(object):
        def __init__(self, gateway=None, loader=None):
            self.gateway = gateway
            self.loader = loader
            self.responses = {}
            

        @cherrypy.expose
        def index(self):
            """
            Loader deliverably to give clients our loader javascript.
            """
            
            #pprint(cherrypy.request)
            self.gateway.loginfo("Client connected from '%s:%s." % (cherrypy.request.remote.ip,
                                                                    cherrypy.request.remote.port))

            #self.gateway.logdebug(str(cherrypy.request.__dict__))
            if self.loader:
                return self.loader

        def defer(self, request):
            # TODO: Needs a timeout and error checking etc.
            # Just looping around and wasting time is no good!
            while not request.recipient in self.responses:
                self.gateway.logdebug("Awaiting response for '%s'" % request)
                time.sleep(0.1)
                
            self.gateway.loginfo("Delivering response.")
            response = jsonpickle.encode(self.responses[request.recipient])
            
            # Clean up
            del(self.responses[request.recipient])
            del(self.gateway.defers[request.recipient])
            
            return response

        @cherrypy.expose
        #@cherrypy.tools.json_in
        def rpc(self):
            # Inconveniently decode JSON back to an object.
            # Actually this should be managed by cherrpy and jQuery,
            # alas that prove difficult.
            cl = cherrypy.request.headers['Content-Length']
            rawbody = cherrypy.request.body.read(int(cl))
            body = jsonpickle.decode(rawbody)
            recipient = body['recipient']
            func = body['func']
            arg = body['arg']
            
            # Suppose this should be the same for all calls to /rpc
            cherrypy.response.headers['Content-Type'] = 'application/json'
            
            # Replace simple directory addresses
            if recipient in self.gateway.directory:
                recipient = self.gateway.directory[recipient]
            
            msg = Message(sender=self.gateway.name, recipient=recipient, func=func, arg=arg)
            
            self.gateway.transmit(msg, self)
            
            # Store defer and wait for request's response
            return self.defer(msg)

    def handleResponse(self, msg):
        self.logdebug("Response received: '%s' Client References: '%s'" % (msg, self.defers))
        if msg.sender in self.defers:
            self.loginfo("Storing deferred response for delivery.")
            client = self.defers[msg.sender]['ref']
            client.responses[msg.sender] = msg

    def transmit(self, msg, clientref):
        self.logdebug("Transmitting on behalf of client '%s': '%s'" % (clientref, msg))
        self.defers[msg.recipient] = {'ref': clientref, 'msg':str(msg)}
        self.send(msg, "outbox")

    def rpc_startEngine(self):
        return self._start_Engine()

    def rpc_stopEngine(self):
        return self._stop_Engine()

    def rpc_restartEngine(self):
        result = self._stop_Engine()
        return result & self._start_Engine()

    def rpc_listDefers(self):
        return str(self.defers)

    def __init__(self):
        self.MR= {'rpc_startEngine': {},
                  'rpc_stopEngine': {},
                  'rpc_restartEngine': {},
                  'rpc_listDefers': {}
                 }
        super(WebGate, self).__init__()

        self.Configuration['debug'] = True
        self.Configuration['port'] = 8055
        self.Configuration['staticdir'] = os.path.join(os.path.abspath("."), "static")
        self.Configuration['serverenabled'] = True
        self.loader = None
        self.defers = {} # Schema: {msg.recipient: {ref:clientref,msg:msg}}
        
    def main_prepare(self):
        if self.Configuration['serverenabled']:
            self._start_Engine()
        else:
            self.logwarning("WebGate not enabled!")

    def _ev_client_connect(self):
        self.loginfo("Client connected: '%s'" % cherrypy.request)
        self.clients.append(cherrypy.request)
    
    def _readLoader(self):
        try:
            self.loader = open(os.path.join(self.Configuration['staticdir'], "index.html")).read()
        except Exception as e:
            self.logerror(str(e))

    def _stop_Engine(self):
        self.defers = {}
        cherrypy.engine.stop()
        return True # TODO: Make sure we really stopped it..

    def _start_Engine(self):
        cherrypy.config.update({'server.socket_port': self.Configuration['port'],
                                'server.socket_host': '0.0.0.0'})
        if self.Configuration['debug']:
            self.loginfo("Enabling debug (autoreload) mode for staticdir '%s'" % self.Configuration['staticdir'])
            
            for folder, subs, files in os.walk(self.Configuration['staticdir']):
                for filename in files:
                    self.loginfo("Autoreload enabled for: '%s'" % str(filename))
                    cherrypy.engine.autoreload.files.add(filename)

        cherrypy.tools.clientconnect = Tool('on_start_resource', self._ev_client_connect)
        config = {'/static':
                  {'tools.staticdir.on': True,
                   'tools.staticdir.dir': self.Configuration['staticdir']}
                 }
        self.logdebug(str(config))
        self._readLoader()
        self.logdebug(self.loader)

        cherrypy.tree.mount(self.WebClient(gateway=self, loader=self.loader), "/", config=config)
        cherrypy.engine.start()
        return True # TODO: Make sure we really started it..
