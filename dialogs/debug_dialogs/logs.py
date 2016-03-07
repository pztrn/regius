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

import time

from PyQt5.QtGui import QColor, QFont, QFontDatabase

from lib.ui.dialog import Dialog

class LogsDialog(Dialog):
    """
    This module responsible for all actions withit Logs debug dialog.
    """

    _info = {
        "name"          : "Logs dialog",
        "shortname"     : "logsdialog",
        "description"   : "This module responsible for all actions with logs dialog."
    }

    def __init__(self):
        Dialog.__init__(self)

        # Flag which indicates that we should not add any logs in log
        # widget, as we're loading logs now.
        self.__loading_logs = 0
        # Text that was put in searchbox.
        self.__text_to_search = ""
        # Log lines total count.
        self.__log_lines_total = 0
        # Shown log lines count.
        self.__log_lines_shown = 0

    def append_line(self, dict):
        """
        This method appends line to QTextEdit widget that is used for
        logs output.
        """
        if self.__loading_logs:
            return

        if len(dict) == 0:
            return

        log_string = "[{level}][MAXMEM: {RES}][{caller}][{ts}] {data}".format(**dict["data"])

        orig_log_text_color = self.ui.main_log.textColor()

        # First - catch very important keywords, like "error" and
        # "warn*". If they're present - colorize line and skip
        # colorizing based on debug level. This achieved with
        # checking "color_set" boolean.
        # For filtering we will use "filter_type" variable.
        color_set = 0
        filter_type = None

        # If "error" was found in lower-case string: use magenta
        # color or it.
        if "error" in log_string.lower():
            self.ui.main_log.setTextColor(QColor("magenta"))
            color_set = 1

        # If "warn" was found in lower-case string: use orange
        # color or it.
        if "warn" in log_string.lower():
            self.ui.main_log.setTextColor(QColor("orange"))
            color_set = 1

        # If color wasn't yet set - determine line color based
        # on debug level.
        if not color_set:
            if dict["level"] == 1:
                self.ui.main_log.setTextColor(QColor("green"))

            if dict["level"] == 2:
                self.ui.main_log.setTextColor(QColor("red"))

        # Second - determine if we should append this log line.
        # It depends on current filter settings.
        append = False

        # Determine if log line should be added based on debug level
        # filter.
        if self.__debug_level >= 0 and dict["level"] == 0:
            append = True

        if self.__debug_level >= 1 and dict["level"] == 1:
            append = True

        if self.__debug_level == 2 and dict["level"] == 2:
            append = True

        # Despite on debug level - we should not put log lines
        # in widget if Log type parameters not include
        # warnings and/or errors.
        if ("warn" in log_string.lower() or "error" in log_string.lower()) and self.__log_type == 0:
            append = False
        if "error" in log_string.lower() and self.__log_type <= 1:
            append = False

        # If we are searching for something - check if current
        # log line contains text we're searching for.
        if not self.__text_to_search.lower() in log_string.lower():
            append = False

        if append:
            self.ui.main_log.append(log_string)
            # Set log lines counts.
            self.__log_lines_shown += 1

        self.__log_lines_total += 1

        self.ui.main_log.setTextColor(orig_log_text_color)

        self.ui.log_lines_total.setText(str(self.__log_lines_total))
        self.ui.log_lines_shown.setText(str(self.__log_lines_shown))

    def closeEvent(self, event):
        """
        This method overrides default closeEvent(). It will save filters
        selected by user into configuration storage.
        """
        # Saving size and position.
        self.on_closeEvent()

        # Clearing widget.
        self.ui.main_log.clear()

        self.config.set_value("qsettings", "logs_browser", "log_type", self.ui.log_type.currentIndex())
        self.config.set_value("qsettings", "logs_browser", "debug_level", self.ui.debug_level.currentIndex())

        self.logger.unregister_callback("logsdialog")

    def load(self):
        """
        Load window.
        """
        self.ui = self.loader.request_ui("ui/debug_dialogs/logs", self)

        self.logger = self.loader.request_library("common_libs", "logger")

        # Set monospace font.
        font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        self.ui.main_log.setFont(font)

        # UI work.
        # Load configuration for filters.
        self.__load_configuration()
        # Connect UI elements to methods.
        self.__connect_signals()
        # Execute default actions for dialog opening.
        self.on_dialog_open()
        self.ui.show()

        # Load current set of log lines.
        self.load_logs()
        # Register callback.
        self.logger.register_callback("logsdialog", self.append_line)

    def load_logs(self):
        """
        Loads logs into log widget.

        It will also respect user-selected filters (log type and
        debug level).
        """
        self.__log_lines_shown = 0
        self.__log_lines_total = 0

        # Clearing log widget, just in case.
        self.ui.main_log.clear()

        # Get logs.
        self.__loading_logs = 1
        logs = self.logger.get_logs()
        self.__loading_logs = 0

        # Fill log widget.
        for item in logs:
            self.append_line(logs[item])

    def __connect_signals(self):
        """
        Connects UI elements to approriate methods.
        """
        self.ui.close_button.released.connect(self.close)
        self.ui.log_type.currentIndexChanged.connect(self.__filters_changed)
        self.ui.debug_level.currentIndexChanged.connect(self.__filters_changed)
        self.ui.searchbox.textChanged.connect(self.__search_in_logs)

    def __filters_changed(self):
        """
        This method executes when filter parameters changed.

        It will set new values for currently showing debug level and
        log type we want to see.

        After setting these parameters it will call self.load_logs()
        for repopulating log widget.
        """
        self.__log_type = self.ui.log_type.currentIndex()
        self.__debug_level = self.ui.debug_level.currentIndex()
        self.log(1, "Logs filtering configuration changed:")
        self.log(1, "Debug level: {0}".format(self.__debug_level))
        self.log(1, "Log type: {0}".format(self.__log_type))
        self.load_logs()

    def __load_configuration(self):
        """
        Loads log type and debug level filters value.

        These values might not present, so we can safely pass all
        possible errors that might appear.
        """
        self.__log_type = self.config.get_value("qsettings", "logs_browser", "log_type")
        self.__debug_level = self.config.get_value("qsettings", "logs_browser", "debug_level")

        if not self.__log_type:
            self.__log_type = 0
        if not self.__debug_level:
            self.__debug_level = 0

        try:
            self.log(2, "Setting Log type: {0}".format(self.__log_type))
            self.ui.log_type.setCurrentIndex(self.__log_type)
        except:
            pass

        try:
            self.log(2, "Setting Debug level: {0}".format(self.__debug_level))
            self.ui.debug_level.setCurrentIndex(self.__debug_level)
        except:
            pass

    def __search_in_logs(self, text):
        """
        This method responsible for searching in logs. It executes
        every time contents of searchbox is changed.
        """
        if text != self.__text_to_search:
            self.__text_to_search = text
            self.load_logs()
