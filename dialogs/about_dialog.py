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

from lib.ui.dialog import Dialog

class AboutDialog(Dialog):
    """
    This module responsible for all actions within About dialog.
    """

    _info = {
        "name"          : "About dialog",
        "shortname"     : "aboutdialog",
        "description"   : "This module responsible for about dialog."
    }

    def __init__(self):
        Dialog.__init__(self)

    def closeEvent(self, event):
        """
        Executes on dialog close.
        """
        # Saving size and position.
        self.on_closeEvent()
        event.accept()

    def show_dialog(self):
        """
        Shows options dialog window.
        """
        self.__app_name = self.config.get_temp_value("app_name")

        # Load options window UI.
        self.ui = self.loader.request_ui("ui/about_dialog", self)

        self.ui.setWindowTitle("About {0}...".format(self.__app_name))

        self.ui.appname.setText('<html><head/><body><p align="center"><span style=" font-size:18pt; font-weight:600;">{0}</span></p></body></html>'.format(self.__app_name))
        self.ui.version.setText('<html><head/><body><p align="center">Version {0}</p></body></html>'.format(self.config.get_temp_value("version")))

        self.on_dialog_open()
        self.__connect_signals()
        self.ui.show()

    def __connect_signals(self):
        """
        Connects UI elements to methods.
        """
        self.ui.close_button.released.connect(self.close)
