#!/usr/bin/python3
import sys

from gi import require_version
require_version('Gtk', '3.0')
from gi.repository import Gtk

from Control import Control
from Log import Log


class AtsApp(Gtk.Application):

    def __init__(self):
        Gtk.Application.__init__(self)
        # create log writer
        self.log = Log("log.txt")

    def do_activate(self):
        # create control instance
        self.control = Control(self)
        self.control.gui.connect('delete-event', self.on_exit)
        # write start message to log
        self.log.write_log_message("application launched", True)

    def on_exit(self, event, data):
        # write close message to log
        self.control.destroy()
        self.log.write_log_message("application closed")

    def do_startup(self):
        Gtk.Application.do_startup(self)

app = AtsApp()
exit_status = app.run(sys.argv)
sys.exit(exit_status)

