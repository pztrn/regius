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

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow

from lib.common_libs import common
from lib.common_libs.loader import Loader

from dialogs.about_dialog import AboutDialog
from dialogs.debug_dialogs.logs import LogsDialog
from dialogs.options_dialog import OptionsDialog

# Application instance.
window = None
app = None

class Regius(QMainWindow):
    def __init__(self, preseed):
        QMainWindow.__init__(self)

        self.loader = Loader()
        self.loader.add_pointer("main.main", self)

        self.__logger = self.loader.request_library("common_libs", "logger")
        self.log = self.__logger.log

        self.config = self.loader.request_library("common_libs", "config")
        self.config.load_configuration_from_files(preseed)

        self.timer = self.loader.request_library("common_libs", "timer")

        # Prepare main database connection.
        self.database = self.loader.request_library("common_libs", "database")
        self.database.load_mappings()

        self.migrator = self.loader.request_library("database_tools", "migrator")

        # We are still not initialized.
        self.config.set_temp_value("core/initialized", False)

        # Set application name from preseed config.
        if "app_name" in preseed["preseed"]:
            self.config.set_temp_value("main/application_name", preseed["preseed"]["app_name"])
        else:
            self.config.set_temp_value("main/application_name", "Default application")

        if preseed["preseed"]["ui"] == "gui":
            self.options = OptionsDialog()

            self.ui = self.loader.request_ui("ui/main_window", self)

            if not self.ui:
                # ToDo: make an exception about corrupted installation.
                pass

            # Set application name.
            self.ui.setWindowTitle(self.config.get_temp_value("main/application_name"))

            # Restore window sizes and position.
            sizes = self.config.get_value("qsettings", "mainwindow", "size")
            position = self.config.get_value("qsettings", "mainwindow", "position")

            try:
                self.log(2, "Setting main window sizes: {sizes}", {"sizes": sizes})
                self.ui.resize(sizes)
            except TypeError as e:
                self.log(0, "Failed to restore window sizes! Falling back to default...")

            try:
                self.log(2, "Setting main window position: {position}", {"position": position})
                self.ui.move(position)
            except TypeError as e:
                self.log(0, "Failed to restore window position! Window manager will place window as he wants!")

            self.ui.show()

            # Connect neccessary signals for menu.
            self.ui.action_Options.triggered.connect(self.show_options)
            self.ui.action_Exit.triggered.connect(self.close)
            self.ui.actionShow_Logs.triggered.connect(self.show_logs_dialog)
            self.ui.action_About.triggered.connect(self.show_about_dialog)

            self.authorize()

    def authorize(self):
        """
        This method responsible for authorization process.
        """
        # Login failed text.
        login_failed = '<html><head/><body><p align="center"><span style=" font-weight:600; color:#ff7979;">Login failed</span></p></body></html>'
        self.login_widget = self.loader.request_library("ui", "login_widget")

    def closeEvent(self, event):
        """
        Overrides default QMainWindow.closeEvent() for taking extra
        actions on application close.
        """
        self.shutdown([False])
        event.accept()

    def get_loader(self):
        """
        Returns Loader() instance to caller.

        @retval Loader Loader() instance.
        """
        return self.loader

    def load_app(self):
        """
        """
        # Load loading widget.
        self.loading_widget = self.loader.request_library("ui", "loading_widget")

        # Counting action steps we will do.
        # For main window and framework itself we have this number of
        # actions.
        # As it cannot be actually predicted (or I don't know yet how to
        # to that) - it's hardcoded.
        main_actions = 6
        # Plugins count. Every plugin will take one position in progress
        # bar maximum value.
        plugins_actions = self.__get_plugins_count()
        # Summing.
        self.loading_widget.set_progress_maximum(main_actions + plugins_actions)
        # Cleaning up.
        del main_actions
        del plugins_actions

        # Show loading widget.
        self.loading_widget.set_appname(self.config.get_temp_value("main/application_name"))
        self.loading_widget.increment_progress()
        self.loading_widget.set_action("Main UI loaded.")

        self.__connect_signals()
        self.loading_widget.increment_progress()
        self.loading_widget.set_action("Main UI signals connected.")

        # Execute database migrations.
        self.loading_widget.set_action("Executing database migrations...")
        self.migrator.migrate()
        self.loading_widget.increment_progress()

        # Plugins loading.
        self.__load_plugins()
        self.loading_widget.increment_progress()
        self.loading_widget.set_action("Plugins loaded.")

        self.loading_widget.increment_progress()
        self.loading_widget.set_action("Main UI size and position restored.")

        self.config.set_temp_value("core/initialized", True)

        self.ui.statusbar.showMessage("{0} loaded.".format(self.config.get_temp_value("main/application_name")))
        self.loading_widget.increment_progress()
        self.loading_widget.set_action("Loading complete.")
        self.loading_widget.set_loading_complete()

    def show_about_dialog(self):
        """
        Shows About dialog.
        """
        about = AboutDialog()
        about.init_dialog(self.loader)
        about.show_dialog()

    def show_logs_dialog(self):
        """
        Shows logs dialog.
        """
        logs = LogsDialog()
        logs.init_dialog(self.loader)
        logs.load()

    def show_options(self):
        """
        Shows options dialog.
        """
        self.options.init_dialog(self.loader)
        self.options.show_dialog()

    def shutdown(self, *args):
        """
        Executes shutdown actions sequence.

        First it will execute shutdown method (on_shutdown()) on every
        loaded library and plugin. After all application will exit with
        exit code 1.
        """
        self.log(0, "Shutting down...")
        self.ui.statusbar.showMessage("Shutting down...")
        self.log(2, "Received {arg_count} arguments for shutdown type:", {"arg_count": len(args)})
        self.log(2, args)
        self.config.save_configuration()
        self.loader.shutdown()
        if len(args) == 0:
            print("Emergency shutdown completed")
            exit(1)
        else:
            print("Normal shutdown completed")

    def __connect_signals(self):
        """
        Connects main UI signals.
        """
        pass

    def __get_plugins_count(self):
        """
        This method counts plugins we will load and returns gathered
        count.

        This is used for loading widget progress bar maximum value
        calculation.
        """
        plugins_to_load = 0
        for item in os.listdir(os.path.join(common.TEMP_SETTINGS["SCRIPT_PATH"], "plugins")):
            plugins_to_load += 1

        if sys.path[0] != common.TEMP_SETTINGS["SCRIPT_PATH"]:
            for item in os.listdir(os.path.join(sys.path[0], "plugins")):
                plugins_to_load += 1

        return plugins_to_load

    def __load_plugins(self):
        """
        Loads plugins.

        If we have no active plugins list in configuration file - we
        will load all plugins. This could be changed in future.
        """
        self.log(0, "Loading plugins...")

        # Obtain plugins list.
        plugins = os.listdir(os.path.join(common.TEMP_SETTINGS["SCRIPT_PATH"], "plugins"))
        self.log(2, "Found plugins:")
        self.log(2, plugins)

        self.log(1, "Plugins list to load obtained, starting loading procedure...")

        for plugin in plugins:
            self.loader.request_plugin(plugin)
            self.loading_widget.increment_progress()
            self.loading_widget.set_action("Plugin '{0}' loaded.".format(plugin))

        if sys.path[0] != common.TEMP_SETTINGS["SCRIPT_PATH"]:
            self.log(0, "Loading application-related plugins...")
            plugins = os.listdir(os.path.join(sys.path[0], "plugins"))
            self.log(2, "Found plugins:")
            self.log(2, plugins)
            for plugin in plugins:
                self.loader.request_plugin(plugin)
                self.loading_widget.increment_progress()
                self.loading_widget.set_action("Plugin '{0}' loaded.".format(plugin))

def init(preseed, app):
    common.TEMP_SETTINGS["SCRIPT_PATH"] = "/".join(sys.modules["lib.common_libs.common"].__file__.split("/")[:-3])
    #sys.path.insert(0, common.TEMP_SETTINGS["SCRIPT_PATH"])
    signal.signal(signal.SIGINT, shutdown)
    if preseed["preseed"]["ui"] == "gui":
        common.TEMP_SETTINGS["APP"] = app
        global window
        window = Regius(preseed)
        return (window, app)
        #exit(app.exec_())
    elif preseed["preseed"]["ui"] == "cli":
        return Regius(preseed)

def shutdown(signal, frame):
    print("Got signal: {0}".format(signal))
    window.shutdown()
    exit()
