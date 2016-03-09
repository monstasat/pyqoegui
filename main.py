#!/usr/bin/python3
import sys
import argparse

from gi import require_version
require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio

from Control.Control import Control
from Log import Log


class AtsApp(Gtk.Application):

    def __init__(self):
        Gtk.Application.__init__(self,flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE)
        # store for parsed command line options
        self.args = None
        # create log writer
        self.log = Log("log.txt")

    def do_activate(self):
        # create control instance
        self.control = Control(self)
        # write start message to log
        self.log.write_log_message("application launched", True)

    def do_startup(self):
        '''
        Gtk.Application startup handler
        '''
        Gtk.Application.do_startup(self)

    def do_shutdown(self):
        '''
        Gtk.Application shutdown handler
        Do clean up before the application is closed.
        this is triggered when self.quit() is called.
        '''
        self.control.destroy()
        # write close message to log
        self.log.write_log_message("application closed")
        Gtk.Application.do_shutdown(self)

    def do_command_line(self, args):
        '''
        Gtk.Application command line handler
        called if Gio.ApplicationFlags.HANDLES_COMMAND_LINE is set.
        must call the self.do_activate() to get the application up and running.
        '''
        Gtk.Application.do_command_line(self, args) # call the default commandline handler
        # make a command line parser
        parser = argparse.ArgumentParser(prog=sys.argv[0])
        # add a --width option
        parser.add_argument('--width',
                            default=1024,
                            type=int,
                            help="width of the main application window")
        # add a --height option
        parser.add_argument('--height',
                            default=768,
                            type=int,
                            help="height of the main application window")
        parser.add_argument('-f',
                            '--fullscreen',
                            action='store_true',
                            help="show main window in fullscreen mode")
        # parse the command line stored in args, but skip the first element (the filename)
        self.args = parser.parse_args(args.get_arguments()[1:])
        # call the main program do_activate() to start up the app
        self.do_activate()
        return 0

app = AtsApp()
exit_status = app.run(sys.argv)
sys.exit(exit_status)

