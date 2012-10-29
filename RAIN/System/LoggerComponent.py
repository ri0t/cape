#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

#    Prototype of the MS0x00 ANRV Operating Software 
#      - Logger Service Component
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
from ANRV.System import Logging
from ANRV.System.Registry import ComponentTemplates
from ANRV.System.RPCComponent import RPCComponent

class LoggerComponent(RPCComponent):
    """
    Not yet implemented!

    Should - given enough time and code have passed by - be able to provide
    logs and certain methods on them, via RPC
    """
    # TODO: implement ;)

    def __init__(self):
        """Initializes this RPC Component. Don't forget to call super(RPCComponent, self).__init__()"""
        super(RPCComponent, self).__init__()

#ComponentTemplates["LoggerComponent"] = [LoggerComponent, "Not yet implemented! Log Service Component"]