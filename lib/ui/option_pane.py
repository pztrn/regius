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

from lib.common_libs.library import Library

from PyQt5.QtWidgets import QWidget

class OptionPane(Library, QWidget):
    """
    This is a metaclass for all dialogs. It will share some common actions
    between all dialogs, for easier access.
    """

    def __init__(self):
        Library.__init__(self)
        QWidget.__init__(self)

    def init_widget_int(self, loader):
        """
        This method executes on every widget initialization and
        contains some tasks that should be done for every widget.

        Do not override this method!
        """
        self.init_library_int(loader)

        self.config = self.loader.request_library("common_libs", "config")
