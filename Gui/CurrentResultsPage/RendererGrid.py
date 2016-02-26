from gi import require_version
require_version('GdkX11', '3.0')
from gi.repository import Gtk,Gdk, GdkX11
from Gui import Spacing
import cairo
import math

# one instance of video renderer (includes renderer window, prog name label, volume button)
class Renderer(Gtk.Grid):

	def __init__(self, guiProgInfo):
		Gtk.Grid.__init__(self)

		self.is_fullscreen = False

		self.background = None

		self.stream_id = guiProgInfo[0]
		# program id from PMT
		self.progID = guiProgInfo[1]
		# program name from SDT
		self.progName = guiProgInfo[2]

		# should be horizontally expandable and fill all available space
		self.set_hexpand_set(True)
		self.set_hexpand(True)
		self.set_halign(Gtk.Align.FILL)
		self.set_valign(Gtk.Align.FILL)


		# creating renderer window - drawing area
		self.drawarea = Gtk.DrawingArea(hexpand=True, vexpand=True)
		self.drawarea.set_events(Gdk.EventMask.EXPOSURE_MASK)
		self.drawarea.set_app_paintable(False)
		# set default renderer size (4:3)
		self.drawarea.set_size_request(100,75)
		# this is to remove flickering
		self.drawarea.set_double_buffered(False)
		# connect 'draw' event with callback
		self.drawarea.connect("draw", self.on_drawingarea_draw)
		self.drawarea.connect('configure_event', self.da_configure)
		self.drawarea.connect('state-flags-changed', self.da_state_changed)
		# do we need to draw black background?
		self.draw = False
		self.no_video = False

		screen = self.drawarea.get_screen()
		visual = screen.get_system_visual()
		if visual != None:
			self.drawarea.set_visual(visual)

		# creating volume button at the right edge of a renderer instance
		volbtn = Gtk.VolumeButton(halign=Gtk.Align.END, hexpand=False, vexpand=False)
		volbtn.connect('value-changed', self.volume_changed)

		# creating a program label
		progname = Gtk.Label(label=self.progName, halign=Gtk.Align.END, hexpand=False, vexpand=False)

		# attach elements to grid
		self.attach(self.drawarea, 0, 0, 2, 1)
		self.attach(progname, 0, 1, 1, 1)
		self.attach(volbtn, 1, 1, 1, 1)

	def volume_changed(self, widget, value):
		pass

	def clear_background(self):
		if self.background is not None:
			self.background = None

	# return xid for the drawing area
	def get_drawing_area_xid(self):
		return self.drawarea.get_window().get_xid()

	def da_configure(self, event, data):
		self.clear_background()
		self.drawarea.queue_draw()

	def da_state_changed(self, flags, data):
		self.clear_background()
		self.drawarea.queue_draw()

	def on_drawingarea_draw(self, widget, cr):
		# if it is the first time we are drawing
		if self.draw is True:
			#if self.background is None:
			cr.set_source_rgb(0, 0, 0)
			w = self.drawarea.get_allocated_width()
			h = self.drawarea.get_allocated_height()
			cr.rectangle(0, 0, w, h)
			cr.fill()
			self.background = cr.get_target()
			#print("draw" + str(self.cnt))
			#self.cnt += 1

# a grid of video renderers
class RendererGrid(Gtk.FlowBox):
	def __init__(self):
		Gtk.FlowBox.__init__(self)

		self.rend_arr = []

		# should be horizontally expandable and fill all available space
		self.set_hexpand(True)
		self.set_vexpand(True)
		self.set_halign(Gtk.Align.FILL)
		self.set_valign(Gtk.Align.FILL)

		# set selection mode to None
		self.set_selection_mode(Gtk.SelectionMode.NONE)

		# set rows and cols homogeneous
		self.set_homogeneous(True)

		# flow box should have horizontal orientation
		self.set_orientation(Gtk.Orientation.HORIZONTAL)

		# set some space between renderers
		self.set_column_spacing(Spacing.COL_SPACING)
		self.set_row_spacing(Spacing.ROW_SPACING)

		self.set_activate_on_single_click(False)

		# connect to draw signal
		self.connect('draw', self.on_draw)
		# connect to child activated signal
		self.connect('child-activated', self.on_child_activated)

	# draw necessary number of renderers
	def draw_renderers(self, progNum, guiProgInfo):

		# first of all delete all previous renderers
		self.remove_renderers()

     	# set max children per line
		if progNum > 3:
			if(progNum%2):
				max_ch = progNum/2 + 1
			else:
				max_ch = progNum/2
		else:
			max_ch = progNum
		self.set_max_children_per_line(max_ch)

		self.rend_arr.clear()
		# add number of renderers
		for i in range(progNum):
			self.rend_arr.append(Renderer(guiProgInfo[i]))
			af = Gtk.AspectFrame(hexpand=True, vexpand=True)
			af.set(0.5, 0.5, 4.0/3.0, False)
			af.add(self.rend_arr[i])
			# insert renderer to flow box
			self.insert(af, -1)

		# show all renderers
		self.show_all()

  	# delete all renderers
	def remove_renderers(self):
		children = self.get_children()
		for child in children:
			child.destroy()
		self.rend_arr.clear()

	# returns array of drawing area xids
	def get_renderers_xid(self):
		xids = []
		for i in range(len(self.get_children())):
			rend = self.rend_arr[i]
			rend.drawarea.realize()
			xids.append([rend.stream_id, rend.progID, rend.drawarea.get_window().get_xid()])
		return xids

	def set_draw_mode_for_renderers(self, draw, stream_id):
		for i in range(len(self.get_children())):
			if self.rend_arr[i].stream_id == stream_id:
				self.rend_arr[i].draw = draw

	def on_draw(self, widget, cr):
		self.on_resize()

	def filter_func(self, child, user_data):
		index = child.get_index()
		return self.rend_arr[index].is_fullscreen

	def on_child_activated(self, widget, child):
		index = child.get_index()
		if self.rend_arr[index].is_fullscreen is True:
			self.rend_arr[index].is_fullscreen = False
			self.set_filter_func((lambda x, y: True), None)
		else:
			self.rend_arr[index].is_fullscreen = True
			self.set_filter_func(self.filter_func, None)

	def on_resize(self):
		rect = self.get_allocation()
		aspect_fb = rect.height / rect.width
		is_fullscreen = False
		for child in self.rend_arr:
			if child.is_fullscreen is True:
				is_fullscreen = True
		children = self.get_children()
		if is_fullscreen is True:
			cols = 1
		else:
			cols = self.get_max_renderers_per_row(aspect_fb, 3.0/4, len(children))
		self.set_max_children_per_line(cols)

	def get_max_renderers_per_row(self, flow_box_div, rend_div, rend_num):
		W = 1.0;
		H = W * flow_box_div;

		aspect_list = []

		for rows in range(1, rend_num + 1):
			columns = math.ceil(rend_num / float(rows))
			S_1 = 0.0

			if (W / columns * rend_div * rows) <= H:
				S_1 = W / columns * (W / columns * rend_div)
			else:
				S_1 = H / rows * (H / rows / rend_div)

			S_useful = S_1 * rend_num;
			S_rects = S_1 * rows * columns;
			space_rate = S_useful / S_rects

			aspect_list.append([rows, columns, S_useful, S_rects, space_rate])

		# sort by s_useful and space rate
		sorted_al = sorted(aspect_list, key=lambda x: (x[2], x[4]))

		if len(sorted_al) > 0:
			return sorted_al[-1][1]
		else:
			return 0
