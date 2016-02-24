from gi import require_version
require_version('PangoCairo', '1.0')
from gi.repository import Gtk, Gdk, cairo, Pango, PangoCairo, GObject
import math
import random
import collections
from Gui.PlotPage.Plot import GraphTypes

NUM_POINTS = 60 + 2
FRAME_WIDTH = 4

class Interval():
	def __init__(self, height, type, color):
		self.height = height
		self.type = type
		self.color = color


class PlotDrawingArea(Gtk.DrawingArea):

	def __init__(self):

		Gtk.DrawingArea.__init__(self)
		# plot type
		self.type = 0
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
		# graph refresh speed (1 sec by default)
		self.speed = 1000
		self.frames_per_unit = 10
		# flag that permits graph drawing
		self.draw = True
		# index of update timer callback
		self.timer_index = None
		self.render_counter = self.frames_per_unit - 1
		# background surface
		self.background = None
		# data array
		self.data = collections.deque([-1.0]*NUM_POINTS, NUM_POINTS)

		self.min = 0
		self.max = 100

		self.y_type = ""

		# start refreshing loop
		self.timer_index = GObject.timeout_add(self.speed/self.frames_per_unit, self.graph_update, None)

		self.intervals = []

	def set_min_max(self, min, max):
		self.min = min
		self.max = max

	def set_y_type(self, text):
		self.y_type = text
		self.clear_background()

	# start plotting
	def graph_start(self):
		# if timer is not already set
		if self.timer_index is None:
			self.graph_update()
			self.timer_index = GObject.timeout_add(self.speed / self.frames_per_unit, self.update, None)
		# enable drawing
		self.draw = True

	def graph_queue_draw(self):
		self.queue_draw()

	def clear_background(self):
		if self.background is not None:
			#self.background.destroy()
			self.background = None

	def graph_destroy(self, data):
		if self.timer_index is not None:
			GObject.source_remove(self.timer_index)

		self.clear_background()

	def graph_state_changed(self, flags, data):
		self.clear_background()
		self.graph_queue_draw()

	# stop plotting
	def graph_stop(self):
		# do not draw anymore, but continue to poll
		self.draw = False

	# change refresh speed
	def change_speed(self, new_speed):
		self.speed = new_speed
		if selt.timer_index != None:
			GObject.source_remove(self.timer_index)
			self.timer_index = GObject.timeout_add(self.speed / self.frames_per_unit. self.update, None)

		self.clear_background()

	# update plot
	def graph_update(self, data):

		if self.render_counter == self.frames_per_unit - 1:
			#print("\ndeque before rotating: " + str(self.data))
			self.data.rotate(NUM_POINTS-1)
			#print("\ndeque after rotating: " + str(self.data))
			self.data[0] = random.uniform(0.4, 0.6)
			#print("\ndeque after adding element: " + str(self.data))

		if self.draw is True:
			self.graph_queue_draw()

		self.render_counter += 1
		if self.render_counter >= self.frames_per_unit:
			self.render_counter = 0
		return True

	def graph_draw(self, widget, cr):
		i = 0
		j = 0
		sample_width = 0.0
		x_offset = 0.0

		# number of pixels wide for one graph point
		sample_width = float(self.draw_width - self.rmargin - self.indent) / float(NUM_POINTS)
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
		cr.rectangle(self.indent + FRAME_WIDTH + 1, FRAME_WIDTH - 1, self.draw_width - self.rmargin - self.indent - 1, self.real_draw_height + FRAME_WIDTH - 1)
		cr.clip()

		# for
		cr.set_source_rgba(0, 0.2, 1.0, 1)
		cr.move_to(x_offset, (1.0 - self.data[-1]) * self.real_draw_height + 3.5)
		for i in range(NUM_POINTS-1):
			cr.curve_to(x_offset - ((i - 0.5) * self.graph_delx),
                            (1.0 - self.data[-1 - i]) * self.real_draw_height + 3.5,
                            x_offset - ((i - 0.5) * self.graph_delx),
                            (1.0 - self.data[-1 - i - 1]) * self.real_draw_height + 3.5,
                            x_offset - (i * self.graph_delx),
                            (1.0 - self.data[-1 - i - 1]) * self.real_draw_height + 3.5)
		cr.stroke()

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
			self.line_width = 3
		elif k == 5 or k == 6:
			self.num_bars = 5
			self.line_width = 3
		else:
			self.num_bars = 10
			self.line_width = 4

	def add_interval(self, height, cur_type):
		# set color
		color = ()
		if cur_type == GraphTypes.ERROR:
			color = (1.0, 0.0, 0.0)
		elif cur_type == GraphTypes.WARNING:
			color = (1.0, 1.0, 0.0)
		else:
			color = (0.0, 1.0, 0.0)

		interval = Interval(height=height, color=color, type=cur_type)
		self.intervals.append(interval)

	# draw plot background (background, grids and labels)
	def draw_background(self):
		#self.graph_configure()
		self.get_num_bars()
		self.graph_dely = (self.draw_height - 20) / self.num_bars
		self.real_draw_height = self.graph_dely * self.num_bars
		self.graph_delx = (self.draw_width - 2.0 - self.indent) / (NUM_POINTS - 3)
		self.graph_buffer_offset = int((1.5 * self.graph_delx) + FRAME_WIDTH)

		cr = self.get_window().cairo_create()

		styleContext = self.get_parent().get_parent().get_style_context()

		fg = styleContext.get_color(Gtk.StateType.NORMAL)

		cr.paint_with_alpha(0.0)
		layout = PangoCairo.create_layout(cr)
		font_desc = styleContext.get_font(Gtk.StateType.NORMAL)
		font_desc.set_size(0.8 *  self.fontsize * Pango.SCALE)
		layout.set_font_description(font_desc)

		# draw frame
		cr.translate(FRAME_WIDTH, FRAME_WIDTH)

		width = self.draw_width - self.rmargin - self.indent
		y = 0
		for interval in self.intervals:
			cr.set_source_rgba(interval.color[0], interval.color[1], interval.color[2], 0.5)
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
			string = '%d' + self.y_type
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

			total_seconds = int(self.speed * (NUM_POINTS - 2) / 1000)

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


	# configure the graph
	def graph_configure(self, event, data):
		rect = self.get_allocation()
		self.draw_width = rect.width
		self.draw_height = rect.height

		self.clear_background()
		self.graph_queue_draw()
