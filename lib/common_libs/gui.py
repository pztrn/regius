import os
import sys

from PyQt5.QtWidgets import QApplication, QMainWindow

from dialogs.about_dialog import AboutDialog
from dialogs.debug_dialogs.logs import LogsDialog
from dialogs.options_dialog import OptionsDialog

class Gui(QMainWindow):
    def __init__(self, loader):
        QMainWindow.__init__(self)

        self.loader = loader
        self.loader.add_pointer("main.gui", self)

        self.log = self.loader.request_library("common_libs", "logger").log
        self.config = self.loader.request_library("common_libs", "config")
        self.options = OptionsDialog()

        self.migrator = self.loader.request_library("database_tools", "migrator")

        self.ui = self.loader.request_ui("ui/main_window", self)

        if not self.ui:
            # ToDo: make an exception about corrupted installation.
            pass

        # Set application name.
        self.ui.setWindowTitle(self.config.get_temp_value("main/application_name"))
        # OS X "hack" - set application title into Finder's top bar.
        # This requires pyobjc installed. So check for it first?
        if sys.platform == 'darwin':
            try:
                from Foundation import NSBundle
                bundle = NSBundle.mainBundle()
                if bundle:
                    info = bundle.localizedInfoDictionary() or bundle.infoDictionary()
                    if info and info['CFBundleName'] == 'Python':
                        info['CFBundleName'] = self.config.get_temp_value("main/application_name")
            except:
                self.log(0, "{RED}ERROR{RESET}: cannot import PyObjC module Foundation. Can't change application title.")

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

        # Replace some texts on some items in UI.
        self.ui.action_About.setText("&About {0}...".format(self.config.get_temp_value("main/application_name")))

        self.authorize()

        if self.config.get_temp_value("main/databaseless"):
            self.load_app()

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
        # Decrement steps by one for databaseless configuration.
        if self.config.get_temp_value("main/databaseless"):
            main_actions -= 1
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
        if not self.config.get_temp_value("main/databaseless"):
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
        # First - check Regius plugins.
        plugins_to_load = 0
        for item in os.listdir(os.path.join(self.config.get_temp_value("REGIUS_PATH"), "plugins")):
            plugins_to_load += 1

        # Second: check application-related plugins.
        for item in os.listdir(os.path.join(self.config.get_temp_value("SCRIPT_PATH"), "plugins")):
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
        # First - get regius plugins.
        regius_plugins = os.listdir(os.path.join(self.config.get_temp_value("REGIUS_PATH"), "plugins"))
        plugins = os.listdir(os.path.join(self.config.get_temp_value("SCRIPT_PATH"), "plugins"))
        self.log(2, "Found plugins:")
        self.log(2, "From regius: {regius_plugins}", {"regius_plugins": regius_plugins})
        self.log(2, "From {application_name}: {app_plugins}", {"app_plugins": plugins, "application_name": self.config.get_temp_value("main/application_name")})

        self.log(1, "Plugins list to load obtained, starting loading procedure...")

        for plugin in regius_plugins:
            self.loader.request_plugin(plugin)
            self.loading_widget.increment_progress()
            self.loading_widget.set_action("Plugin '{0}' loaded.".format(plugin))

        for plugin in plugins:
            self.loader.request_plugin(plugin)
            self.loading_widget.increment_progress()
            self.loading_widget.set_action("Plugin '{0}' loaded.".format(plugin))

