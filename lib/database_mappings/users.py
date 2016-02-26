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

from sqlalchemy import Column, Integer, String, VARCHAR

from lib.common_libs import common
DBMap = common.TEMP_SETTINGS["DBMap"]

class Users(DBMap):
    __tablename__ = "users"

    id = Column("id", Integer, primary_key = True, autoincrement = True, unique = True)
    username = Column("username", VARCHAR(255), nullable = False)
    password = Column("password", VARCHAR(255), nullable = False)
    email = Column("email", VARCHAR(255), nullable = False)
    groups_ids = Column("groups_ids", VARCHAR, nullable = False)
