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
import sys

from lib.common_libs import common
from lib.common_libs.logger import Logger

class Loader:
    """
    This library responsible for all plugins and UI loading actions.
    Depending on passed parameter, it will load a library, or user interface.

    Loaded libraries will be placed into self.__libraries.
    Loaded plugins will be placed into self.__plugins.
    Loaded UIs will be placed into self.__uis.
    """

    _info = {
        "name"          : "Loader library",
        "shortname"     : "loader",
        "description"   : "This library responsible for all loading actions. All plugins parts should be loaded using this library."
    }

    def __init__(self):
        print("Initializing loader...")
        # Libraries instances.
        self.__libraries = {}
        # Plugins instances.
        self.__plugins = {}
        # Interface objects instances.
        self.__uis = {}
        # Dialogs instances.
        self.__dialogs = {}
        # Database mappings.
        self.__db_mappings = {}

        self.__script_path = common.TEMP_SETTINGS["SCRIPT_PATH"]
        self.__regius_path = common.TEMP_SETTINGS["REGIUS_PATH"]

        if not "LOGGER" in common.TEMP_SETTINGS:
            common.TEMP_SETTINGS["LOGGER"] = Logger()
            common.TEMP_SETTINGS["LOGGER"].initialize_logger()

        self.log = common.TEMP_SETTINGS["LOGGER"].log

        self.__libraries["COMMON_LIBS.LOGGER"] = common.TEMP_SETTINGS["LOGGER"]

    def add_pointer(self, name, pointer):
        """
        This method is used for manually adding pointer to something.

        @param name String which will represent pointer in loaded
        libraries dictionary.
        @param pointer Pointer to something.
        """
        if not name.upper() in self.__libraries:
            self.log(2, "Adding pointer to '{CYAN}{name}{RESET}' manually...", {"name": name.upper()})
            self.__libraries[name.upper()] = pointer
        else:
            self.log(2, "{RED}ERROR{RESET}: pointer to '{CYAN}{name}{RESET}' already exists!", {"name": name.upper()})

    def get_loaded_plugins(self):
        """
        Returns a dictionary with loaded plugins.

        @retval plugins_dict Dictionary with loaded plugins.
        """
        return self.__plugins

    def request_db_mapping(self, mapping_name):
        """
        Loads plugins that related to current worker.

        @param mapping_name Name of database mapping to load or lookup.
        @retval mapping Instance of ``lib.common_libs.database_mappings.{mapping_name}``.
        @retval None If database mapping loading was unsuccessful.
        """
        caller = sys._getframe(1).f_locals["self"].__class__.__name__
        if mapping_name.upper() in self.__db_mappings:
            self.log(2, "Already loaded, returning pointer to mapping '{CYAN}{db_mapping}{RESET}' to '{MAGENTA}{caller}{RESET}'", {"db_mapping": mapping_name.upper(), "caller": caller})
            return self.__db_mappings[mapping_name.upper()]
        else:
            self.log(1, "Mapping '{MAGENTA}{mapping_name}{RESET}' not loaded, loading...", {"mapping_name": mapping_name})
            db_mapping = self.__load_db_mapping(mapping_name)
            if db_mapping:
                self.__add_db_mapping(mapping_name.upper(), db_mapping)
            else:
                self.log(2, "Failed to load mapping '{CYAN}{db_mapping}{RESET}', returning None", {"db_mapping": mapping_name.upper()})
                return None
            self.log(2, "Returning pointer to mapping '{CYAN}{db_mapping}{RESET}' to '{MAGENTA}{caller}{RESET}'", {"db_mapping": mapping_name.upper(), "caller": caller})
            return self.__db_mappings[mapping_name.upper()]

    def request_library(self, libtype, libname):
        """
        Looking into ``self.__libraries`` and return a pointer to library, if
        library was previously initialized. Otherwise it will try to load it,
        place in ``self.__libraries`` and return a pointer to just initialized
        library.

        @param libtype Subdirectory of "lib" directory where library is placed.
        @param libname Library file name without ".py".
        @retval pointer Pointer to initialized library.
        """
        full_libname = "{0}.{1}".format(libtype, libname)
        caller = sys._getframe(1).f_locals["self"].__class__.__name__
        self.log(2, "Trying to obtain library '{CYAN}{full_libname}{RESET}' for '{MAGENTA}{caller}{RESET}'", {"full_libname": full_libname, "caller": caller})
        if full_libname.upper() in self.__libraries.keys():
            self.log(2, "Already loaded, returning pointer to library '{CYAN}{full_libname}{RESET}' to '{MAGENTA}{caller}{RESET}'", {"full_libname": full_libname, "caller": caller})
            return self.__libraries[full_libname.upper()]
        else:
            self.log(2, "Library '{CYAN}{full_libname}{RESET}' not found.", {"full_libname": full_libname})
            library = self.__load_library(full_libname)
            if library:
                self.__add_library(full_libname.upper(), library)
            else:
                self.log(2, "Failed to load library '{CYAN}{full_libname}{RESET}', returning None", {"full_libname": full_libname})
                return None
            self.log(2, "Returning pointer to library '{CYAN}{full_libname}{RESET}' to '{MAGENTA}{caller}{RESET}'", {"full_libname": full_libname, "caller": caller})
            return self.__libraries[full_libname.upper()]

    def request_plugin(self, plugin_name):
        """
        Loads plugins that related to current worker.

        @param plugin_name Name of plugin to load.
        @retval pointer Pointer to initialized plugin.
        """
        caller = sys._getframe(1).f_locals["self"].__class__.__name__
        if plugin_name.upper() in self.__plugins:
            self.log(2, "Already loaded, returning pointer to plugin '{CYAN}{plugin}{RESET}' to '{MAGENTA}{caller}{RESET}'", {"plugin": plugin_name.upper(), "caller": caller})
            #self.__plugin_requesters.pop()
            return self.__plugins[plugin_name.upper()]
        else:
            self.log(1, "Plugin '{MAGENTA}{plugin_name}{RESET}' not loaded, loading...", {"plugin_name": plugin_name})
            plugin = self.__load_plugin(plugin_name)
            if plugin:
                self.__add_plugin(plugin_name.upper(), plugin)
            else:
                self.log(2, "Failed to load plugin '{CYAN}{plugin}{RESET}', returning None", {"plugin": plugin_name.upper()})
                #self.__plugin_requesters.pop()
                return None
            self.log(2, "Returning pointer to plugin '{CYAN}{plugin}{RESET}' to '{MAGENTA}{caller}{RESET}'", {"plugin": plugin_name.upper(), "caller": caller})
            return self.__plugins[plugin_name.upper()]

    def request_ui(self, ui_filepath, instance):
        """
        Loads requested user interface object and return it to caller.
        """
        caller = sys._getframe(1).f_locals["self"].__class__.__name__
        self.log(1, "Trying to load interface '{CYAN}{interface}{RESET}' for '{MAGENTA}{caller}{RESET}'...", {"interface": ui_filepath, "caller": caller})

        # Make sure that we will have valid path separator on every OS.
        splitted = 0
        # For *NIX.
        if "/" in ui_filepath:
            ui_filepath = ui_filepath.split("/")
            splitted = 1

        # For Windows.
        if "\\" in ui_filepath:
            ui_filepath = ui_filepath.split("\\")
            splitted = 1

        # Re-generate string for UI file path if it was previously
        # splitted into list.
        if splitted:
            ui_filepath = os.path.join(*ui_filepath)

        # Add ".ui" to file path.
        ui_filepath += ".ui"

        # Generate path to UI.
        ui_path = os.path.join(self.__regius_path, ui_filepath)
        if not os.path.exists(ui_path):
            ui_path = os.path.join(self.__script_path, ui_filepath)

        self.log(2, "Regenerated file path for current OS: {filepath}", {"filepath": ui_filepath})

        if not ui_filepath in self.__uis:
            self.log(1, "UI {filepath} not loaded, loading it now...", {"filepath": ui_filepath})
            # Load UI.
            # For those who will ask me about this import - yes, it is
            # required for proper CLI-GUI separation.
            # And no, I saw no memory footprint increasing while doing
            # this. And yes, this is not PEP8.
            from PyQt5 import uic
            try:
                ui = uic.loadUi(ui_path, instance)
            except FileNotFoundError:
                self.log(2, "{RED}FileNotFoundError{RESET}")
                return None

            # Assing UI instance to self.__uis element, so we could request
            # a pointer to it later in other parts of program.
            self.__uis[ui_filepath] = ui
        else:
            self.log(1, "UI '{CYAN}{filepath}{RESET} already loaded, returning a pointer to '{MAGENTA}{caller}{RESET}'...", {"filepath": ui_filepath, "caller": caller})
            ui = self.__uis[ui_filepath]

        # Return an instance.
        return ui

    def shutdown(self):
        """
        Executes shutdown actions on every library and plugin.
        """
        self.log(0, "Executing shutdown sequence for plugins...")
        for item in self.__plugins:
            self.log(1, "Executing shutdown actions for plugin '{CYAN}{plugin}{RESET}'...", {"plugin": item})
            self.__plugins[item].on_shutdown()

        self.log(0, "Shutting down libraries...")
        for item in self.__libraries:
            # Completely pass main form :)
            if item == "MAIN.MAIN" or item == "MAIN.GUI" or item == "MAIN.CLI":
                continue

            # Execute shutdown actions for everything except logger.
            # It should be shutted down in very last.
            if not item == "COMMON_LIBS.LOGGER":
                self.log(1, "Executing shutdown actions for library '{CYAN}{library}{RESET}'...", {"library": item})
                self.__libraries[item].on_shutdown()

        # Logger should be shutted down at last.
        self.__libraries["COMMON_LIBS.LOGGER"].on_shutdown()

    def __add_db_mapping(self, name, pointer):
        """
        Adds database mapping to dictionary with loaded database mappings.

        @param name Name of database mapping.
        @param pointer Pointer to database mapping.
        """
        self.log(2, "Added mapping '{CYAN}{name}{RESET}' to database mappings dict", {"name": name})
        self.__db_mappings[name] = pointer

    def __add_library(self, name, pointer):
        """
        Adds library to dictionary with initialized libraries.

        @param name Name of library.
        @param pointer Pointer to library.
        """
        self.log(2, "Added library '{CYAN}{name}{RESET}' to libraries dict", {"name": name})
        self.__libraries[name] = pointer

    def __add_plugin(self, name, pointer):
        """
        Adds plugin to dictionary with initialized plugins.

        @param name Name of plugin.
        @param pointer Pointer to plugin.
        """
        self.log(2, "Added plugin '{CYAN}{name}{RESET}' to plugins dict", {"name": name})
        self.__plugins[name] = pointer

    def __load(self, type, item):
        """
        Loads a library or plugin, and returns pointer to ``self.request_plugin``
        or ``self.request_library``.

        Class's name should be:

        * Capitalized.
        * Be exactly like file name.

        For example, if you want to load "remote_config" database
        mapping, then file should be named ``remote_config.py`` and
        class which will be loaded, should be named ``Remote_config``.

        After successful importing class will be instantiated, and
        some initialization methods will be executed:

        * For libraries: init_library_int() and init_library().
        * For plugins: init_library_int() and init_plugin().
        * For database mappings: nothing.

        @param type Type of loadable object. Can be "db_mapping",
        "library" or "plugin".
        @param item Loadable object file name without ".py".
        @retval pointer Pointer to loaded object.
        @retval None If loading failed.
        """
        try:
            if type == "db_mapping":
                self.log(2, "Importing '{BLUE}{item}{RESET}'...", {"item": item})
                __import__("lib.database_mappings.{0}".format(item))
                exec("self.module = sys.modules['lib.database_mappings.{0}']".format(item.lower()))
                exec("self.module = self.module.{0}".format(item.capitalize()))
                self.log(2, "Imported item: {item}, type {type}", {"item": self.module, "type": type})
            elif type == "library":
                self.log(2, "Importing '{BLUE}{item}{RESET}'...", {"item": item})
                __import__("lib.{0}".format(item))
                exec("self.module = sys.modules['lib.{0}']".format(item.lower()))
                exec("self.module = self.module.{0}()".format(item.split(".")[1].capitalize()))
                self.log(2, "Imported item: {item}, type {type}", {"item": self.module, "type": type})
            elif type == "plugin":
                __import__("plugins.{0}.{0}".format(item))
                exec("self.module = sys.modules['plugins.{0}.{0}']".format(item.lower()))
                exec("self.module = self.module.{0}_Plugin()".format(item.capitalize()))
        except AttributeError as e:
            self.log(0, "{RED}Failed to initialize {type} '{CYAN}{item}{RED}' (AttributeError): {RESET}{error}", {"type": type, "item": item, "error": e})
            return None
        except ImportError as e:
            self.log(0, "{RED}Failed to load {type} '{CYAN}{item}{RED}' (ImportError): {RESET}{error}", {"type": type, "item": item, "error": e})
            return None
        except KeyError as e:
            self.log(0, "{RED}Failed to initialize {type} '{CYAN}{item}{RED}' (KeyError): {RESET}{type} module isn't found in loaded modules dictionary.", {"type": type, "item": item, "error": e})
            self.log(0, "{RED}Bad {type} name?{RESET}", {"type": type})
            return None

        # Use local variable for next actions, to get rid of possible
        # overwrite by loading dependencies or something like that.
        module = self.module

        if type == "db_mapping":
            # Nothing to initialize here.
            pass
        elif type == "library":
            # For libraries we just init them with function from
            # Library metaclass.
            module.init_library_int(self)
            module.init_library()
        elif type == "plugin":
            # For plugin we initializing:
            #   * Library metaclass functions and variables
            #   * Plugin metaclass functions and variables
            #   * Plugin itself
            module.init_library_int(self)
            module.init_plugin()
            try:
                module.initialize()
            except AttributeError as e:
                self.log(0, "{RED}Failed to initialize plugin '{CYAN}{item}{RED}' (AttributeError): {RESET}{error}", {"item": item, "error": e})
        else:
            self.log(0, "{RED}Requested unknown type of loadable object: {BLUE}{type}{RESET}", {"type": type})

        return module

    def __load_db_mapping(self, db_mapping):
        """
        Loads and initializes database table mapping by calling
        self.__load() with required parameters.

        @param db_mapping Name of database mapping's file without ".py".
        @retval pointer Pointer to loaded database mapping.
        """
        self.log(0, "Loading mapping '{CYAN}{db_mapping}{RESET}'...", {"db_mapping": db_mapping})
        db_mapping = self.__load("db_mapping", db_mapping)
        return db_mapping

    def __load_library(self, full_libname):
        """
        Loads and initializes library. Nuff said.

        This method should be separated from loading plugins due
        to requirement of logging - we should know what we load
        and for whom.
        """
        self.log(0, "Loading library '{CYAN}{full_libname}{RESET}'...", {"full_libname": full_libname})
        library = self.__load("library", full_libname)
        return library

    def __load_plugin(self, plugin_name):
        """
        Loads and initializes plugin. Nuff said.

        This method should be separated from loading libraries due
        to requirement of logging - we should know what we load
        and for whom.
        """
        self.log(0, "Loading plugin '{MAGENTA}{plugin_name}{RESET}'...", {"plugin_name": plugin_name})
        plugin = self.__load("plugin", plugin_name)
        return plugin
