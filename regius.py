#!/usr/bin/env python3

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

import os
import signal
import sys

from lib.common_libs import common
from lib.common_libs.loader import Loader

# Application instance.
window = None
app = None

class Regius:
    def __init__(self, preseed):
        if preseed["preseed"]["ui"] == "gui":
            common.TEMP_SETTINGS["UI"] = "gui"
        else:
            common.TEMP_SETTINGS["UI"] = "cli"

        # Initialize loader.
        self.loader = Loader()
        self.loader.add_pointer("main.main", self)
        common.LOADER = self.loader

        # Initialize logger.
        self.__logger = self.loader.request_library("common_libs", "logger")
        self.log = self.__logger.log
        # Set debug level.
        if "default_debug_level" in preseed["logger"]:
            self.__logger.set_debug_level(preseed["logger"]["default_debug_level"])

        # Initialize configuration.
        self.config = self.loader.request_library("common_libs", "config")
        # If application name wasn't specified in preseed file - set it
        # to default, "Regius".
        if not "app_name" in preseed["preseed"]:
            preseed["preseed"]["app_name"] = "Regius"
        self.config.load_configuration_from_files(preseed)
        self.config.parse_env()

        # After configuration was properly initialized we should set
        # some logger parameters.
        if "logger" in preseed:
            self.__logger.initialize_preliminary_parameters(self.config, preseed["logger"])
        else:
            self.__logger.initialize_preliminary_parameters(self.config)

        # We are still not initialized.
        self.config.set_temp_value("core/initialized", False)

        # Set application name from preseed config.
        if "app_name" in preseed["preseed"]:
            self.config.set_temp_value("main/application_name", preseed["preseed"]["app_name"])
        else:
            self.config.set_temp_value("main/application_name", "Regius")

        # Set application version from preseed config.
        if "version" in preseed["preseed"]:
            self.config.set_temp_value("main/application_version", preseed["preseed"]["version"])
        else:
            self.config.set_temp_value("main/application_version", "0.0.0-Unknown")

        # Next part will be executed only if GUI mode is activated.
        if preseed["preseed"]["ui"] == "gui":
            from lib.common_libs.gui import Gui
            Gui(self.loader)

        elif preseed["preseed"]["ui"] == "cli":
            # This part is executing if application using CLI.
            # ToDo: make it work.
            pass

    def get_loader(self):
        """
        Returns Loader() instance to caller.

        @retval Loader Loader() instance.
        """
        return self.loader

    def shutdown(self, *args):
        """
        Executes shutdown actions sequence.

        First it will execute shutdown method (on_shutdown()) on every
        loaded library and plugin. After all application will exit with
        exit code 1.
        """
        self.log(0, "Shutting down...")
        self.log(2, "Received {arg_count} arguments for shutdown type:", {"arg_count": len(args)})
        self.log(2, args)
        self.config.save_configuration()
        self.loader.shutdown()
        if len(args) == 0:
            print("Emergency shutdown completed")
            exit(1)
        else:
            print("Normal shutdown completed")

def init(preseed, app_path, app = None):
    common.TEMP_SETTINGS["REGIUS_PATH"] = "/".join(sys.modules["lib.common_libs.loader"].__file__.split("/")[:-3])
    common.TEMP_SETTINGS["SCRIPT_PATH"] = app_path
    #sys.path.insert(0, common.TEMP_SETTINGS["SCRIPT_PATH"])
    signal.signal(signal.SIGINT, shutdown)
    if preseed["preseed"]["ui"] == "gui":
        common.TEMP_SETTINGS["APP"] = app
        global window
        window = Regius(preseed)
        return (window, app)
        #exit(app.exec_())
    elif preseed["preseed"]["ui"] == "cli":
        global window
        window = Regius(preseed)
        return window

def shutdown(signal, frame):
    print("Got signal: {0}".format(signal))
    window.shutdown()
    exit()
