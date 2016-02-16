#!/usr/bin/python3
from gi.repository import Gtk,Gdk, GdkX11

import common

# one instance of video renderer (includes renderer window, prog name label, volume button)
class RendererOne(Gtk.Grid):

	def __init__(self, progName):
		Gtk.Grid.__init__(self)
		print("created renderer one!")
		# should be horizontally expandable and fill all available space
		self.set_hexpand_set(True)
		self.set_hexpand(True)
		self.set_halign(Gtk.Align.FILL)
		self.set_valign(Gtk.Align.FILL)

		# creating renderer window - drawing area
		self.drawarea = Gtk.DrawingArea(hexpand=True, vexpand=True)
		# minimum renderer size (4:3)
		self.drawarea.set_size_request(100,75)
		# setting initial renderer color
		color = Gdk.color_parse("black")
		rgba = Gdk.RGBA.from_color(color)
		#self.drawarea.override_background_color(0, rgba)

		screen = self.drawarea.get_screen()
		visual = screen.get_system_visual()
		if visual != None:
			self.drawarea.set_visual(visual)

		# creating volume button at the right edge of a renderer instance
		volbtn = Gtk.VolumeButton(halign=Gtk.Align.END)

		# creating a program label
		progname = Gtk.Label(label=progName, halign=Gtk.Align.END)

		# attach elements to grid
		self.attach(self.drawarea, 0, 0, 2, 1)
		self.attach(progname, 0, 1, 1, 1)
		self.attach(volbtn, 1, 1, 1, 1)

	# return xid for the drawing area
	def get_drawing_area_xid(self):
		return self.drawarea.get_window().get_xid()

# a grid of video renderers
class Renderer(Gtk.FlowBox):
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
		self.set_column_spacing(common.DEF_COL_SPACING)
		self.set_row_spacing(common.DEF_ROW_SPACING)

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
		#max_ch = 30
		self.set_max_children_per_line(max_ch)
		#self.set_min_children_per_line(5)

		self.rend_arr.clear()
		# add number of renderers
		print(progNum)
		for i in range(progNum):
			# each renderer is placed into aspect frame widget (4:3)
			af = Gtk.AspectFrame(hexpand=True, vexpand=True)
			af.set(0.5, 0.5, 4/3, False)
			self.rend_arr.append(RendererOne(progNames[i]))
			print("renderer №" + str(i) + ": " +  str(self.rend_arr[i]))
			af.add(self.rend_arr[i])
			# insert renderer to flow box
			self.insert(af, -1)

		# show all renderers
		print(self.rend_arr)
		self.show_all()
		for i in range(progNum):
			xid = self.rend_arr[i].drawarea.get_window().get_xid()
			print("renderer: " + str(self.rend_arr[i]) + ", window: " + str(self.rend_arr[i].get_window()) + ", xid: " + str(xid))

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
			print(self.rend_arr[i])
			print(xids[i])
		return xids
