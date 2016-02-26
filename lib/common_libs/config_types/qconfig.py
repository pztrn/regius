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

from PyQt5.QtCore import QSettings

class QConfig:
    """
    This lbrary responsible for reading and writing Qt-related
    configuration (like window positions, sizes, etc.).

    On reading it will return a dictionary that very similar
    a configparser-produced one, so it will be 2-level
    dictionary with data.

    On writing it will morph data from 2-level dictionary into
    QConfig things.

    This class also provides methods for reading and writing
    data to 2-level dictionary.
    """

    def __init__(self, logger, loader):
        self.loader = loader
        self.log = logger
        self.__config = {}

    def get_keys_for_group(self, group):
        """
        Returns all keys for specified group.
        """
        if group in self.__config:
            return self.__config[group].keys()

    def get_value(self, group, key):
        """
        Returns a value for key in group. Easy-peasy! :)
        """
        if not group in self.__config:
            self.log(0, "{RED}ERROR:{RESET} group '{MAGENTA}{group}{RESET}' not found in configuration! Returning None for '{BLUE}{key}{RESET}'...", {"group": group, "key": key})
            return None

        if not key in self.__config[group]:
            self.log(0, "{RED}ERROR:{RESET} key '{BLUE}{key}{RESET}' not found in group '{MAGENTA}{group}{RESET}'! Returning None...", {"key": key, "group": group})
            return None

        return self.__config[group][key]

    def load_configuration(self):
        """
        Reads configuration from QSettings file into 2-level dict.
        """
        self.log(0, "Reading Qt configuration...")
        self.qsettings = QSettings(os.path.join("tovarouchet", "qsettings"))

        self.log(1, "Reading main window configuration...")
        for item in self.qsettings.allKeys():
            group, item = item.split("/")
            if not group in self.__config:
                self.__config[group] = {}

            self.qsettings.beginGroup(group)

            self.__config[group][item] = self.qsettings.value(item)

            self.qsettings.endGroup()

    def save_configuration(self):
        """
        Saves configuration to QSettings instance.
        """
        self.log(0, "Saving Qt configuration...")

        for section in self.__config:
            if len(self.__config[section]) > 0:
                self.qsettings.beginGroup(section)
                for item in self.__config[section]:
                    self.qsettings.setValue(item, self.__config[section][item])

                self.qsettings.endGroup()

        # Save main window's size and position.
        self.log(2, "Saving main window's size and position...")
        ui = self.loader.request_ui("ui/main_window", None)
        self.qsettings.beginGroup("mainwindow")
        self.qsettings.setValue("size", ui.size())
        self.qsettings.setValue("position", ui.pos())
        self.qsettings.endGroup()
        self.qsettings.sync()

    def set_value(self, group, key, value):
        """
        Sets a value for key in group. Easy-peasy! :)
        """
        if not group in self.__config:
            self.__config[group] = {}

        self.__config[group][key] = value


