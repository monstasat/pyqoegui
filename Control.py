from gi.repository import Gtk, Gio
import time

from Backend.Backend import Backend
from Gui.MainWindow import MainWindow
#from Usb.Usb import Usb

from Backend import State
from Config import Config
from Log import Log
from TranslateMessages import TranslateMessages

class Control():

	def __init__(self, app):

		#self.received = False

		# create log writer
		self.log = Log("log.txt")
		# create config
		self.config = Config()
		# create message translator
		self.msg_translator = TranslateMessages()
		# execute server for receiving messages from gstreamer pipeline
		self.start_server(1600)

		# create parameters which should be stored in control
		self.currentProgList = []
		self.analyzedProgList = self.config.load_prog_list()
		self.analysisSettings = []
		self.dumpSettings = []
		self.language = ""
		self.color_theme = ""
		# parameters of current results page
		self.progTableVisible = True
		# parameters of plot page
		# parameters of all results page

		self.backend = Backend(1)
		self.gui = MainWindow(app)
		# self.usb = Usb()

		# connect to gui signals
		self.gui.connect('new_settings_prog_list', self.on_new_prog_settings_from_gui)
		# connect to usb signals
		# --

		# execute all gstreamer pipelines
		self.backend.start_all_pipelines()

		# set gui for analyzed programs
		self.apply_prog_list_to_gui(self.analyzedProgList)

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

		if len(wstr) > 0:
			if wstr[0] == 'd':
			# received program list
				progList = self.msg_translator.translate_prog_string_to_prog_list(wstr[1:])
				self.gui.progDlg.show_prog_list(progList)
				compared_prog_list = self.msg_translator.translate_prog_list_to_compared_prog_list(self.analyzedProgList, progList)
				#if self.received == False:
				print("comp prog list: " + str(compared_prog_list))
				self.apply_prog_list_to_backend(compared_prog_list)
				#self.received = True
			elif wstr[0] == 'v':
			# received video parameters
				pass
			# received end of stream
			elif wstr[0] == 'e':
				self.on_end_of_stream(int(wstr[1:]))

	# make changes in gui according to prog list
	def apply_prog_list_to_gui(self, progList):
		# set gui for new programs
		progNames = self.msg_translator.translate_prog_list_to_prog_names(progList)
		self.gui.set_new_programs(progNames)

	# applying prog list to backend
	def apply_prog_list_to_backend(self, progList):
		# get xids from gui renderers
		xids = self.gui.get_renderers_xids()

		# apply new settings to backend
		self.backend.apply_new_program_list(progList, xids)

	# if stream has ended, restart corresponding gstreamer pipeline
	def on_end_of_stream(self, stream_id):
		state = self.backend.get_pipeline_state(stream_id)
		if state is State.RUNNING:
			self.backend.restart_pipeline(stream_id)
			# send blank prog list of corresponding stream id to gui
			self.gui.progDlg.show_prog_list([stream_id, []])

	def on_new_prog_settings_from_gui(self, param):
		# get program list from gui
		self.analyzedProgList = self.gui.get_applied_prog_list()

		# extract streams that are selected
		stream_ids = self.msg_translator.translate_prog_list_to_stream_ids(self.analyzedProgList)

		# restart pipelines with selected ids
		for process_id in stream_ids:
			self.backend.restart_pipeline(process_id)

		# save program list
		self.config.save_prog_list(self.analyzedProgList)

	def destroy(self):
		# terminate all gstreamer pipelines
		self.backend.terminate_all_pipelines()
