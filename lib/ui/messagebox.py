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

from PyQt5.QtWidgets import QMessageBox

class MessageBox(QMessageBox):
    """
    This class is responsible for all message boxes we might show.
    """

    _info = {
        "name"          : "Message box",
        "shortname"     : "messagebox",
        "description"   : "This library responsible for all message boxes."
    }

    def __init__(self, box_type = None, title = None, text = None):
        QMessageBox.__init__(self)

        if box_type:
            if box_type == "warning":
                self.setIcon(QMessageBox.Warning)
            elif box_type == "critical":
                self.setIcon(QMessageBox.Critical)
            elif box_type == "error":
                self.setIcon(QMessageBox.Critical)

        if title:
            self.setWindowTitle("Tovarouchet - {0}".format(title))

        if text:
            if box_type == "error":
                self.setText("Tovarouchet encounter a critical error!\n\nThis is usually very bad! Report to developer!\n\nError was:\n\n{0}".format(text))

