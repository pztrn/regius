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

# Base exception class.

"""@package exception
This module contains RegiusException class which is a base for
all MUI's exceptions. All exceptions should be subclassed from this
one.
"""

from lib.common_libs import common
from lib.common_libs.library import Library

class RegiusException(BaseException, Library):
    """
    Base exception. All other exceptions should be subclassed
    from this.
    """
    def __init__(self):
        BaseException.__init__(self)
        Library.__init__(self)
        self.init_library_int(common.LOADER)

        # This flag represents exception's critical state.
        self.__critical = 0

    def end_exception(self):
        """
        This method should be called on completing custom exception
        output. It will check if exception is critical.

        If exception is critical - it will print a notice about it
        and exit with exit code 1. Otherwise it will just print
        70's of "=" character, to distinguish exception in log from
        other text.
        """
        if self.__critical:
            self.log(0, "This is a critical problem, exiting...")
        self.log(0, "{RED}" + ("=" * 70))

        if self.__critical:
            exit(1)

    def set_critical(self):
        """
        This method will set critical flag for this exception.
        """
        self.__critical = 1

    def start_exception(self):
        """
        This is a starting point for every exception. It will print
        70's of "=" character and set text color to red, to distinguish
        exception in log from other text.
        """
        self.log(0, "{RED}" + ("=" * 70))
        self.log(0, "{app_name} experiencing a problem:", {"app_name": self.config.get_temp_value("main/application_name")})

