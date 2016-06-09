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

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QMessageBox, QTreeWidgetItem

from lib.ui.dialog import Dialog
from lib.ui.messagebox import MessageBox

class OptionsDialog(Dialog):
    """
    This class is responsible for options window.

    It'll use two types of code and ui files:
        * General - represents basic program parameters, that doesn't
          belongs to plugins
        * Plugins - represents all features that implemented by
          plugins.
    """

    _info = {
        "name"          : "Options dialog",
        "shortname"     : "options_dialog",
        "description"   : "This module responsible for all common options dialog actions."
    }

    def __init__(self):
        Dialog.__init__(self)

        # Dictionary with pointers to option panes UIs.
        self.__option_panes_uis = {}
        # Dictionary with pointers to option panes classes instances.
        self.__option_panes_code = {}

        # Panes that failed to load.
        self.__failed_to_load = []

        # Currently activated pane.
        self.__current = {}

    def closeEvent(self, event):
        """
        Executes on dialog close.
        """
        # Saving size and position.
        self.on_closeEvent()
        if self.config.get_temp_value("ui/options_dialog/configuration_already_saved"):
            self.log(2, "Configuration was already saved, closing options window")
            event.accept()
        else:
            if self.config.get_temp_value("ui/options_dialog/close_without_saving"):
                self.log(1, "Closing options window without saving changes")
                event.accept()
            else:
                self.log(1, "Closing options window with saving changes")
                self.__save_configuration()
                event.accept()

    def load_panes(self):
        """
        Loads option panes code. This method is called right after tree widget
        preparation, like adding root items for general and plugin-related
        option panes.

        Just to be sure that these root items exists this method will try to
        acquire pointer to them. If it fails - it will stop all futher
        actions, close options window and show error box.

        This is a proxy for two internal methods - __load_general_panes_code()
        and __load_plugins_panes_code(). First one loads panes for general
        option panes, which have its UIs in ui/option_panes/ directory.
        Second one loads code for plugin panes, which should be in
        plugin_root/option_pane.py file.

        Every option pane code file should be subclassed from
        lib.ui.option_pane.OptionPane class, which have everything every
        option pane might need.
        """
        self.log(1, "Starting option panes code initialization...")
        self.__load_general_panes()

        self.__load_plugins_panes()

    def show_dialog(self, pane_name = None):
        """
        Shows options dialog window.

        This method should be called outside of this class, e.g. when
        instantiated.

        This method will create 2 root items for sidebar to which all
        panes will belong, depends on it's type (general or plugins).
        After creating them, load_panes() will be called, which is
        a proxy for __load_general_panes() and __load_plugins_panes()
        methods, which will actually load UIs and panes code.

        Afterall, it will connect some common UI elements (like OK or
        Cancel button, options tree, etc.) to it's methods.

        This method also have an ability to show exact pane name.
        Just pass 'pane_name' to it.
        """
        self.__loaded_plugins = self.loader.get_loaded_plugins()
        self.log(1, "Loaded plugins to poll for UIs:")
        self.log(1, list(self.__loaded_plugins.keys()))

        # Load options window UI.
        self.ui = self.loader.request_ui("ui/options_window", self)
        # Root items.
        self.root_item = self.ui.tree.invisibleRootItem()
        # Set root item for general option panes.
        self.general_root_item = QTreeWidgetItem(["General"])
        self.general_root_item.setFlags(Qt.ItemIsEnabled)
        # Set root item for plugins option panes.
        self.plugins_root_item = QTreeWidgetItem(["Plugins"])
        self.plugins_root_item.setFlags(Qt.ItemIsEnabled)
        self.root_item.addChild(self.general_root_item)
        self.root_item.addChild(self.plugins_root_item)
        # Set all root items to show its childs.
        self.ui.tree.expandAll()

        if not self.config.get_temp_value("ui/options_dialog/initialized"):
            self.load_panes()
            self.config.set_temp_value("ui/options_dialog/initialized", True)

        self.__connect_common_ui_signals()

        # If pane name was passed - show it.
        if pane_name:
            item = self.ui.tree.findItems(pane_name, Qt.MatchExactly | Qt.MatchRecursive, 0)[0]
            self.ui.tree.setCurrentItem(item)

        self.on_dialog_open()
        self.ui.show()

    def __close_without_saving(self):
        """
        This method sets special flag for closing window without pushing
        any data to configuration.

        Cancel button is connected here.
        """
        self.config.set_temp_value("ui/options_dialog/close_without_saving", True)
        self.ui.close()

    def __connect_common_ui_signals(self):
        """
        This method will connect common UI elements (like OK and Cancel buttons)
        do required methods.
        """
        self.log(1, "Connecting UI elements to methods...")
        self.log(2, "Connecting Cancel button...")
        self.ui.cancel_button.clicked.connect(self.__close_without_saving)
        self.ui.ok_button.clicked.connect(self.__save_configuration)
        self.log(2, "Connecting options tree item selection changed slot...")
        self.ui.tree.itemSelectionChanged.connect(self.__show_widget)

    def __load_code(self, type, name):
        """
        Universal pane code loader.

        Reason why it not included in lib.loader.Loader() is simple:
        we might want different initialization method in future.
        Maybe it will be merged some time.
        """
        try:
            if type == "general":
                __import__("dialogs.option_panes.{0}".format(name.lower()))
                exec("self.module = sys.modules['dialogs.option_panes.{0}']".format(name.lower()))
            elif type == "plugin":
                __import__("plugins.{0}.options".format(name.lower()))
                exec("self.module = sys.modules['plugins.{0}.options']".format(name.lower()))
            exec("self.module = self.module.{0}Pane()".format(name.capitalize()))
        except AttributeError as e:
            self.log(0, "{RED}Failed to initialize class for '{CYAN}{name}{RED}' (AttributeError): {RESET}{error}", {"name": name, "error": e})
            if not name in self.__failed_to_load:
                self.__failed_to_load.append(name)
        except ImportError as e:
            self.log(0, "{RED}Failed to load code for '{CYAN}{name}{RED}' (ImportError): {RESET}{error}", {"name": name, "error": e})
            if not name in self.__failed_to_load:
                self.__failed_to_load.append(name)
        except KeyError as e:
            self.log(0, "{RED}Failed to initialize code for '{CYAN}{name}{RED}' (KeyError): {RESET}{type} module isn't found in loaded modules dictionary.", {"name": name, "error": e})
            self.log(0, "{RED}Bad code file name?{RESET}")
            if not name in self.__failed_to_load:
                self.__failed_to_load.append(name)

        try:
            self.module.init_widget_int(self.loader)
            self.module.init_widget()
        except AttributeError as e:
            self.log(0, "{RED}Failed to initialize code for '{CYAN}{name}{RED}' (AttributeError): {RESET}{error}", {"name": name, "error": e})
            if not name in self.__failed_to_load:
                self.__failed_to_load.append(name)

        if not name in self.__failed_to_load:
            self.log(1, "Option pane '{CYAN}{pane_name}{RESET}' successfully loaded", {"pane_name": name})

            # Plugins panes SHOULD NOT override general ones.
            if type == "plugin":
                if not name in self.__option_panes_code:
                    self.__option_panes_code[name] = self.module
                    del self.module
                else:
                    box = MessageBox("error", "Failed to load option pane", "Plugin option pane '{0}' tries to overwrite general option pane!.".format(plugin_name))
                    box.show()
            else:
                self.__option_panes_code[name] = self.module
                del self.module

    def __load_general_panes(self):
        """
        This method will load general option panes.

        Pane code file should be located at dialog/option_panes
        directory and have exact name as it should be added in
        tree widget in options window.

        Every code file should contain init_widget() method,
        which will be called right after instantiation of pane
        code class. This method will be called after init_widget_int()
        method, which reside in lib.ui.option_pane.OptionPane class and
        contains common initialization tasks.
        """
        # Obtain list of code and UI files.
        option_panes_code_path = os.path.join(self.config.get_temp_value("REGIUS_PATH"), "dialogs", "option_panes")
        option_panes_uis_path = os.path.join(self.config.get_temp_value("REGIUS_PATH"), "ui", "option_panes")
        code_files = os.listdir(option_panes_code_path)
        ui_files = os.listdir(option_panes_uis_path)
        to_load = []

        # Check if code file have approriate UI file to use with.
        for file in code_files:
            pane_name = file.split(".")[0]
            self.log(2, "Checking for existing UI for '{CYAN}{code_filename}{RESET}'...", {"code_filename": file})
            if os.path.exists(os.path.join(option_panes_uis_path, pane_name + ".ui")):
                self.log(2, "Found UI file for code file '{YELLOW}{code_filename}{RESET}', adding to list for loading...", {"code_filename": file})
                to_load.append(pane_name)
            else:
                self.log(2, "UI for '{CYAN}{code_filename}{RESET}' not exist, skipping load", {"code_filename": file})

        # Check if we will load anything.
        # If no - just return.
        if len(to_load) > 0:
            self.log(1, "Will load '{BLUE}{count}{RESET}' panes", {"count": len(to_load)})
        else:
            return None

        for item in to_load:
            self.log(1, "Loading pane '{CYAN}{pane_name}{RESET}'...", {"pane_name": item})
            self.log(2, "Trying to load UI for pane '{CYAN}{pane_name}{RESET}'...", {"pane_name": item})
            ui = self.loader.request_ui(os.path.join("ui", "option_panes", item), None)
            self.__option_panes_uis[item] = {
                "widget"    : ui,
                "index"     : self.ui.widget.count()
            }
            self.ui.widget.addWidget(ui)
            tree_item = QTreeWidgetItem(self.general_root_item)
            tree_item.setText(0, item.capitalize())

            self.log(2, "Trying to load code file for pane '{CYAN}{pane_name}{RESET}'...", {"pane_name": item})
            self.__load_code("general", item)

    def __load_plugins_panes(self):
        """
        This method will load plugins option panes.

        Pane code file should be located at dialog/option_panes
        directory and have exact name as it should be added in
        tree widget in options window.

        Every code file should contain init_widget() method,
        which will be called right after instantiation of pane
        code class. This method will be called after init_widget_int()
        method, which reside in lib.ui.option_pane.OptionPane class and
        contains common initialization tasks.        """
        self.log(1, "Loading plugins panes...")

        for plugin in self.__loaded_plugins:
            plugin = self.__loaded_plugins[plugin]
            plugin_name = plugin.__class__.__name__
            self.log(2, "Obtaining UI for plugin {plugin}...", {"plugin": plugin_name})
            ui = plugin.get_option_pane()
            if not ui:
                self.log(1, "{RED}Failed to load option pane for plugin '{CYAN}{plugin_name}{RESET}'", {"plugin_name": plugin_name})
                if not plugin.__class__._info["shortname"] in self.__failed_to_load:
                    self.__failed_to_load.append(plugin.__class__._info["shortname"])
                continue
            self.__option_panes_uis[ui["name"]] = ui
            self.__option_panes_uis[ui["name"]]["index"] = self.ui.widget.count()
            tree_item = QTreeWidgetItem(self.plugins_root_item)
            tree_item.setText(0, ui["name"].capitalize())
            self.ui.widget.addWidget(ui["widget"])

            self.log(2, "Trying to load code file for pane '{CYAN}{pane_name}{RESET}'...", {"pane_name": plugin_name})
            self.__load_code("plugin", plugin_name.split("_")[0])

    def __save_configuration(self):
        """
        This method will execute every pane's method on_close(), which
        should push configuration values to configuration.
        """
        self.log(0, "Saving configuration...")

        for item in self.__option_panes_code:
            self.log(1, "Executing on_close() method for '{CYAN}{pane_name}{RESET}'...", {"pane_name": item})
            self.__option_panes_code[item].on_close()

        self.config.set_temp_value("ui/options_dialog/configuration_already_saved", True)
        self.ui.close()
        self.log(2, "Asking Config() to save configuration on disk...")
        self.config.save_configuration()

    def __show_widget(self):
        """
        This method is responsible for showing widget depending on
        selected pane in options tree.
        """
        parent = False
        try:
            selection = self.ui.tree.selectedItems()[0]
        except IndexError:
            # Happens when you select parent item. Should be
            # safe to pass.
            parent = True

        if not parent:
            try:
                self.__current = self.__option_panes_uis[selection.text(0).lower()]

                # Try to set current widget.
                self.log(1, "Enabling widget '{form}'", {"form": selection.text(0)})
                self.ui.widget.setCurrentIndex(self.__current["index"])
            except KeyError as e:
                self.log(0, "{RED}ERROR{RESET}: failed to show options pane '{YELLOW}{pane}{RESET}': {error}", {"pane": selection.text(0), "error": repr(e)})
                box = MessageBox("error", "Failed to load option pane", "Failed to obtain pointer to pane '{0}' in loaded option panes.".format(selection.text(0)))
                box.show()
