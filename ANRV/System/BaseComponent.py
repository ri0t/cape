#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

#    Prototype of the MS0x00 ANRV Operating Software 
#      - Basic Component Class
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
import uuid

from ANRV.System.Identity import SystemName
from ANRV.System.LoggableComponent import LoggableComponent

class BaseComponent(Axon.Component.component, LoggableComponent):
    """
    Basic Component

    Brings in various essential new attributes and few to none Methods.

    uuid - unique identifier of this component instance
    hdesc - human readable descriptor
    hname - human readable name
    systemname - current owning system

    """

    uuid = None
    hname = ""
    hdesc = ""
    systemname = SystemName

    def __init__(self, **kwargs):
        """Initializes this Configurable Component.
        Don't forget to call
            super(ConfigurableComponent, self).__init__()
        if you overwrite this.
        """
        # TODO: Do we want to be able to handle kwargs here?
        # They'll just get thrown upwards in the callchain and will then be bound as attributes, iirc.
        super(BaseComponent, self).__init__(**kwargs)
        self.uuid = uuid.uuid4()
        self.hdesc = "No description yet."
        self.hname = self.name

#ComponentTemplates["ConfigurableComponent"] = [ConfigurableComponent, "Configurable Component"]