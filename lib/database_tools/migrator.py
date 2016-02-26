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

from alembic import command
from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.runtime.environment import EnvironmentContext
from alembic.script import ScriptDirectory
import os

from lib.common_libs.library import Library

class Migrator(Library):
    """
    This class responsible for executing database migrations,
    provided by framework and by plugins.
    """

    _info = {
        "name"          : "Migrator library",
        "shortname"     : "migrator",
        "description"   : "This library responsible for all database migration actions."
    }

    def __init__(self):
        Library.__init__(self)

    def init_library(self):
        """
        """
        self.log(0, "Initializing database migration tools...")
        self.__database = self.loader.request_library("common_libs", "database")

    def migrate(self):
        """
        Executes database migrations.
        """
        self.__migrate_core()
        self.__migrate_plugins()

    def __migrate_core(self):
        """
        Execute framework database migrations.
        """
        if os.path.exists(os.path.join(self.config.get_temp_value("SCRIPT_PATH"), "alembic.ini")) and os.path.exists(os.path.join(self.config.get_temp_value("SCRIPT_PATH"), "migrations")):
            self.log(0, "Executing core database migrations...")
            self.log(2, "Loading alembic configuration...")
            core_config = Config(os.path.join(self.config.get_temp_value("SCRIPT_PATH"), "alembic.ini"))
            core_config.set_main_option("script_location", os.path.join(self.config.get_temp_value("SCRIPT_PATH"), "migrations"))
            core_config.set_main_option("version_table_name", "db_version_for_core")
            core_config.set_main_option("sqlalchemy.url", self.config.get_temp_value("database/db_string"))

            self.log(2, "Running migrations...")
            conn = self.__database.get_database_connection()
            with conn.begin() as connection:
                command.upgrade(core_config, "head")

    def __migrate_plugins(self):
        """
        Executing plugins migrations.
        """
        conn = self.__database.get_database_connection()

        self.log(0, "Executing migrations for plugins...")

        self.log(2, "Getting list of available plugins...")
        plugins = os.listdir(os.path.join(self.config.get_temp_value("SCRIPT_PATH"), "plugins"))

        for plugin in plugins:
            if plugin.endswith("__") or plugin.endswith(".py") or plugin.endswith(".pyc") or plugin.endswith(".pyo"):
                self.log(0, "{RED}ERROR: unsupported type of plugin: {plugin_name}{RESET}", {"plugin_name": plugin})
                continue

            self.log(1, "Searching for migrations for plugin '{CYAN}{plugin_name}{RESET}'...", {"plugin_name": plugin})
            plugin_path = os.path.join(self.config.get_temp_value("SCRIPT_PATH"), "plugins", plugin)
            if "alembic.ini" in os.listdir(plugin_path):
                self.log(1, "Alembic configuration found, executing migrations for plugin '{CYAN}{plugin_name}{RESET}'...", {"plugin_name": plugin})

                alembic_config = Config(os.path.join(plugin_path, "alembic.ini"))
                alembic_config.set_main_option("script_location", "plugins/{0}/migrations".format(plugin))
                alembic_config.set_main_option("version_table_name", "db_version_for_plugin_{0}".format(plugin))
                alembic_config.set_main_option("sqlalchemy.url", self.config.get_temp_value("database/db_string"))
                # Beginning with processing migrations for plugin.
                with conn.begin() as connection:
                    command.upgrade(alembic_config, "head")
            else:
                self.log(1, "No alembic configuration found for plugin '{CYAN}{plugin_name}{RESET}', skipping migrations execution", {"plugin_name": plugin})

