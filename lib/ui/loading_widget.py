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

# Loading widget.

from PyQt5.QtWidgets import QWidget

from lib.common_libs.library import Library

class Loading_widget(QWidget, Library):
    """
    This widget is used in main tab widget and added on very beginning
    of initialization. This widget will show a progress of application
    loading, with possible additional pixmap.
    """

    _info = {
        "name"          : "Loading widget",
        "shortname"     : "loadingwidget",
        "description"   : "This widget have no special responsibility. It shows loading progress."
    }

    def __init__(self):
        QWidget.__init__(self)
        Library.__init__(self)

    def increment_progress(self):
        """
        Increments progress bar value by 1.

        This method isn't passed to plugins, because every plugin
        should have only one step in loading progress window, at
        least for now.
        """
        self.__progress += 1
        self.progress.setValue(self.__progress)

    def init_library(self):
        """
        Loading widget library initialization.
        """
        self.config = self.loader.request_library("common_libs", "config")
        self.ui = self.loader.request_ui("ui/loading_widget", self)
        self.__main_ui = self.loader.request_ui("ui/main_window", None)

        self.__tab_index = self.__main_ui.tabs.addTab(self.ui, "Loading...")

        self.__progress = 0

        # Force progress be 0 in progress bar.
        self.ui.progress.setValue(0)
        # Force 0 to be a minimum value for progress bar.
        self.ui.progress.setMinimum(0)

    def set_action(self, text):
        """
        Sets current action.
        """
        self.ui.progress.setFormat("[{0} / {1}] {2}".format(self.ui.progress.value(), self.ui.progress.maximum(), text))
        self.ui.loading_log.append("[<b>{0}</b> / <b>{1}</b>] {2}".format(self.ui.progress.value(), self.ui.progress.maximum(), text))
        # Process app events, if neccessary.
        self.config.get_temp_value("APP").processEvents()

    def set_appname(self, app_name):
        """
        Sets current application name.
        """
        self.app_name = app_name
        self.ui.appname.setText('<html><head/><body><p align="center"><span style=" font-size:16pt; font-weight:600;">{0} is loading...</span></p></body></html>'.format(self.app_name))

    def set_loading_complete(self):
        """
        Activates "Proceed" button when loading was complete.

        This method should not be called if errors appeared, because
        this leading to inconsistent application behaviour!
        """
        self.log(0, "Loading complete.")
        self.ui.appname.setText('<html><head/><body><p align="center"><span style=" font-size:16pt; font-weight:600;">{0} loaded!</span></p></body></html>'.format(self.app_name))
        self.__main_ui.tabs.setTabText(self.__tab_index, "Loaded!")
        self.__main_ui.tabs.setEnabled(True)
        self.ui.close_widget.setEnabled(True)
        self.ui.close_widget.released.connect(self.__delete_widget)

    def set_progress_maximum(self, maximum = 0):
        """
        Sets progressbar maximum, assuming that every action will
        trigger +1 to it. It will be a sum of:

            * Core actions, that calculated separately.
            * Sum of plugins.

        Every plugin will have an ability to set own status text with
        self.set_loading_action(text) method.

        If maximum wasn't specified - 100 is used.
        """
        if maximum:
            self.ui.progress.setMaximum(maximum)
        else:
            self.ui.progress.setmaximum(100)

    def __delete_widget(self):
        """
        Deletes tab from main tab widget with loading widget.

        This method should be called only by clicking "Proceed" button!
        """
        self.__main_ui.tabs.removeTab(self.__tab_index)
