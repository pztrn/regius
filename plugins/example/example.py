import time

from lib.common_libs.plugin import Plugin

class Example_Plugin(Plugin):
    """
    This is an example plugin, which will help you to start developing
    your own plugins rapidly.
    """

    _info = {
        "name"          : "Example plugin",
        "shortname"     : "example",
        "description"   : "This is an example plugin, which will help you to start developing your own plugins rapidly."
    }

    def __init__(self):
        Plugin.__init__(self)

    def initialize(self):
        """
        Goods plugin initialization.
        """
        self.log(0, "Initializing plugin...")

        self.set_loading_action("Loading UI and adding it as tab...")
        self.__add_main_ui_tab()

    def __add_main_ui_tab(self):
        """
        Adds a tab to main UI.
        """
        self.ui = self.load_ui("plugins/example/ui/example_widget")
        self.add_tab("Example plugin", self.ui)
