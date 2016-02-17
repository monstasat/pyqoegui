#!/usr/bin/python3
from gi.repository import Gtk

import sys
from Gui.MainWindow import MainWindow
from Server import Server
from Log import Log
from Backend import Backend

class MyApplication(Gtk.Application):

	GUI_SERVER_PORT = 1600

	def __init__(self):
		Gtk.Application.__init__(self)
		self.log = Log("log.txt")
		self.gs_pipeline = Backend()

	def callback(self, param):
		print('hello man!')

	def do_activate(self):
		self.win = MainWindow(self)
		self.win.connect('delete-event', self.on_exit)
		server = Server(self.GUI_SERVER_PORT, self.win)

		self.win.connect('new_settings_prog_list', self.callback)

		self.gs_pipeline.execute()

		# write start message to log
		self.log.write_log_message("application launched", True)

	def on_exit(self, event, data):
		self.gs_pipeline.terminate()

		# write close message to log
		self.log.write_log_message("application closed")

	def do_startup(self):
		Gtk.Application.do_startup(self)

app = MyApplication()
exit_status = app.run(sys.argv)
sys.exit(exit_status)
