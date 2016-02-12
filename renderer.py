#!/usr/bin/python3
from gi.repository import Gtk,Gdk, GdkX11

import constants

#One instance of video renderer (includes renderer window, prog name label, volume button)
class RendererOne(Gtk.Grid):

	def __init__(self, progName):
		Gtk.Grid.__init__(self)

		#should be horizontally expandable and fill all available space
		self.set_hexpand_set(True)
		self.set_hexpand(True)
		self.set_halign(Gtk.Align.FILL)
		self.set_valign(Gtk.Align.FILL)

		#creating renderer window - drawing area
		self.drawarea = Gtk.DrawingArea(hexpand=True, vexpand=True)
		#minimum renderer size (4:3)
		self.drawarea.set_size_request(100,75)
		#setting initial renderer color
		color = Gdk.color_parse("black")
		rgba = Gdk.RGBA.from_color(color)
		self.drawarea.override_background_color(0, rgba)

		#creating volume button at the right edge of a renderer instance
		volbtn = Gtk.VolumeButton(halign=Gtk.Align.END)

		#creating a program label
		progname = Gtk.Label(label=progName, halign=Gtk.Align.END)

		#attach elements to grid
		self.attach(self.drawarea, 0, 0, 2, 1)
		self.attach(progname, 0, 1, 1, 1)
		self.attach(volbtn, 1, 1, 1, 1)

	def get_drawing_area_xid(self):
		return self.drawarea.get_property('window').get_xid()

#A grid of video renderers
class Renderer(Gtk.FlowBox):
	def __init__(self):
		Gtk.FlowBox.__init__(self)

		##should be horizontally expandable and fill all available space
		self.set_hexpand(True)
		self.set_halign(Gtk.Align.FILL)
		self.set_valign(Gtk.Align.FILL)

		#set selection mode to None
		self.set_selection_mode(Gtk.SelectionMode.NONE)

		#set rows and cols homogeneous
		self.set_homogeneous(True)

		#flow box should have horizontal orientation
		self.set_orientation(Gtk.Orientation.HORIZONTAL)

		#set some space between renderers
		self.set_column_spacing(constants.DEF_COL_SPACING)
		self.set_row_spacing(constants.DEF_ROW_SPACING)

	#draw necessary number of renderers
	def draw_renderers(self, progNum, progNames):

		#first of all delete all previous renderers
		self.remove_renderers()

     	#set max children per line
		if progNum > 3:
			if(progNum%2):
				max_ch = progNum/2 + 1
			else:
				max_ch = progNum/2
		else:
			max_ch = progNum
		self.set_max_children_per_line(max_ch)
		self.set_min_children_per_line(5)

		#add number of renderers
		for i in range(progNum):
			#each renderer is placed into aspect frame widget (4:3)
			af = Gtk.AspectFrame()
			af.set(0.5, 0.5, 4/3, False)
			af.add(RendererOne(progNames[i]))
			#insert renderer to flow box
			self.insert(af, -1)

		#show all renderers
		self.show_all()

		print("renderers added: " + str(progNum))

  	#delete all renderers
	def remove_renderers(self):
		children = self.get_children()
		for child in children:
			child.destroy()

	def get_renderers_xid(self):
		xids = []
		for child in self.get_children():
			xids.append(child.get_children()[0].get_children()[0].get_drawing_area_xid())
		return xids
