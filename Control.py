from gi.repository import Gtk, Gio
import time

from Backend.Backend import Backend
from Gui.MainWindow import MainWindow
#from Usb.Usb import Usb

from Backend import State
from Config import Config
from Log import Log
from TranslateMessages import TranslateMessages
from ErrorDetector import ErrorDetector
import CustomMessages

class Control():

	def __init__(self, app):

		# create log writer
		self.log = Log("log.txt")
		# create config
		self.config = Config()
		# create message translator
		self.msg_translator = TranslateMessages()
		# create error detector
		self.error_detector = ErrorDetector()
		# execute server for receiving messages from gstreamer pipeline
		self.start_server(1600)

		# create parameters which should be stored in control
		# currently received prog list with all received streams
		self.currentProgList = []
		# analyzed prog list with all analyzed streams
		self.analyzedProgList = self.config.load_prog_list()
		self.analysisSettings = []
		self.dumpSettings = []
		self.language = ""
		self.color_theme = ""
		# parameters of current results page
		self.progTableVisible = True
		# parameters of plot page
		# parameters of all results page

		self.backend = Backend(streams=1)
		self.gui = MainWindow(app)
		# self.usb = Usb()

		# connect to gui signals
		self.gui.connect(CustomMessages.NEW_SETTINS_PROG_LIST, self.on_new_prog_settings_from_gui)
		self.gui.connect(CustomMessages.ACTION_START_ANALYSIS, self.on_start_from_gui)
		self.gui.connect(CustomMessages.ACTION_STOP_ANALYSIS, self.on_stop_from_gui)
		self.gui.connect(CustomMessages.VOLUME_CHANGED, self.on_volume_changed)
		# connect to usb signals
		# --

		# start analysis on app startup
		self.start_analysis()

		# set gui for analyzed programs
		self.apply_prog_list_to_gui(self.analyzedProgList)

		# initially set drawing black background for corresponding renderers to True
		for stream in self.analyzedProgList:
			self.gui.set_draw_mode_for_renderers(True, stream[0])

		self.gui.queue_draw()

	def start_analysis(self):
		# execute all gstreamer pipelines
		self.backend.start_all_pipelines()
		self.gui.toolbar.change_start_icon()

	def stop_analysis(self):
		# execute all gstreamer pipelines
		self.backend.terminate_all_pipelines()
		self.gui.toolbar.change_start_icon()
		self.gui.clear_all_programs_in_prog_dlg()

		# set drawing black background for all renderers to True
		for stream in self.analyzedProgList:
			self.gui.set_draw_mode_for_renderers(True, stream[0])
		# force redrawing of gui
		self.gui.queue_draw()

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
				# convert program string from pipeline to program list (array)
				progList = self.msg_translator.translate_prog_string_to_prog_list(wstr[1:])

				# add received progList to common prog list
				self.currentProgList = self.msg_translator.append_prog_list_to_common(progList, self.currentProgList)

				# show received program list in gui (in program selection dialog)
				self.gui.store.show_prog_list(progList)

				# compare received and current analyzed prog lists
				compared_prog_list = self.msg_translator.translate_prog_list_to_compared_prog_list(self.analyzedProgList, progList)

				# apply compared program list to backend (compared list contains only program equal prorams from current and received lists)
				self.apply_prog_list_to_backend(compared_prog_list)

				# set drawing black background for corresponding renderers to False
				self.gui.set_draw_mode_for_renderers(False, compared_prog_list[0])

			elif wstr[0] == 'v':
				# received video parameters
				#freeze black blockiness av_luma av_diff
				vparams = self.msg_translator.translate_vparams_string_to_list(wstr[1:])
				self.error_detector.set_video_data(vparams)
				self.gui.on_video_measured_data(vparams)

			elif wstr[0] == 'e':
				# received end of stream
				self.on_end_of_stream(int(wstr[1:]))
				print(wstr)

	# make changes in gui according to program list
	def apply_prog_list_to_gui(self, progList):
		# gui only needs program names and ids to redraw - so we need to extract them from program list
		guiProgInfo = self.msg_translator.translate_prog_list_to_gui_prog_info(progList)

		# set gui for new programs from program list
		self.gui.set_new_programs(guiProgInfo)

	# applying prog list to backend
	def apply_prog_list_to_backend(self, progList):
		# to draw video backend needs xid of drawing areas - so we get them from gui
		xids = self.gui.get_renderers_xids()
		# combine prog list with xids
		combinedProgList = self.msg_translator.combine_prog_list_with_xids(progList, xids)

		# apply new settings to backend (settings consist of program list and xids)
		self.backend.apply_new_program_list(combinedProgList)

	# actions when backend send "end of stream" message
	def on_end_of_stream(self, stream_id):
		# refresh program list in gui (in this case, delete this stream from program list in prog select dialog)
		# this is done by passing empty prog list to gui
		self.gui.store.show_prog_list([stream_id, []])

		# getting state of gstreamer pipeline with corresponding stream id
		state = self.backend.get_pipeline_state(stream_id)

		# if current state is RUNNING (this means that pipeline currently decoding some programs)
		# we need to restart this pipeline
		if state is State.RUNNING:
			self.backend.restart_pipeline(stream_id)

		# set drawing black background for corresponding renderers to True
		self.gui.set_draw_mode_for_renderers(True, stream_id)
		# force redrawing of gui
		self.gui.queue_draw()

	# actions when gui send NEW_SETTINS_PROG_LIST message
	def on_new_prog_settings_from_gui(self, param):
		# get program list from gui and store it in control
		self.analyzedProgList = self.gui.get_applied_prog_list()

		# redraw gui according to new program list
		self.apply_prog_list_to_gui(self.analyzedProgList)

		# we need to restart gstreamer pipelines with ids that were selected - so we need to extract these ids from program list
		stream_ids = self.msg_translator.translate_prog_list_to_stream_ids(self.analyzedProgList)

		# restart pipelines with selected ids
		for process_id in stream_ids:
			self.backend.restart_pipeline(process_id)

		# save program list in config
		self.config.save_prog_list(self.analyzedProgList)

	def on_start_from_gui(self, param):
		self.start_analysis()

	def on_stop_from_gui(self, param):
		self.stop_analysis()

	def on_volume_changed(self, param):
		pass

	# when app closes, we need to delete all gstreamer pipelines
	def destroy(self):
		# terminate all gstreamer pipelines
		self.backend.terminate_all_pipelines()
