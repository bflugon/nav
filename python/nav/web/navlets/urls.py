#
# Copyright (C) 2013 UNINETT AS
#
# This file is part of Network Administration Visualized (NAV).
#
# NAV is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License version 2 as published by
# the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.  You should have received a copy of the GNU General Public
# License along with NAV. If not, see <http://www.gnu.org/licenses/>.
#
"""Module comment"""

from django.conf.urls import patterns, include, url
from . import list_navlets
from .portadmin import NavletPortadmin
from .machinetracker import MachineTrackerNavlet
from .status import StatusNavlet

urlpatterns = patterns('',
    url(r'^list-navlets/', list_navlets, name='list-navlets'),
    url(r'^portadmin/', NavletPortadmin.as_view(),
        name='navlet-portadmin'),
    url(r'^machinetracker/', MachineTrackerNavlet.as_view(),
        name='navlet-machinetracker'),
    url(r'^status/', StatusNavlet.as_view(),
        name='navlet-machinetracker')
)