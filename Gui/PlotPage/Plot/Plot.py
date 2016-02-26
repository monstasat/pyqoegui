from gi import require_version
require_version('PangoCairo', '1.0')
from gi.repository import Gtk, Gdk, cairo, Pango, PangoCairo, GObject
from Gui.PlotPage.Plot.PlotBottomBar import PlotBottomBar
from Gui.PlotPage.Plot import GraphTypes
from Gui import Spacing
from collections import deque
from functools import reduce
import math

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

class Interval():
	def __init__(self, height, type, color):
		self.height = height
		self.type = type
		self.color = color

class Plot(Gtk.Box):
	def __init__(self, selected_progs, plot_index):
		Gtk.Box.__init__(self)

		# main widget of a plot - box with vertical orientation
		self.set_orientation(Gtk.Orientation.VERTICAL)

		# add plot label at the top
		self.label = Gtk.Label(halign=Gtk.Align.END, hexpand=True, vexpand=False, label="")

		# add drawing area in the middle
		self.da = Gtk.DrawingArea()
		self.da.set_hexpand(True)
		self.da.set_vexpand(True)
		self.da.set_halign(Gtk.Align.FILL)
		self.da.set_valign(Gtk.Align.FILL)
		self.da.set_size_request(250, 40)
		# connect drawing area to some signals
		self.da.connect('draw', self.graph_draw)
		self.da.connect('configure_event', self.graph_configure)
		self.da.connect('destroy', self.graph_destroy)
		self.da.connect('state-flags-changed', self.graph_state_changed)
		self.da.set_events(Gdk.EventMask.EXPOSURE_MASK)

		# add plot bottom bar at the bottom
		self.bottom_bar = PlotBottomBar(selected_progs)

		self.add(self.label)
		self.add(self.da)
		self.add(self.bottom_bar)
		self.set_spacing(Spacing.ROW_SPACING)

		# graph points number
		self.NUM_POINTS = 160 + 2
		# width of graph frame
		self.FRAME_WIDTH = 4

		# plot parameters
		# plot type
		self.minor_type = plot_index
		self.major_type = 'video' if plot_index < 5 else 'audio'

		# progs displayed on graph. needed for mapping data to corresponding plot line
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

		# buffers for storing input data before it is shown on graph
		self.buffer = []
		for i in range(len(self.progs)):
			self.buffer.append([])

		# drawing area parameters
		# draw area width
		self.draw_width = 0
		# draw area height
		self.draw_height = 0
		# number of horizontal bars
		self.num_bars = 1
		self.graph_dely = 0
		self.real_draw_height = 0
		self.graph_delx = 0
		self.graph_buffer_offset = 0
		# offset from left border
		self.indent = 24
		# graph font size
		self.fontsize = 8
		# offset from right border
		self.rmargin = 7 * self.fontsize
		# line width
		self.line_width = 1
		# background surface
		self.background = None
		# flag that permits graph drawing
		self.draw = True
		# graph range
		self.min = 0
		self.max = 100
		# y axis unit
		self.unit = ""
		# background intervals
		self.intervals = []

		# graph refresh speed (1 sec by default) and other refresh parameters
		self.speed = 250
		self.frames_per_unit = 10
		self.render_counter = self.frames_per_unit - 1
		# index of refresh timer callback
		self.timer_index = None
		# start refreshing loop
		self.timer_index = GObject.timeout_add(self.speed/self.frames_per_unit, self.graph_update, None)

		# number of displayed programs
		self.prog_num = len(self.progs)
		# data storage for analyzed programs
		self.data = []
		for i in range(self.prog_num):
			self.data.append(deque([-1.0] * self.NUM_POINTS, self.NUM_POINTS))

	# set graph title
	def set_title(self, text):
		self.label.set_text(text)

	# add interval to plot
	def add_interval(self, height, type, clear_previous=False):
		if clear_previous is True:
			self.intervals.clear()

		# set color
		if type == GraphTypes.ERROR:
			color = (1.0, 0.0, 0.0)
		elif type == GraphTypes.WARNING:
			color = (1.0, 1.0, 0.0)
		else:
			color = (0.0, 1.0, 0.0)

		# append interval to list
		self.intervals.append(Interval(height=height, color=color, type=type))

	# set minimum and maximum values of plot y axis
	def set_min_max(self, min, max):
		self.min = min
		self.max = max
		self.clear_background()

	# set unit for plot y axis
	def set_y_axis_unit(self, unit):
		if unit == '%':
			self.unit = '%%'
		else:
			self.unit = unit
		self.clear_background()
		self.bottom_bar.set_unit(unit)

	# change plot refresh speed
	def change_speed(self, new_speed):
		self.speed = new_speed
		if selt.timer_index != None:
			GObject.source_remove(self.timer_index)
			self.timer_index = GObject.timeout_add(self.speed / self.frames_per_unit. self.update, None)

		self.clear_background()

	# force graph redraw
	def graph_queue_draw(self):
		self.da.queue_draw()

	# invalidate graph background
	def clear_background(self):
		if self.background is not None:
			#self.background.destroy()
			self.background = None

	# start plotting
	def graph_start(self):
		# if timer is not already set
		if self.timer_index is None:
			self.graph_update()
			self.timer_index = GObject.timeout_add(self.speed / self.frames_per_unit, self.update, None)
		# enable drawing
		self.draw = True

	# stop plotting
	def graph_stop(self):
		# do not draw anymore, but continue to poll
		self.draw = False

	# when graph is to be destroyed
	def graph_destroy(self, data):
		if self.timer_index is not None:
			GObject.source_remove(self.timer_index)
		self.clear_background()

	# if graph state was changed
	def graph_state_changed(self, flags, data):
		self.clear_background()
		self.graph_queue_draw()

	# configure event was received
	def graph_configure(self, event, data):
		rect = self.da.get_allocation()
		self.draw_width = rect.width
		self.draw_height = rect.height

		self.clear_background()
		self.graph_queue_draw()


	# draw on graph
	def graph_draw(self, widget, cr):
		i = 0
		j = 0
		sample_width = 0.0
		x_offset = 0.0

		# number of pixels wide for one graph point
		sample_width = float(self.draw_width - self.rmargin - self.indent) / float(self.NUM_POINTS)
		# general offset
		x_offset = self.draw_width - self.rmargin
		# subframe offset
		x_offset += self.rmargin - ((sample_width / self.frames_per_unit) * self.render_counter)

		# draw the graph
		#if self.background is None:
		self.draw_background()

		cr.set_source_surface(self.background)
		cr.paint()

		cr.set_line_width(self.line_width)
		# 0 - butt, 1 - round, 2 - square
		#cr.set_line_cap(1)
		#cr.set_line_join(1)
		cr.rectangle(self.indent + self.FRAME_WIDTH + 1, self.FRAME_WIDTH - 1, self.draw_width - self.rmargin - self.indent - 1, self.real_draw_height + self.FRAME_WIDTH - 1)
		cr.clip()

		for i in range(self.prog_num):
			data = self.data[i]
			Gdk.cairo_set_source_rgba(cr, self.bottom_bar.colors[i])
			#cr.set_source_rgba(0, 0.2, 1.0, 1)
			cr.move_to(x_offset, (1.0 - data[-1]) * self.real_draw_height + 3.5)
			for i in range(self.NUM_POINTS-1):
				cr.curve_to(x_offset - ((i - 0.5) * self.graph_delx),
                            (1.0 - data[-1 - i]) * self.real_draw_height + 3.5,
                            x_offset - ((i - 0.5) * self.graph_delx),
                            (1.0 - data[-1 - i - 1]) * self.real_draw_height + 3.5,
                            x_offset - (i * self.graph_delx),
                            (1.0 - data[-1 - i - 1]) * self.real_draw_height + 3.5)
			cr.stroke()

	# draw plot background (background, grids and labels)
	def draw_background(self):
		#self.graph_configure()
		self.get_num_bars()
		self.graph_dely = (self.draw_height - 20) / self.num_bars
		self.real_draw_height = self.graph_dely * self.num_bars
		self.graph_delx = (self.draw_width - 2.0 - self.indent) / (self.NUM_POINTS - 3)
		self.graph_buffer_offset = int((1.5 * self.graph_delx) + self.FRAME_WIDTH)

		#rect = self.da.get_allocation()
		#surface = self.da.get_window().create_similar_surface(cairo.Content.COLOR_ALPHA, rect.width, rect.height)
		cr = self.da.get_window().cairo_create()

		styleContext = self.get_parent().get_style_context()

		fg = styleContext.get_color(Gtk.StateType.NORMAL)

		cr.paint_with_alpha(0.0)
		layout = PangoCairo.create_layout(cr)
		font_desc = styleContext.get_font(Gtk.StateType.NORMAL)
		font_desc.set_size(0.8 *  self.fontsize * Pango.SCALE)
		layout.set_font_description(font_desc)

		# draw frame
		cr.translate(self.FRAME_WIDTH, self.FRAME_WIDTH)

		width = self.draw_width - self.rmargin - self.indent
		y = 0
		for interval in self.intervals:
			cr.set_source_rgba(interval.color[0], interval.color[1], interval.color[2], 0.5)
			cr.set_source_rgba(1, 1, 1, 0.5)
			interval_height = interval.height * self.real_draw_height
			cr.rectangle(self.indent, y, width, interval_height)
			y += interval_height
			cr.fill()

		cr.set_line_width(1.0)
		cr.set_source_rgb(0.89, 0.89, 0.89)

		for i in range(self.num_bars + 1):
			y = 0.0
			if i == 0:
				y = 0.5 + self.fontsize / 2.0
			elif i == self.num_bars:
				y = i * self.graph_dely + 0.5
			else:
				y = i * self.graph_dely + self.fontsize / 2.0

			string = ""
			#if i == 0:
			string = '%d' + self.unit
			#else:
			#	string = '%d'
			cr.set_source_rgba(fg.red, fg.green, fg.blue, fg.alpha)
			caption = string%(self.max - i * ((self.max - self.min) / self.num_bars))

			layout.set_alignment(Pango.Alignment.LEFT)
			layout.set_text(caption, -1)
			extents = layout.get_extents()
			cr.move_to(self.draw_width - self.indent - 23, y - 1.0 * extents[1].height / Pango.SCALE / 2)

			PangoCairo.show_layout(cr, layout)

			if i == 0 or i == self.num_bars:
				cr.set_source_rgb(0.70, 0.71, 0.70)
			else:
				cr.set_source_rgb(0.89, 0.89, 0.89)

			cr.move_to(self.indent, i * self.graph_dely + 0.5)
			cr.line_to(self.draw_width - self.rmargin + 0.5 + 4, i * self.graph_dely + 0.5)
			cr.stroke()

			total_seconds = int(self.speed * (self.NUM_POINTS - 2) / 1000)

		for i in range(7):
			x = i * (self.draw_width - self.rmargin - self.indent) / 6
			if i == 0 or i == 6:
				cr.set_source_rgb(0.70, 0.71, 0.70)
			else:
				cr.set_source_rgb(0.89, 0.89, 0.89)

			cr.move_to((math.ceil(x) + 0.5) + self.indent, 0.5)
			cr.line_to((math.ceil(x) + 0.5) + self.indent, self.real_draw_height + 4.5)
			cr.stroke()

			seconds = total_seconds - i * total_seconds / 6

			if i == 0:
				format = "%u секунд"
			else:
				format = "%u"

			caption = format%seconds
			layout.set_text(caption, -1)
			extents = layout.get_extents()
			cr.move_to((math.ceil(x) + 0.5 + self.indent) - (1.0 * extents[1].width / Pango.SCALE / 2),
						self.draw_height - 1.15 * extents[1].height / Pango.SCALE)

			cr.set_source_rgba(fg.red, fg.green, fg.blue, fg.alpha)
			PangoCairo.show_layout(cr, layout)

		cr.stroke()

		# remember surface
		self.background = cr.get_target()

	# update plot
	def graph_update(self, data):

		for i in range(self.prog_num):
			if self.render_counter == self.frames_per_unit - 1:
				data = self.get_data(i)
				if data is None:
					data = self.data[i][0] * self.max
				#print("\ndeque before rotating: " + str(self.data))
				self.data[i].rotate(self.NUM_POINTS-1)
				#print("\ndeque after rotating: " + str(self.data))
				self.data[i][0] = data / self.max#random.uniform(0.4, 0.6)
				#print("\ndeque after adding element: " + str(self.data))
				self.bottom_bar.set_value(data, i)

		if self.draw is True:
			self.graph_queue_draw()


		self.render_counter += 1
		if self.render_counter >= self.frames_per_unit:
			self.render_counter = 0
		return True

	# decide number of horizontal bars
	def get_num_bars(self):
		k = int(self.draw_height / (self.fontsize + 14))
		if k == 0 or k == 1:
			self.num_bars = 1
			self.line_width = 1
		elif k == 2 or k == 3:
			self.num_bars = 2
			self.line_width = 2
		elif k == 4:
			self.num_bars = 4
			self.line_width = 2
		elif k == 5 or k == 6:
			self.num_bars = 5
			self.line_width = 2
		else:
			self.num_bars = 10
			self.line_width = 2

	# new data was received
	def on_incoming_data(self, data):
		index = self.progs.index(data[0])
		self.buffer[index].extend(data[1])

	def get_data(self, index):
		#print(self.buffer[index])
		if len(self.buffer[index]) is not 0:
			average = reduce(lambda x, y: x + y, self.buffer[index]) / len(self.buffer[index])
		else:
			average = None
		self.buffer[index].clear()
		return average
