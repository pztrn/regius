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

# Configuration library.

import os
import sys

from lib.common_libs import common
from lib.common_libs.library import Library

# Configuration classes.
from lib.common_libs.config_types.ini import INI
from lib.common_libs.config_types.json import JSON

class Config(Library):
    """
    This class is responsible for all configuration actions, like reading
    configuration from files or database, put it here, and so on.

    Also, this class is responsible for temporary configuration things,
    so any temporary variables should be set like:
    self.config.set_temp_value(k, v).
    """

    _info = {
        "name"          : "Configuration library",
        "shortname"     : "config",
        "description"   : "This library responsible for all configuration actions."
    }

    def __init__(self):
        Library.__init__(self)

        # Temporary configuration settings
        self.__temp_settings = {}
        # Persistent configuration.
        # Can be obtained from files, or database.
        self.__config = {}

    def get_available_backends(self):
        """
        Returns a list of available backends.
        """
        return self.__available_backends

    def get_keys_for_group(self, type, group):
        """
        Returns all keys for specified group.
        """
        if type == "qsettings":
            return self.__qconfig.get_keys_for_group(group)
        elif type == "json":
            return self.__json.get_keys_for_group(group)

    def get_temp_value(self, key):
        """
        Returns item from temporary configuration if it exists.
        Otherwise return None.
        """
        if key in self.__temp_settings:
            caller_class = sys._getframe(1).f_locals["self"].__class__.__name__
            self.log(2, "Returning value for temporary variable to '{CYAN}{caller}{RESET}': '{key}' = '{value}'", {"caller": caller_class, "key": key, "value": self.__temp_settings[key]})
            return self.__temp_settings[key]

    def get_value(self, type, group, key):
        """
        Returns a value for 'key' in 'group' from configuration
        storage 'type'.
        """
        if type == "qsettings":
            if self.__qconfig:
                return self.__qconfig.get_value(group, key)
        elif type == "json":
            return self.__json.get_value(group, key)
        elif type == "ini":
            return self.__ini.get_value(group, key)
        elif type == "all":
            ini = self.__ini.get_value(group, key)
            json = self.__json.get_value(group, key)
            if self.__qconfig:
                qsettings = self.__qconfig.get_value(group, key)

            # Our preference - QConfig, then JSON, then INI. Only latter
            # will be returned.
            if ini:
                return ini

            if json:
                return json

            if self.__qconfig:
                if qsettings:
                    return qsettings

    def init_library(self):
        """
        Library initialization :).

        This method will open all possible configuration types, for now
        it's QSettings only (lib.common_libs.config_types.qconfig).

        Also it will obtain all data from common.TEMP_SETTINGS to it's own
        dictionary (self.__temp_settings) for get_temp_value() and
        set_temp_value() methods work.
        """
        if not os.path.exists(os.path.expanduser(os.path.join("~/.config/regius"))):
            self.log(2, "Configuration directory does not exist, creating...")
            os.makedirs(os.path.expanduser(os.path.join("~/.config/regius")))

        if common.TEMP_SETTINGS["UI"] == "gui":
            from lib.common_libs.config_types.qconfig import QConfig
            self.__qconfig = QConfig(self.log, self.loader)
        else:
            self.__qconfig = None

        self.__json = JSON(self.log, self.loader)
        self.__ini = INI(self.log, self.loader)

        # Update self.__temp_settings with values from common.TEMP_SETTINGS.
        self.__temp_settings.update(common.TEMP_SETTINGS)

        # Someday it will be dynamic.
        self.__available_backends = ["JSON", "INI", "QConfig"]

    def load_configuration_from_files(self, preseed):
        """
        Load configuration from preseed file.

        This preseed file is optional. If no preseed file will be found:
        adding new database server dialog will appear.
        """
        if preseed["preseed"]["ui"] == "gui":
            self.__qconfig.load_configuration(preseed["preseed"]["app_name"])
        else:
            self.log(0, "Skipping QConfig initialization.")

        # Set configuration path.
        cfg_path = None
        if "config" in preseed["paths"] and len(preseed["paths"]["config"]) != 0:
            cfg_path = preseed["paths"]["config"]

        # If configuration path doesn't start with "/" - use relative
        # path.
        if cfg_path and not cfg_path.startswith("/"):
            cfg_path = os.path.join(sys.path[0], cfg_path)

        self.log(0, "Configuration path: {cfg_path}", {"cfg_path": cfg_path})

        self.__ini.load_configuration(preseed["preseed"]["app_name"], cfg_path)
        self.__json.load_configuration(preseed["preseed"]["app_name"], cfg_path)
        self.__temp_settings.update(preseed)

    def parse_env(self):
        """
        This method parses environment variables.
        """
        if not "env" in self.__temp_settings:
            self.__temp_settings["env"] = {}

        for env_key in os.environ.keys():
            self.__temp_settings["env"][env_key] = os.environ[env_key]

    def save_configuration(self):
        """
        Force configuration to be saved.
        """
        self.log(0, "Saving configuration...")
        result = self.__qconfig.save_configuration()
        if result:
            self.log(0, "{RED}ERROR:{RESET} failed to save Qt-related configuration!")

        result = self.__json.save_configuration()
        if result:
            self.log(0, "{RED}ERROR:{RESET} failed to save JSON configuration!")

    def set_temp_value(self, key, value):
        """
        Sets (or overwrites) temporary variable.
        """
        self.log(1, "Setting temporary variable: '{key}' => '{value}'", {"key": key, "value": value})
        self.__temp_settings[key] = value

    def set_value(self, type, group, key, value):
        """
        Sets 'value' for 'key' in 'group' from configuration storage
        'type'.
        """
        if type == "qsettings":
            self.__qconfig.set_value(group, key, value)
        elif type == "json":
            self.__json.set_value(group, key, value)
