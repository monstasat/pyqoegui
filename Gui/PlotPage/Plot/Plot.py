from gi.repository import Gtk, Gdk
from Gui.PlotPage.Plot.PlotDrawingArea import PlotDrawingArea
from Gui.PlotPage.Plot.PlotBottomBar import PlotBottomBar
from Gui import Spacing
import numpy as np
from collections import deque
from functools import reduce

# selected progs example
# [[0, '2020', '12 Спас', 3, [['2021', 'video-h264'], ['2022', 'audio-mpeg1']]], [0, '2030', '13 СТС', 3, [['2031', 'video-h264'], ['2032', 'audio-mpeg1']]]]

# measured data example
#
#[	[0, 2040, 2041],
#	[	[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
#		[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
#		[1.012457, 1.015967, 1.019858, 1.016469, 1.021836, 1.014565, 1.017597, 1.016618],
#		[98.768616, 99.07489, 98.909363, 98.968193, 98.610985, 98.731422, 98.490211, 98.564255],
#		[0.963773, 1.333854, 1.312551, 1.111461, 0.973235, 0.745173, 0.724185, 0.915919]
#	]
#]

class Plot(Gtk.Box):
	def __init__(self, selected_progs, plot_index):
		Gtk.Box.__init__(self)

		# plot parameters
		# plot type
		self.minor_type = plot_index
		self.major_type = 'video' if plot_index < 5 else 'audio'

		self.progs = []
		for prog in selected_progs:
			prog_info = []
			# stream id
			prog_info.append(prog[0])
			# prog id
			prog_info.append(prog[1])
			for pid in prog[4]:
				if pid[1].split('-')[0] == self.major_type:
					# pid
					prog_info.append(pid[0])
			# convert strings to int
			prog_info = list(map(int, prog_info))
			self.progs.append(prog_info)

		self.buffer = []
		for i in range(len(self.progs)):
			self.buffer.append([])

		# main widget of a plot - box with vertical orientation
		self.set_orientation(Gtk.Orientation.VERTICAL)

		# add plot label at the top
		self.label = Gtk.Label(halign=Gtk.Align.START, hexpand=True, vexpand=False, label="")

		# add plot bottom bar at the bottom
		self.bottom_bar = PlotBottomBar(selected_progs)

		# add drawing area in the middle
		self.da = PlotDrawingArea(self, self.progs, self.bottom_bar.default_colors[0:len(self.progs)])
		self.da.set_hexpand(True)
		self.da.set_vexpand(True)
		self.da.set_halign(Gtk.Align.FILL)
		self.da.set_valign(Gtk.Align.FILL)
		self.da.set_size_request(250, 40)
		self.da.connect('draw', self.da.graph_draw)
		self.da.connect('configure_event', self.da.graph_configure)
		self.da.connect('destroy', self.da.graph_destroy)
		self.da.connect('state-flags-changed', self.da.graph_state_changed)
		self.da.set_events(Gdk.EventMask.EXPOSURE_MASK)

		self.add(self.label)
		self.add(self.da)
		self.add(self.bottom_bar)
		self.set_spacing(Spacing.ROW_SPACING)

	# set graph title
	def set_title(self, text):
		self.label.set_text(text)

	def add_interval(self, width, type, clear_previous=False):
		if clear_previous is True:
			self.da.intervals.clear()
		self.da.add_interval(width, type)

	def set_min_max(self, min, max):
		self.da.set_min_max(min, max)

	def set_y_axis_unit(self, unit):
		self.da.set_y_axis_unit(unit)
		self.bottom_bar.set_unit(unit)

	def on_incoming_data(self, data):
		index = self.progs.index(data[0])
		self.buffer[index].extend(data[1])

	def get_data(self, index):
		print(self.buffer[index])
		if len(self.buffer[index]) is not 0:
			average = reduce(lambda x, y: x + y, self.buffer[index]) / len(self.buffer[index])
		else:
			average = None
		self.buffer[index].clear()
		return average
