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

import hashlib
from sqlalchemy.orm import exc

from lib.common_libs.library import Library

class Useractions(Library):
    """
    """

    _info = {
        "name"          : "User actions library",
        "shortname"     : "useractions",
        "description"   : "This library responsible for all actions with system users."
    }

    def __init__(self):
        Library.__init__(self)

    def check_user_auth(self, username, password):
        """
        """
        self.log(2, "Creating password hash for user '{YELLOW}{username}{RESET}'...", {"username": username})
        pw_hash = hashlib.sha256()
        pw_hash.update(password.encode("utf-8"))
        hashed_pw = pw_hash.hexdigest()

        self.log(2, "Getting user infomation from database...")
        try:
            user_data = self.db_session.query(self.__user_mapping).filter(self.__user_mapping.username == username).one()
        except exc.NoResultFound as e:
            self.log(0, "{RED}User {username} not found!{RESET}", {"username": username})
            return "USERACTIONS_USER_NOT_FOUND"

        self.log(2, "Hash from database: {db_hash}, hashed password: {hashed_pw}", {"db_hash": user_data.password, "hashed_pw": hashed_pw})
        if user_data.password == hashed_pw:
            self.config.set_temp_value("CURRENT_USER", username)
            return "USERACTIONS_AUTH_OK"

    def init_library(self):
        """
        """
        self.__database = self.loader.request_library("common_libs", "database")
        self.db_session = self.__database.get_session()
        self.__user_mapping = self.loader.request_db_mapping("users")
