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

from collections import OrderedDict
import datetime
import json
import os
import platform
import resource
import sys

from lib.common_libs import common
from lib.common_libs.library import Library

############################# COLORS DEFINITION
# Colors for terminal output.
TERM_COLORS = {
    "RESET"     : "\033[1;m",
    "RED"       : "\033[1;31m",
    "GREEN"     : "\033[1;32m",
    "YELLOW"    : "\033[1;33m",
    "BLUE"      : "\033[1;34m",
    "MAGENTA"   : "\033[1;35m",
    "CYAN"      : "\033[1;36m"
}
# Colors for file output.
FILE_COLORS = {
    "RESET"     : "",
    "RED"       : "",
    "GREEN"     : "",
    "YELLOW"    : "",
    "BLUE"      : "",
    "MAGENTA"   : "",
    "CYAN"      : ""
}
###############################################

class Logger(Library):
    """
    This library responsible for all logging actions. It will log
    simultaneously into console and in file.

    Regarding colors: while logging into console colors will be applied.
    When we will write data to file - we will cut colors off.

    Also this method is providing unified storage for logs, and it can
    be accessible anywhere in application. See get_logs(type) method.
    """

    _info = {
        "name"          : "Logger library",
        "shortname"     : "logger",
        "description"   : "This library responsible for all logging actions."
    }

    def __init__(self):
        Library.__init__(self)
        # Internal variables.
        self.__vars = {
            # Was file successfully opened for writing?
            "file_opened"       : False,
            "OS"                : platform.system()
        }

        self.__callbacks = {}
        self.__complete_log = OrderedDict()
        self.__log_sequence = 0

    def get_logs(self, **kwargs):
        """
        Returns a dictionary with logs.

        This method uses these parameters:

            * type - type of log entries (NORMAL, DEBUG, ERROR, TRACEBACK).
            * module - module name which produced logs.

        All other parameters are ignored for now.
        """
        logs_to_return = OrderedDict()
        for item in self.__complete_log:
            if "type" in kwargs:
                if self.__complete_log[item]["type"] == kwargs["type"]:
                    if "module" in kwargs and self.__complete_log[item]["module"] == kwargs["module"]:
                            logs_to_return[item] = self.__complete_log[item]
                    else:
                        logs_to_return[item] = self.__complete_log[item]
            else:
                if "module" in kwargs and self.__complete_log[item]["module"] == kwargs["module"]:
                    logs_to_return[item] = self.__complete_log[item]
                else:
                    logs_to_return[item] = self.__complete_log[item]

        self.log(1, "Returning logs to caller")
        self.log(1, "Lines in log: {0}".format(len(logs_to_return)))
        return logs_to_return

    def initialize_logger(self):
        """
        This method performs logger initialization.
        """
        print("Initializing logger...")

        if not os.path.exists(os.path.sep.join([self._script_path, "logs"])):
            os.makedirs(os.path.sep.join([self._script_path, "logs"]))

        try:
            log_path = os.path.sep.join([self._script_path, "logs", "main.log"])
            self.log(0, "Starting writing to log file: {log_path}", {"log_path": log_path})
            self.file = open(log_path, "a")
            self.__vars["file_opened"] = 1
            self.file.write("-" * 50 + "\n")
            self.log(0, "Logging to file started")
        except:
            self.log(0, "Failed to open log file for writing!")

    def log(self, level, data, replace_data = {}):
        """
        Do logprinting. By default, it will print to console. But this
        method might be extended in future.

        @level (int) - level of debug.
        @data (str) - data to print.
        @replace_data (dict) - dict with data to replace in @data. @data
        must contain replaceable data as with dict formatting in
        lowercase.
        """
        # Replace data for file logging.
        file_replace_data = replace_data.copy()
        file_replace_data.update(FILE_COLORS)

        # Replace data for terminal logging.
        term_replace_data = replace_data.copy()
        term_replace_data.update(TERM_COLORS)

        # Create timestamp.
        raw_timestamp = datetime.datetime.now()
        timestamp = raw_timestamp.strftime("%Y-%m-%d %H:%M:%S")

        # Prepare internally-used logs storage to be updated with
        # new data.
        self.__complete_log[self.__log_sequence] = {}

        # Create resource-usage thing.
        if self.__vars["OS"] == "Darwin":
            # MacOS reports bytes here.
            res_usage = str("%0.2f" % (resource.getrusage(resource.RUSAGE_SELF)[2] / 1024 / 1024)) + "M"
        elif self.__vars["OS"] == "Linux":
            # Linux reports kilobytes here.
            res_usage = str("%0.2f" % (resource.getrusage(resource.RUSAGE_SELF)[2] / 1024)) + "M"
        else:
            # We do not even suspect that anyone will launch it on anything else :)
            # Probably, we should add FreeBSD support?
            res_usage = "UNSUPPORTED"

        # If data is a dictionary or json - pass it to dumper first.
        if type(data) == dict:
            data = self.__dump_json(data)
        elif type(data) in (list, tuple):
            data = self.__dump_list(data)

        # Who called logger? :)
        caller_class = sys._getframe(1).f_locals["self"].__class__.__name__
        # Making caller name be maximum of 15 chars.
        if len(caller_class) > 15:
            caller_class = caller_class[:14]
        # If caller name less than 15 - add spaces to the end, to make output
        # prettier.
        caller_class = "{0}{1}".format(caller_class, (" " * (15 - len(caller_class))))

        # Calculating same thing for debug level.
        # We take "HARDDEBUG" length as maximum.
        level_max_length = len("HARDDEBUG")
        level_in_text = "HARDDEBUG"
        if level == 0:
            level_in_text = "NORMAL" + (" " * (level_max_length - len("NORMAL")))
        elif level == 1:
            level_in_text = "DEBUG" + (" " * (level_max_length - len("DEBUG")))

        # Initialize dict for file logging.
        # This dict is also used for pushing data to callback, see end
        # of this method.
        file_data = {}

        if level == 0:
            # Loglevel 0 - just do printing without extras.
            print("[{0}][MAXMEM: {1}][{2}][{3}] {4}".format(level_in_text, res_usage, caller_class, timestamp, data.format(**term_replace_data)))

            file_data = {
                "caller": caller_class,
                "ts"    : timestamp,
                "data"  : data.format(**file_replace_data),
                "RES"   : res_usage,
                "level" : level_in_text
            }
            # Write logging data to file only if file handler is open.
            if self.__vars["file_opened"]:
                self.file.write("[{level}][MAXMEM: {RES}][{caller}][{ts}] {data}\n".format(**file_data))
                self.file.flush()

            # Add to internal-accessible log storage.
            self.__complete_log[self.__log_sequence] = {
                "module": caller_class,
                "timestamp": raw_timestamp,
                "level": level,
                "data": file_data
            }

            if "ERROR" in file_data or "Error" in file_data["data"]:
                self.__complete_log[self.__log_sequence]["type"] = "error"
            else:
                self.__complete_log[self.__log_sequence]["type"] = "normal"
        elif level == 1:
            lightdebug = {
                "green" : TERM_COLORS["GREEN"],
                "yellow": TERM_COLORS["YELLOW"],
                "reset" : TERM_COLORS["RESET"],
                "caller": caller_class,
                "ts"    : timestamp,
                "data"  : data.format(**term_replace_data),
                "RES"   : res_usage,
                "level" : level_in_text
            }
            # Print to terminal.
            print("{green}[{level}]{green}[MAXMEM: {RES}]{yellow}[{caller}]{green}[{ts}]{reset} {data}".format(**lightdebug))

            file_data = {
                "caller": caller_class,
                "ts"    : timestamp,
                "data"  : data.format(**file_replace_data),
                "RES"   : res_usage,
                "level" : level_in_text
                }
            # Write to logfile.
            if self.__vars["file_opened"]:
                self.file.write("[{level}][MAXMEM: {RES}][{caller}][{ts}] {data}".format(**file_data) + "\n")
                self.file.flush()

            # Add to internal-accessible log storage.
            self.__complete_log[self.__log_sequence] = {
                "module": caller_class,
                "timestamp": raw_timestamp,
                "level": level,
                "data": file_data
            }

            if "ERROR" in file_data or "Error" in file_data["data"]:
                self.__complete_log[self.__log_sequence]["type"] = "error"
            else:
                self.__complete_log[self.__log_sequence]["type"] = "debug"

        elif level == 2:
            harddebug = {
                "red"   : TERM_COLORS["RED"],
                "green" : TERM_COLORS["GREEN"],
                "yellow": TERM_COLORS["YELLOW"],
                "reset" : TERM_COLORS["RESET"],
                "caller": caller_class,
                "ts"    : timestamp,
                "data"  : data.format(**term_replace_data),
                "RES"   : res_usage,
                "level" : level_in_text
            }
            # Print to terminal.
            print("{red}[{level}]{green}[MAXMEM: {RES}]{yellow}[{caller}]{green}[{ts}]{reset} {data}".format(**harddebug))

            file_data = {
                "caller": caller_class,
                "ts"    : timestamp,
                "data"  : data.format(**file_replace_data),
                "RES"   : res_usage,
                "level" : level_in_text
                }
            # Write to logfile.
            if self.__vars["file_opened"]:
                self.file.write("[{level}][MAXMEM: {RES}][{caller}][{ts}] {data}".format(**file_data) + "\n")
                self.file.flush()

            # Add to internal-accessible log storage.
            self.__complete_log[self.__log_sequence] = {
                "module": caller_class,
                "timestamp": raw_timestamp,
                "level": level,
                "data": file_data
            }

            if "ERROR" in file_data or "Error" in file_data["data"]:
                self.__complete_log[self.__log_sequence]["type"] = "error"
            else:
                self.__complete_log[self.__log_sequence]["type"] = "harddebug"

        self.__log_sequence += 1
        # Checking if filedata is here. If yes - push it to callback.
        # This push will happen only if callbacks were added with
        # self.register_callback() method.
        if len(file_data) > 0 and len(self.__callbacks) > 0:
            for callback in self.__callbacks:
                self.__callbacks[callback](self.__complete_log[self.__log_sequence - 1])

    def on_shutdown(self):
        """
        Closing logfile.
        """
        self.log(0, "Closing logger...")
        if self.__vars["file_opened"]:
            # Ensure that we have flushed logfile on disk...
            self.log(1, "Flushing unflushed things into file...")
            self.file.flush()
            # ...and close it!
            # Calling flush() here for second time to ensure that log message
            # "Closing log file..." will appear in log.
            self.log(1, "Closing log file...")
            self.file.flush()
            self.file.close()

    def register_callback(self, callback_name, pointer):
        """
        Registers an output callback. This callback must not be a file
        or console output, it's done by default.

        Every callback should accept a dictionary which contains:
            * Caller class name
            * Formatted timestamp
            * Resource usage (maximum memory usage only for now)
            * Debug level of this particular log line
            * Line data

        For example take a look at any "file_data" dictionary in log()
        method.
        """
        self.log(1, "Adding logging callback: {0}".format(pointer.__class__.__name__))
        self.__callbacks[callback_name] = pointer

    def unregister_callback(self, callback_name):
        """
        Removes callback from callbacks dict.
        """
        if callback_name in self.__callbacks:
            self.log(1, "Unregistering logger callback: '{MAGENTA}{callback_name}{RESET}'...", {"callback_name": callback_name})
            del self.__callbacks[callback_name]

    def __dump_json(self, dict):
        """
        Dumping JSON (aka dict object) into printable string.
        This allows to print resulted string with log() method
        defined above.

        log() method will automagically detects if passed data
        is a dict, and if yes - dump_json() will be called, and
        dictionary data printed.
        """
        data = json.dumps(dict, indent = 4, sort_keys = True)
        data = data.replace("{", "[")
        data = data.replace("}", "]")

        return "\n" + data

    def __dump_list(self, received_data):
        """
        Dumping list (aka slice) object into printable string.
        This allows to print resulted string with log() method
        defined above.

        log() method will automagically detects if passed data
        is a list, and if yes - dump_list() will be called, and
        list data printed.
        """
        data = []
        if type(received_data) == tuple:
            for item in received_data:
                if not type(item) == str:
                    data.append(str(item))
        elif type(received_data) == list:
            data = received_data
        else:
            self.log(0, "{RED}INTERNAL ERROR:{RESET} unsupported data type passed to Logger.__dump_list(): {datatype}", {"datatype": type(received_data)})

        return ", ".join(data)
