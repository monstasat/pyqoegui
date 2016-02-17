#!/usr/bin/python3
from gi import require_version
require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio
import sys

from Backend.Backend import Backend
from Gui.MainWindow import MainWindow
#from Usb.Usb import Usb

from Log import Log
from TranslateMessages import TranslateMessages


class Control(Gtk.Application):

	def __init__(self):
		Gtk.Application.__init__(self)

		# create log writer
		self.log = Log("log.txt")

		# create parameters which should be stored in control
		self.currentProgList = []
		self.analyzedProgList = []
		self.analysisSettings = []
		self.dumpSettings = []
		self.language = ""
		self.color_theme = ""
		# parameters of current results page
		self.progTableVisible = True
		# parameters of plot page
		# parameters of all results page

		# create message translator
		self.msg_translator = TranslateMessages()
		# execute server for receiving messages from gstreamer pipeline
		self.start_server(1600)

	# start server
	def start_server(self, port):
		# server for recieving messages from gstreamer pipeline
		server = Gio.SocketService.new()
		server.add_inet_port(port, None)
		# x - data to be passed to callback
		server.connect("incoming", self.message_from_pipeline_callback)
		server.start()

	def message_from_pipeline_callback(self, obj, conn, source):
		istream = conn.get_input_stream()
		ostream = conn.get_output_stream()
		buffer = istream.read_bytes(1000)
		data = buffer.get_data()

		#decode string back to unicode
		wstr = data.decode('utf-8', 'ignore')
		#print("message received!")
		#print(wstr)

		if len(wstr) > 0:
			if wstr[0] == 'd':
			# received program list
				progList = self.msg_translator.translate_prog_message_from_pipeline(wstr[1:])
				self.gui.progDlg.show_prog_list(progList)
			elif wstr[0] == 'v':
			# received video parameters
				#self.win.
				pass

	def on_new_prog_settings_from_gui(self, param):
		# get program list from gui
		progList = self.gui.get_applied_prog_list()

		# set gui for new programs
		progNames = self.msg_translator.translate_prog_list_to_prog_names(progList)
		self.gui.set_new_programs(progNames)

		# get xids from gui renderers
		xids = self.gui.get_renderers_xids()

		# apply new settings to backend
		self.backend.apply_new_program_list(progList, xids)

	def do_activate(self):
		self.backend = Backend(1)
		self.gui = MainWindow(self)
		# self.usb = Usb()

		self.backend.start_all_pipelines()

		# write start message to log
		self.log.write_log_message("application launched", True)

		# connect to gui signals
		self.gui.connect('delete-event', self.on_exit)
		self.gui.connect('new_settings_prog_list', self.on_new_prog_settings_from_gui)
		# connect to usb signals
		# --

	def on_exit(self, event, data):
		# write close message to log
		self.backend.terminate_all_pipelines()
		self.log.write_log_message("application closed")

	def do_startup(self):
		Gtk.Application.do_startup(self)

app = Control()
exit_status = app.run(sys.argv)
sys.exit(exit_status)
