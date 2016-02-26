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

from lib.common_libs import common
from lib.common_libs.library import Library

class Login_widget(QWidget, Library):
    """
    This widget is used in main tab widget and added on every launch,
    if authorization is needed for application.
    """

    _info = {
        "name"          : "Login widget",
        "shortname"     : "loginwidget",
        "description"   : "This widget is responsible for user log in."
    }

    def __init__(self):
        QWidget.__init__(self)
        Library.__init__(self)

    def init_library(self):
        """
        Login widget initialization.
        """
        self.ui = self.loader.request_ui("ui/login_widget", self)

        self.__main_ui = self.loader.request_ui("ui/main_window", None)

        self.config = self.loader.request_library("common_libs", "config")
        self.database = self.loader.request_library("common_libs", "database")

        self.ui.app_name.setText('<html><head/><body><p><span style="font-size:18pt; font-weight:600;">{0}</span></p></body></html>'.format(self.config.get_temp_value("main/application_name")))

        # Load database configuration and obtain connections.
        self.log(1, "Obtaining connections list...")
        __db_data = self.config.get_keys_for_group("qsettings", "database")

        connections = []

        for item in __db_data:
            conn_name = item.split("_")[0]
            if not conn_name in connections:
                connections.append(conn_name)

        self.log(2, "Connections list obtained:")
        self.log(2, connections)

        self.log(1, "Adding connections to connections selector...")

        for conn_name in connections:
            self.ui.connections.addItem(conn_name)

        self.__tab_index = self.__main_ui.tabs.addTab(self.ui, "Login...")

        self.__main = self.loader.request_library("main", "gui")

        self.ui.login_button.clicked.connect(self.__check_auth)
        # Enable login and password input fields only if auth = 1
        # in preseed config.
        if self.config.get_value("json", "preseed", "auth") == 1:
            self.ui.username.returnPressed.connect(self.__check_auth)
            self.ui.password.returnPressed.connect(self.__check_auth)
        else:
            self.ui.username.setVisible(False)
            self.ui.password.setVisible(False)
            self.ui.label_2.setVisible(False)
            self.ui.label_3.setVisible(False)

    def __check_auth(self):
        """
        Checks passed user and password against local or remote database.
        """
        # Do nothing for now, pass directly to app loading.
        self.log(1, "Creating database connection...")
        result = self.database.create_connection(self.ui.connections.currentText())
        session = self.database.get_session()
        users_table = self.database.get_database_mapping("users")
        if not result:
            self.ui.login_status.setText('<html><head/><body><p><span style="font-weight:600; color: red;">Failed to connect to users database!</span></p></body></html>')
            return

        self.ui.login_status.setText('<html><head/><body><p>Database connection established</p></body></html>')

        if self.config.get_value("json", "preseed", "auth"):
            self.ui.login_status.setText('<html><head/><body><p>Checking user and password...</p></body></html>')

            ua = self.loader.request_library("database_tools", "useractions")
            result = ua.check_user_auth(self.ui.username.text(), self.ui.password.text())
            if not result:
                self.log(0, "{RED}Failed to authenticate user {YELLOW}{username}{RESET}", {"username": self.ui.username.text()})
                self.ui.login_status.setText('<html><head/><body><p><span style="font-weight:600; color: red;">Failed to authenticate user!</span></p></body></html>')
                return
            else:
                if result == "USERACTIONS_USER_NOT_FOUND":
                    self.ui.login_status.setText('<html><head/><body><p><span style="font-weight:600; color: red;">Invalid username or password!</span></p></body></html>')
                    return
                elif result == "USERACTIONS_AUTH_OK":
                    self.ui.login_status.setText('<html><head/><body><p>Authentication successful</p></body></html>')
                else:
                    self.ui.login_status.setText('<html><head/><body><p><span style="font-weight:600; color: red;">Unhandled authentication error: {error}!</span></p></body></html>', {"error": result})
                    return

            self.log(0, "Authenticated user '{YELLOW}{username}{RESET}'", {"username": self.ui.username.text()})
        else:
            self.log(0, "Single-user profile, will not check for password...")

        self.__main_ui.tabs.removeTab(self.__tab_index)
        self.__main.load_app()
