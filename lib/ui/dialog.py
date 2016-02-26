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

from PyQt5.QtWidgets import QDialog

class Dialog(Library, QDialog):
    """
    This is a metaclass for all dialogs. It will share some common actions
    between all dialogs, for easier access.
    """

    def __init__(self):
        Library.__init__(self)
        QDialog.__init__(self)

    def closeEvent(self, event):
        """
        This method overrides Qt's closeEvent() method for QDialog.

        It will execute some actions, like sizes saving.
        """
        self.on_closeEvent()

    def init_dialog(self, loader):
        """
        This method executes on every dialog initialization and
        contains some tasks that should be done for every dialog.

        Do not override this method!
        """
        self.init_library_int(loader)

        self.config = self.loader.request_library("common_libs", "config")

        # Adding dialog to Loader's list, so it will be able to cleanup
        # later.
        self.loader.add_pointer(self.__module__, self)

    def on_closeEvent(self):
        """
        This method saving some common parameters, like dialog window
        size and position. They will be restored later with on_dialogOpen()
        method.

        This method executes by default on closeEvent() emitting, and
        can be triggered manually from any dialog that subclassed from
        lib.ui.Dialog() class.
        """
        self.log(1, "Dialog closing, saving parameters...")
        self.log(2, "Saving size: {0}".format(self.ui.size()))
        self.config.set_value("qsettings", "dialogs", "{0}_size".format(self._info["shortname"]), self.ui.size())
        self.log(2, "Saving position: {0}".format(self.ui.pos()))
        self.config.set_value("qsettings", "dialogs", "{0}_pos".format(self._info["shortname"]), self.ui.pos())

    def on_dialog_open(self):
        """
        This method restores some common parameters, like dialog window
        size and position on screen.

        This method should be launched manually after dialog UI
        initialization.

        Warning: to make this method work properly main UI instance
        should be called as self.ui!
        """
        sizes = self.config.get_value("qsettings", "dialogs", "{0}_size".format(self._info["shortname"]))
        position = self.config.get_value("qsettings", "dialogs", "{0}_pos".format(self._info["shortname"]))

        try:
            self.log(2, "Setting window sizes: {sizes}", {"sizes": sizes})
            self.ui.resize(sizes)
        except TypeError as e:
            self.log(0, "{RED}ERROR:{RESET} Failed to restore window sizes! Falling back to default...")

        try:
            self.log(2, "Setting window position: {position}", {"position": position})
            self.ui.move(position)
        except TypeError as e:
            self.log(0, "{RED}ERROR:{RESET} Failed to restore window position! Window manager will place window as he wants!")
