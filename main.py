#!/usr/bin/python3
from gi.repository import Gtk

import sys
from Gui.MainWindow import MainWindow
from Server import Server

class MyApplication(Gtk.Application):

	GUI_SERVER_PORT = 1600

	def __init__(self):
		Gtk.Application.__init__(self)

	def do_activate(self):
		self.win = MainWindow(self)
		self.win.connect('delete-event', self.on_exit)
		server = Server(self.GUI_SERVER_PORT, self.win)
		#self.win.show_all()

	def on_exit(self, event, data):
		# log message to be here
		pass

	def do_startup(self):
		Gtk.Application.do_startup(self)

app = MyApplication()
exit_status = app.run(sys.argv)
sys.exit(exit_status)
