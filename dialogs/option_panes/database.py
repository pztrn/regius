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

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTreeWidgetItem

from lib.ui.option_pane import OptionPane

class DatabasePane(OptionPane):
    """
    """

    _info = {
        "name"          : "Database option pane",
        "shortname"     : "database_pane",
        "description"   : "This module responsible for all actions with database option pane."
    }

    def __init__(self):
        OptionPane.__init__(self)

        # Internal configuration. Used for filling elements in
        # connection list, storing configuration on changes and
        # pushing configuration back to configuration storage.
        self.__config = {}

    def add_connection(self):
        """
        Adds database connection.
        """
        item = QTreeWidgetItem(self.root_item)
        item.setFlags(Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable)
        item.setText(0, "Enter connection name")
        self.ui.connections_list.editItem(item)

    def delete_connection(self):
        """
        """
        conn_item = self.ui.connections_list.selectedItems()[0]
        conn_name = conn_item.text(0)
        self.log(1, "Deleting connection '{conn_name}'...", {"conn_name": conn_name})
        if conn_name in self.__config:
            del self.__config[conn_name]
        else:
            self.log(1, "Connection '{conn_name}' wasn't saved to configuration storage yet, just removing item from connections list widget", {"conn_name": conn_name})

        idx = self.root_item.indexOfChild(conn_item)
        self.root_item.takeChild(idx)

    def init_widget(self):
        """
        Widget initialization method, called right after instantiation.
        """
        self.ui = self.loader.request_ui(os.path.join("ui", "option_panes", "database"), None)

        # Root item for connections list.
        self.root_item = self.ui.connections_list.invisibleRootItem()

        # This flag indicates that we haven't connect database type
        # combobox.
        self.config.set_temp_value("config/database/dbtype_combobox_connected", False)

        self.__connect_signals()
        self.__get_configuration()

    def on_close(self):
        """
        This method executes on options window close.
        """
        self.log(1, "Saving database options...")
        self.__save_configuration()

    def rename_connection(self):
        """
        """
        conn_item = self.ui.connections_list.selectedItems()[0]
        self.log(1, "Renaming connection '{conn_name}'...", {"conn_name": conn_item.text(0)})
        self.ui.connections_list.editItem(conn_item)

    def __connect_signals(self):
        """
        Connects signals to slots.
        """
        self.log(1, "Connecting signals...")

        # Connections list itself.
        self.ui.connections_list.currentItemChanged.connect(self.__connection_selection_changed)

        #self.ui.db_type.currentIndexChanged.connect(self.__text_edited)

        # Add, edit, remove buttons.
        self.ui.add_connection.clicked.connect(self.add_connection)
        self.ui.delete_connection.clicked.connect(self.delete_connection)
        self.ui.rename_connection.clicked.connect(self.rename_connection)

        # Text editing.
        self.ui.host.textEdited.connect(self.__text_edited)
        self.ui.port.textEdited.connect(self.__text_edited)
        self.ui.username.textEdited.connect(self.__text_edited)
        self.ui.password.textEdited.connect(self.__text_edited)
        self.ui.db_name.textEdited.connect(self.__text_edited)

    def __get_configuration(self):
        """
        This method retrieving configuration and set UI elements.
        """
        keys = self.config.get_keys_for_group("qsettings", "database")

        if keys:
            for item in keys:
                conn_name = item.split("_")[0]
                db_item = item.split("_")[1]

                if not conn_name in self.__config:
                    self.__config[conn_name] = {}

                self.__config[conn_name][db_item] = self.config.get_value("qsettings", "database", item)

        for item in self.__config.keys():
            conn_item = QTreeWidgetItem(self.root_item)
            conn_item.setText(0, item)
            conn_item.setFlags(Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable)

    def __save_configuration(self):
        """
        This method obtaining data from widget and set configuration
        accordingly.
        """
        self.log(1, "Saving configuration...")
        for item in self.__config:
            for key in self.__config[item]:
                self.config.set_value("qsettings", "database", item + "_" + key, self.__config[item][key])

    def __connection_selection_changed(self, current):
        """
        Sets input fields options after selecting item in connections
        list.
        """
        self.log(1, "Enabling input items on widget...")
        self.ui.db_type.setEnabled(True)
        self.ui.host.setEnabled(True)
        self.ui.port.setEnabled(True)
        self.ui.username.setEnabled(True)
        self.ui.password.setEnabled(True)
        self.ui.db_name.setEnabled(True)

        current_item = current.text(0)
        self.log(1, "Putting values in input fields for '{conn_name}'...", {"conn_name": current_item})
        if not current_item in self.__config:
            self.log(1, "Nothing to put in input fields for item '{conn_name}'", {"conn_name": current_item})
        else:
            self.ui.db_type.setCurrentIndex(int(self.__config[current_item]["type"]))
            self.ui.host.setText(self.__config[current_item]["host"])
            self.ui.port.setText(self.__config[current_item]["port"])
            self.ui.username.setText(self.__config[current_item]["user"])
            self.ui.password.setText(self.__config[current_item]["pass"])
            self.ui.db_name.setText(self.__config[current_item]["dbname"])

        # Connect database type combobox only on first widgets filling.
        if not self.config.get_temp_value("config/database/dbtype_combobox_connected"):
            self.ui.db_type.currentIndexChanged.connect(self.__text_edited)

    def __text_edited(self, text):
        """
        Saves new text from input field into configuration.
        """
        # Get connection name.
        conn_item = self.ui.connections_list.selectedItems()
        conn_name = conn_item[0].text(0)

        self.log(2, "Selection changed, updating configuration parameters for connection '{conn_name}'...", {"conn_name": conn_name})

        # Save into internal configuration dictionary.
        if not conn_name in self.__config:
            self.__config[conn_name] = {}

        self.__config[conn_name]["type"] = self.ui.db_type.currentIndex()
        self.__config[conn_name]["host"] = self.ui.host.text()
        self.__config[conn_name]["port"] = self.ui.port.text()
        self.__config[conn_name]["user"] = self.ui.username.text()
        self.__config[conn_name]["pass"] = self.ui.password.text()
        self.__config[conn_name]["dbname"] = self.ui.db_name.text()
