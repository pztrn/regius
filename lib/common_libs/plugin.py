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

class Plugin(Library):
    """
    This is a metaclass for all plugins. It will share some common actions
    between all plugins, for easier access.
    """

    def __init__(self):
        Library.__init__(self)

    def add_tab(self, tab_name, widget):
        """
        Adds a tab named 'tab_name' on main tab widget and sets 'widget'
        as its main widget.
        """
        self.__main_ui.tabs.addTab(widget, tab_name)

    def get_option_pane(self):
        """
        Returns a dictionary with option pane name and instance.
        """
        ui = {
            "name"      : self._info["shortname"],
            "widget"    : self.loader.request_ui("plugins/{0}/ui/options".format(self._info["shortname"]), None)
        }
        return ui

    def init_plugin(self):
        """
        Plugin initialization.
        """
        self.config = self.loader.request_library("common_libs", "config")

        if self.config.get_temp_value("UI") == "gui":
            self.__main_ui = self.loader.request_ui("ui/main_window", None)

            self.toolbar = self.__main_ui.main_toolbar
            self.statusbar = self.__main_ui.statusbar

            self.loading_widget = self.loader.request_library("ui", "loading_widget")

            self.set_loading_action = self.loading_widget.progress.setFormat

    def load_ui(self, ui_filepath):
        """
        Loads UI file for plugin.
        """
        ui = self.loader.request_ui(ui_filepath, None)
        return ui

    def on_shutdown(self):
        """
        Executes on application shutdown. Should be overrided by plugin
        if shutdown actions are required.
        """
        self.log(1, "Item '{CYAN}{plugin}{RESET}' have nothing to perform for shutdown", {"plugin": self._info["shortname"]})