from gi import require_version
require_version('GdkX11', '3.0')
from gi.repository import Gtk,Gdk, GdkX11
from Gui import Spacing
import cairo

# one instance of video renderer (includes renderer window, prog name label, volume button)
class Renderer(Gtk.Grid):

	def __init__(self, progName):
		Gtk.Grid.__init__(self)

		# should be horizontally expandable and fill all available space
		self.set_hexpand_set(True)
		self.set_hexpand(True)
		self.set_halign(Gtk.Align.FILL)
		self.set_valign(Gtk.Align.FILL)

		# creating renderer window - drawing area
		self.drawarea = Gtk.DrawingArea(hexpand=True, vexpand=True)
		# minimum renderer size (4:3)
		self.drawarea.set_size_request(100,75)
		# this is to remove flickering
		self.drawarea.set_double_buffered(False)
		# connect 'draw' event with callback
		self.drawarea.connect("draw", self.on_drawingarea_draw)
		# we need to draw only once - black background
		self.drawn = False
		#self.drawarea.modify_bg(0, Gdk.color_parse("black"))

		screen = self.drawarea.get_screen()
		visual = screen.get_system_visual()
		if visual != None:
			self.drawarea.set_visual(visual)

		# creating volume button at the right edge of a renderer instance
		volbtn = Gtk.VolumeButton(halign=Gtk.Align.END, hexpand=False, vexpand=False)

		# creating a program label
		progname = Gtk.Label(label=progName, halign=Gtk.Align.END, hexpand=False, vexpand=False)

		# attach elements to grid
		self.attach(self.drawarea, 0, 0, 2, 1)
		self.attach(progname, 0, 1, 1, 1)
		self.attach(volbtn, 1, 1, 1, 1)

	# return xid for the drawing area
	def get_drawing_area_xid(self):
		return self.drawarea.get_window().get_xid()

	def on_drawingarea_draw(self, widget, cr):
		# if it is the first time we are drawing
		if self.drawn is False:
			cr.set_source_rgb(0, 0, 0)
			cr.rectangle(0, 0, self.drawarea.get_allocated_width(), self.drawarea.get_allocated_height())
			cr.fill()
			self.drawn = True

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

	# draw necessary number of renderers
	def draw_renderers(self, progNum, progNames):

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
			self.rend_arr.append(Renderer(progNames[i]))
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
			xids.append(self.rend_arr[i].drawarea.get_window().get_xid())
		return xids
