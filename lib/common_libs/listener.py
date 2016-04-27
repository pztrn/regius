import asyncio
import importlib
import sys

from lib.common_libs.library import Library

"""@package Listener
This package contains class which will start listening for client
connections in asyncio loop.
"""

class Listener(Library):
    """
    This class responsible for starting listening for client connections
    in asyncio loop.
    """

    def __init__(self):
        Library.__init__(self)

        self.__proto = None
        self.__address = None
        self.__port = None

    def init_library(self):
        """
        Library initialization.

        For this class doing nothing that just print initialization
        message.
        """
        self.log(0, "Initializing Listener...")

        self.__proto = self.config.get_value("all", "listener", "protocol")
        importlib.import_module("lib.protocols." + self.__proto)
        exec("self.ph = sys.modules['lib.protocols.{0}'].{1}".format(self.__proto, self.__proto.capitalize()))
        self.__proto_handler = self.ph
        self.log(1, "Using protocol {CYAN}{proto}{RESET}", {"proto": self.__proto})
        self.__address = self.config.get_value("all", "listener", "address")
        self.__port = self.config.get_value("all", "listener", "port")

    def start_listening(self):
        """
        This method starts listening on port.
        """
        loop = asyncio.get_event_loop()
        coro = loop.create_server(self.__proto_handler, self.__address, self.__port)
        self.log(0, "Starting listening for connections on tcp://{address}:{port}/", {"address": self.__address, "port": self.__port})
        server = loop.run_until_complete(coro)
        try:
            loop.run_forever()
        except KeyboardInterrupt as e:
            print()
            self.close_app()
        except RuntimeError as e:
            self.log(0, "{RED}ERROR:{RESET} RuntimeError appeared: {error}", {"error": e})
            self.log(0, "{RED}Error appeared in __listen_to_tcp() method.{RESET}")

        server.close()
        loop.run_until_complete(server.wait_closed())
        loop.close()
