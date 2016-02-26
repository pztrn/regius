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
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import exc
from sqlalchemy import pool
from sqlalchemy.orm import sessionmaker
import sys

from lib.common_libs import common
from lib.common_libs.exception import TovarouchetException
from lib.common_libs.library import Library

from lib.database_tools.migrator import Migrator

class Database(Library):
    """
    This library responsible for all database-related actions.

    It will create a connection and a session for later ORM usage.
    But, of course, this class can be used in plain SQL mode, for accelerating
    development process.

    If you want to use it for ORM, just issue somehting like:

        base = database.create_base()

        class Users(base):
            ...

    See SQLAlchemy documentation for more on this topic.

    If you want to use SQL mode, you can issue something like:

        database.execute(query)
        database.commit()

    Second line is neccessary if you do database changes.

    For batch execution issue:

        database.executemany(list_of_queries)

    """

    _info = {
        "name"          : "Database library",
        "shortname"     : "database",
        "description"   : "This module responsible for all actions with database."
    }

    def __init__(self):
        Library.__init__(self)

    def create_connection(self, connection_name):
        """
        Creates connection to database.

        In case of error will set temporary option "DB_ERROR_CODE" and
        "DB_ERROR_DESCRIPTION", for later usage by other modules.
        """
        self.log(0, "Trying to connect to database '{conn_name}'...", {"conn_name": connection_name})

        # Creating engine string.
        self.log(2, "Composing engine string...")

        __db_type = "sqlite"
        __cfg_db_type = int(self.config.get_value("qsettings", "database", "{0}_type".format(connection_name)))

        # Checking for connection type.
        if __cfg_db_type == 1:
            __db_type = "postgresql+psycopg2"
        elif __cfg_db_type == 2:
            __db_type = "mysql+pymysql"

        self.log(2, "Connection type: {__db_type}", {"__db_type": __db_type})

        # Checking if port is defined. If not - use approriate default
        # one.
        # First we will set default ports depending on database type.
        # After that we will check if port was defined in connection
        # and, if yes, will use it.
        __port = None
        if "postgresql" in __db_type:
            __port = 5432
        elif "mysql" in __db_type:
            __port = 3306

        if self.config.get_value("qsettings", "database", "{0}_port".format(connection_name)):
            __port = self.config.get_value("qsettings", "database", "{0}_port".format(connection_name))

        if __port:
            __port = ":{0}".format(__port)
        else:
            __port = ""

        # If port was defined - add ":" in front, so it will be
        # counted as port. If nothing is defined, then it will
        # use default port.
        self.__db_engine = "{0}://{1}:{2}@{3}{4}/{5}".format(
            __db_type,
            self.config.get_value("qsettings", "database", "{0}_user".format(connection_name)),
            self.config.get_value("qsettings", "database", "{0}_pass".format(connection_name)),
            self.config.get_value("qsettings", "database", "{0}_host".format(connection_name)),
            __port,
            self.config.get_value("qsettings", "database", "{0}_dbname".format(connection_name))
            )

        self.log(1, "Engine string created: '{engine_string}'", {"engine_string": self.__db_engine})
        self.config.set_temp_value("database/db_string", self.__db_engine)

        try:
            self.__db_engine = create_engine(self.__db_engine, client_encoding='utf8', isolation_level="READ UNCOMMITTED")
            try:
                self.__db_engine.connect()
            except exc.OperationalError as e:
                self.log(0, "{RED}Error while connecting to database:{RESET}")
                self.log(0, "{RED}{error}{RESET}", {"error": repr(e)})
            self.log(0, "Connection to database established")
            return 1
        except exc.OperationalError as e:
            raise DatabaseConnectionException(e)

    def get_database_connection(self):
        """
        This method returns RAW database connection pointer to caller.
        Useful when running migrations.

        @retval db_engine Raw database connection.
        """
        return self.__db_engine

    def get_database_mapping(self, mapping_name):
        """
        Call lib.common_libs.loader.Loader for loading or returning a
        pointer to database mapping class, which can be used with
        database session.

        @param mapping_name Name of table to obtain mapping.
        @retval Mapping Instance of ``lib.common_libs.database_mappings.{mapping_name}``
        """
        caller = sys._getframe(1).f_locals["self"].__class__.__name__
        db_mapping = self.loader.request_db_mapping(mapping_name)
        self.log(2, "Returning database mapping '{BLUE}{mapping_name}{RESET}' to '{MAGENTA}{caller}{RESET}'", {"caller": caller, "mapping_name": mapping_name})
        return db_mapping

    def get_session(self):
        """
        Returns session object from currently established connection.

        @retval Session Session pointer.
        """
        caller = sys._getframe(1).f_locals["self"].__class__.__name__
        self.log(2, "Returning session object to '{CYAN}{caller}{RESET}'", {"caller": caller})
        session = sessionmaker(bind = self.__db_engine, expire_on_commit = False)
        session.configure(bind = self.__db_engine)
        return session()

    def init_library(self):
        """
        """
        self.log(0, "Initializing database connection...")

        self.__database_data = self.config.get_keys_for_group("qsettings", "database")

        common.TEMP_SETTINGS["DBMap"] = declarative_base()

    def load_mappings(self):
        """
        Loads tables mappings.
        """
        self.log(0, "Loading database mappings...")

        files = os.listdir(os.path.join(self.config.get_temp_value("SCRIPT_PATH"), "lib", "database_mappings"))

        for item in files:
            if item.startswith("__"):
                continue

            mapping_module_name = item.split(".")[0]
            self.log(1, "Loading database mapping: '{BLUE}{mapping_module_name}{RESET}'", {"mapping_module_name": mapping_module_name})

            self.loader.request_db_mapping(mapping_module_name)

class DatabaseConnectionException(TovarouchetException):
    """
    This exception appears on connection error.
    """
    def __init__(self, error):
        """
        @param error String that represents error message.
        """
        TovarouchetException.__init__(self)

        self.start_exception()
        self.log(0, "Exception occured while connecting to database:")
        self.log(0, repr(error))
        self.set_critical()
        self.end_exception()
