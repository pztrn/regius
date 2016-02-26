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

import asyncio

from lib.common_libs.library import Library

class Timer(Library):
    """
    This library responsible for executing tasks with timeout. It allows other
    libraries to add, modify and delete timers based on their own logic.
    """

    _info = {
        "name"          : "Timer library",
        "shortname"     : "timer",
        "description"   : "This library responsible for all timing actions, like executing tasks with timeout."
    }

    def __init__(self):
        Library.__init__(self)

        self.__tasks = {}

        self.timer_loop = asyncio.get_event_loop()

    def add_timer(self, name, description, callback, timeout, repeatable):
        """
        Adds delayed calls to timer loop.
        """
        if not name in self.__tasks:
            self.log(1, "Adding timer: {name} | {description} | {class}.{callback} | {timeout}", {"name": name, "description": description, "class": callback.__self__.__class__.__name__, "callback": callback.__name__, "timeout": timeout})
            # ToDo: add check for timeout, it should not be more than 24 hours.
            task = self.timer_loop.call_later(timeout, self.timer_exec, {"callback": callback, "name": name})
            self.__tasks[name] = {
                "name"              : name,
                "description"       : description,
                "callback"          : callback,
                "timeout"           : timeout,
                "repeatable"        : repeatable,
                "handle"            : task
            }
        else:
            self.log(1, "Task '{BLUE}{name}{RESET}' already exists, will not add it until it will be removed.", {"name": name})

    def timer_exec(self, args):
        """
        This function is kinda a "decorator" around callback passed for
        self.add_timer().

        All timered calls will be wrapped with this function. As we have
        callback defined in self.__tasks[task_name], it will be executed.
        After execution we will look into self.__tasks[task_name]["repeatable"]
        variable, and if it is set to True - we will re-add timer action
        for re-execution. Otherwise we will just remove this task.
        """
        self.log(1, "Timer action! Callback: {0}".format(args["callback"]))
        args["callback"]()
        if args["name"] in self.__tasks:
            if self.__tasks[args["name"]]["repeatable"]:
                data = self.__tasks[args["name"]]
                self.remove_timer(data["name"])
                self.add_timer(data["name"], data["description"], data["callback"], data["timeout"], data["repeatable"])
            else:
                self.remove_timer(data["name"])

    def on_shutdown(self):
        """
        Executes some timer-specific actions on shutdown.
        """
        self.log(1, "Closing timer event loop...")
        self.timer_loop.close()

    def remove_timer(self, name):
        """
        Removes timer from timers list.
        """
        if name in self.__tasks:
            self.log(1, "Removing timer '{BLUE}{name}{RESET}'", {"name": name})
            self.__tasks[name]["handle"].cancel()
            del self.__tasks[name]
        else:
            self.log(1, "Task '{BLUE}{name}{RESET}' not found", {"name": name})
