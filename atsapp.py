#!/usr/bin/python3
from gi.repository import Gtk, Gio

import sys
from Gui.MainWindow import MainWindow

class MyApplication(Gtk.Application):

	def __init__(self):
		Gtk.Application.__init__(self)

	def send_message(self, msg, destination):
		client = Gio.SocketClient.new()
		connection = client.connect_to_host("localhost", destination, None)
		istream = connection.get_input_stream()
		ostream = connection.get_output_stream()

		# send message
		ostream.write(msg)

		# close connection
		connection.close(None)

	def incoming_callback(self, obj, conn, source, data):
		istream = conn.get_input_stream()
		ostream = conn.get_output_stream()
		buffer = istream.read_bytes(1000)
		data[0] = buffer.get_data()

		#decode string back to unicode
		wstr = data[0].decode('utf-8', 'ignore')
		#print("msg of type '" + wstr[0] + "' received!")
		print(wstr)

		if len(wstr) > 0:
			# if received program list
			if wstr[0] == 'd':
				self.win.progDlg.show_prog_list(wstr[1:])
			# if received video parameters
			elif wstr[0] == 'v':
				#self.win.
				pass

	def do_activate(self):
		self.win = MainWindow(self)
		self.win.connect('delete-event', self.on_exit)
		self.win.show_all()

		# code to set some elements initially visible/invisible
		self.win.cur_results_page.hide_renderer_and_table()
		# if table is invisible, hide the button
		self.win.manage_table_revealer_button_visibility()

		# server for recieving messages from gstreamer pipeline
		x = ["foo"]
		server = Gio.SocketService.new()
		server.add_inet_port(common.GUI_PORT, None)
		# x - data to be passed to callback
		server.connect("incoming", self.incoming_callback, x)
		server.start()

	def on_exit(self, event, data):
		pass

	def do_startup(self):
		Gtk.Application.do_startup(self)

app = MyApplication()
exit_status = app.run(sys.argv)
sys.exit(exit_status)
