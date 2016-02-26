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

import json
import os

from lib.common_libs import common

class JSON:
    """
    This library responsible for working with configuration in JSON
    format.
    """

    def __init__(self, logger, loader):
        self.loader = loader
        self.log = logger
        self.__config = {}
        self.__main_cfg = os.path.expanduser("~/.config/tovarouchet/config.json")

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
        Reads configuration from JSON file into dict.
        """
        self.log(0, "Reading JSON configuration...")
        # Read main config.
        if os.path.exists(self.__main_cfg):
            self.log(2, "Main configuration file found, loading it...")
            self.__config = json.loads(open(self.__main_cfg, "r").read())
        # Read preseed file
        preseed_cfg = os.path.join(common.TEMP_SETTINGS["SCRIPT_PATH"], "config.json")
        if os.path.exists(preseed_cfg):
            self.log(2, "Preseed configuration file found, loading it...")
            self.__config.update(json.loads(open(preseed_cfg, "r").read()))

    def save_configuration(self):
        """
        Saves configuration to QSettings instance.
        """
        self.log(0, "Saving JSON configuration...")

        # Do not save preseed data if present, it is unchangeable.
        if "preseed" in self.__config:
            del self.__config["preseed"]

        config_data = json.dumps(self.__config, indent = 4)
        with open(self.__main_cfg, "w") as cfg:
            cfg.write(config_data)
            cfg.flush()

    def set_value(self, group, key, value):
        """
        Sets a value for key in group. Easy-peasy! :)
        """
        if not group in self.__config:
            self.__config[group] = {}

        self.__config[group][key] = value


