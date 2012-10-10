#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#from flup.server.fcgi import WSGIServer
import bottle

from ANRV.System.Registry import ComponentTemplates
from ANRV.System.RPCComponent import RPCComponentThreaded
from ANRV.System.LoggableComponent import LoggableComponent

import Axon

class WSGIGateway(RPCComponentThreaded):
    def __init__(self):
        super(WSGIGateway, self).__init__()
        self.app = bottle.Bottle()
        self._setRoutes()

    def _setRoutes(self):
        self.loginfo("Setting up routes.")

        # Create a route by hand
        pseudoroute = bottle.Route(self.app, "/pseudowsgi/<path>", "GET", self.pseudowsgi)

        # Add route
        self.app.router.add("/pseudowsgi/<path>", "GET", pseudoroute)

        # The following, it doesn't work. :(
        self.app.route('/pseudowsgi/<path>', self.pseudowsgi)

    def pseudowsgi(self, **kwargs):
        print(bottle.request.url)
        print(bottle.response)
        for cookie in bottle.request.cookies:
            print(cookie)
        return "FOOBAR %s" % kwargs

    def main(self):
        self.loginfo("Starting bottle server.")
        # TODO: Do this in a safe way (ie don't crash upon already opened port, etc)
        bottle.run(app=self.app, host="localhost", port=5555, debug=False)


ComponentTemplates["WSGIGateway"] = [WSGIGateway, "WSGI Gateway component"]
