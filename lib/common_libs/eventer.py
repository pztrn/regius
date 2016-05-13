from collections import OrderedDict
import sys

from lib.common_libs.library import Library

"""@package Eventer
This package contains class which responsible for event handling.
All parts of application is able to add own events and event handlers.

This class will not be autoloaded, it should be loaded only if you want
to write event-based application.

This class is not using asyncio for now, all events are dispatched in
synchronous mode.
"""

class Eventer(Library):
    """
    This package contains class which responsible for event handling.
    All parts of application is able to add own events and event handlers.
    """

    _info = {
        "name"          : "Eventer library",
        "shortname"     : "eventer",
        "description"   : "This library responsible for all event-related actions."
    }

    def __init__(self):
        Library.__init__(self)

        self.__events = OrderedDict()

    def init_library(self):
        """
        Library initialization.

        For this class doing nothing that just print initialization
        message.
        """
        self.log(0, "Initializing Event Handler...")

    def add_event(self, event_name, description = None):
        """
        Adds event to events list. After adding event handlers can be added
        to event handlers list for this event with
        add_event_handler(name, priority, handler).

        @param event_name Name of event.
        """
        if not event_name in self.__events:
            caller = sys._getframe(1).f_locals["self"].__class__.__name__
            self.log(1, "Adding event '{YELLOW}{event_name}{RESET}' for module '{MAGENTA}{module_name}{RESET}'", {"event_name": event_name, "module_name": caller})
            self.__events[event_name] = {
                "module"        : caller,
                "name"          : event_name,
                "description"   : description,
                "handlers"      : OrderedDict()
            }

    def add_event_handler(self, event_name, handler, weight):
        """
        """
        caller = sys._getframe(1).f_locals["self"].__class__.__name__
        if event_name in self.__events:
            if not weight in self.__events[event_name]["handlers"]:
                self.log(1, "Adding handler '{CYAN}{handler}{RESET}' with weight {YELLOW}{weight}{RESET} for '{MAGENTA}{event_name}{RESET}'", {"handler": repr(handler), "weight": weight, "event_name": event_name})
                self.__events[event_name]["handlers"][weight] = {
                    "name"      : repr(handler),
                    "handler"   : handler
                }
            else:
                self.log(1, "{RED}Weight {YELLOW}{weight}{RED} for '{MAGENTA}{event_name}{RED}' already taken!{RESET}", {"weight": weight, "event_name": event_name})
        else:
            self.log(0, "{RED}ERROR:{RESET} event '{MAGENTA}{event_name}{RESET}' not registered!", {"event_name": event_name})

    def fire_event(self, event_name, data = None):
        """
        Fires event, if event exists in self.__events dictionary (e.g.
        event was added by some part of program.)

        @param event_name Name of event to fire.
        """
        if not event_name in self.__events:
            self.log(0, "{RED}ERROR{RESET}: failed to fire event '{CYAN}{event_name}{RESET}': event does not exist", {"event_name": event_name})
            return

        self.log(0, "Firing event '{CYAN}{event_name}{RESET}'...", {"event_name": event_name})
        for weight in self.__events[event_name]["handlers"]:
            self.log(2, "Firing handler '{MAGENTA}{handler}{RESET}' for '{CYAN}{event_name}{RESET}'...", {"event_name": event_name, "handler": self.__events[event_name]["handlers"][weight]["name"]})
            self.__events[event_name]["handlers"][weight]["handler"](data)

    def get_events(self):
        """
        Returns all available events. This can be used for iterating
        thru them, or for checking if event was already added.

        @retval list_of_events List of added events.
        """
        return self.__events.keys()