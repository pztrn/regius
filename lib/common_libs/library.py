# Regius application framework.
# Copyright (c) 2015 - 2016, Stanislav N. aka pztrn <pztrn at pztrn dot name>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import sys

from lib.common_libs import common

class Library:
    """
    This is a metaclass for all libraries. It will share some common actions
    between all libraries, for easier access.
    """

    def __init__(self):
        if sys.path[0] == common.TEMP_SETTINGS["SCRIPT_PATH"]:
            self._script_path = common.TEMP_SETTINGS["SCRIPT_PATH"]
        else:
            self._script_path = sys.path[0]

    def init_library(self):
        """
        Basic library initialization tasks, that should be done after
        instantiation and primary initialization is complete.

        This method should be overloaded, if needed. It will be executed
        after init_library_int().
        """
        pass

    def init_library_int(self, loader):
        """
        Basic library initialization tasks, that should be done after
        instantiation and primary initialization is complete.

        This method should not be overloaded.
        """
        self.loader = loader

        # Do not load logger more than once.
        # ToDo: rework with using temporary options.
        if hasattr(self, "_info") and self._info["shortname"] == "logger":
            pass
        else:
            self.log = self.loader.request_library("common_libs", "logger").log

        # Do not load configuration more than once.
        # ToDo: rework using temporary options.
        if hasattr(self, "_info") and self._info["shortname"] == "config":
            pass
        else:
            self.config = self.loader.request_library("common_libs", "config")

    def on_shutdown(self):
        """
        A placeholder for shutdown method. Every library MUST have own
        on_shutdown() implementation if want to execute some actions.
        """
        self.log(1, "Library '{CYAN}{library}{RESET}' have nothing to perform for shutdown", {"library": self._info["shortname"]})

        if "dialog" in self._info["shortname"]:
            if self.isVisible():
                self.log("1", "Dialog '{MAGENTA}{dialog}{RESET}' is opened, closing...", {"dialog": self._info["shortname"]})
                self.close()

    def __temporary_logger(self, level, data):
        """
        Temporary logging replacement. This method is used until real logger
        will be initialized and ready to use.
        """
        print("[LOGGER NOT INITIALIZED][LVL: {0}] {1}".format(level, data))
