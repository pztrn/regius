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

import configparser
import os
import sys

from lib.common_libs import common

class INI:
    """
    This library responsible for working with configuration in INI
    format.
    """

    def __init__(self, logger, loader):
        self.loader = loader
        self.log = logger
        self.__config = {}

    def get_keys_for_group(self, group):
        """
        Returns all keys for specified group.
        """
        self.log(0, "INI.get_keys_for_group() not implemented!")

    def get_value(self, group, key):
        """
        Returns a value for key in group. Easy-peasy! :)
        """
        self.log(0, "INI.get_value() not implemented!")

    def load_configuration(self, app_name, config_path = None):
        """
        Reads configuration from JSON file into dict.
        """
        self.__app_name = app_name
        if not config_path:
            self.__cfg_dir = os.path.expanduser(os.path.join("~/", ".config/", "regius", self.__app_name))
        else:
            self.__cfg_dir = os.path.expanduser(os.path.join(config_path))
        self.__main_cfg = os.path.join(self.__cfg_dir, "config.ini")

        self.log(0, "Reading INI configuration...")

        config = configparser.ConfigParser()
        cfg = config.read(self.__main_cfg)

        self.log(2, "Loading config.ini...")
        for section in config.keys():
            if not section in self.__config:
                self.__config[section] = {
                    "__file_path": self.__main_cfg
                }

            for item in config[section]:
                self.__config[section][item] = config[section][item]

        self.log(2, "Loading configuration from sorted list of files...")
        self.log(2, "Loading configuration from user's home directory...")
        self.__load_from_directory(self.__cfg_dir)

    def save_configuration(self):
        """
        Saves configuration to QSettings instance.
        """
        self.log(0, "INI.save_configuration() not implemented!")

    def set_value(self, group, key, value):
        """
        Sets a value for key in group. Easy-peasy! :)
        """
        self.log(0, "INI.set_value() not implemented!")

    def __load_from_directory(self, directory):
        """
        """
        cfglist = os.listdir(directory)
        cfglist = sorted(cfglist)
        for config in cfglist:
            cfgpath = os.path.join(directory, config)
            if config.endswith("ini"):
                config = configparser.ConfigParser()
                cfg = config.read(cfgpath)

                for section in config.keys():
                    if not section in self.__config:
                        self.__config[section] = {
                            "__file_path": cfgpath
                        }
                    else:
                        self.__config[section]["__file_path"] = cfgpath

                    for item in config[section]:
                        self.__config[section][item] = config[section][item]
