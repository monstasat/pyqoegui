#!/usr/bin/python3
from gi.repository import Gtk,Gdk

import constants

#One instance of video renderer (includes renderer window, prog name label, volume button)
class RendererOne(Gtk.Grid):

	def __init__(self, index):
		Gtk.Grid.__init__(self)

		#should be horizontally expandable and fill all available space
		self.set_hexpand_set(True)
		self.set_hexpand(True)
		self.set_halign(Gtk.Align.FILL)
		self.set_valign(Gtk.Align.FILL)

		#creating renderer window - drawing area
		drawarea = Gtk.DrawingArea()
		#minimum renderer size (4:3)
		drawarea.set_size_request(100,75)
		#horizontally and vertically expandable - should fill all free area of the grid
		drawarea.set_hexpand(True)
		drawarea.set_vexpand(True)
		#setting initial renderer color
		color = Gdk.color_parse("black")
		rgba = Gdk.RGBA.from_color(color)
		drawarea.override_background_color(0, rgba)

		#creating volume button
		volbtn = Gtk.VolumeButton()
		#place at the right edge of a renderer instance
		volbtn.set_halign(Gtk.Align.END)

		#creating a program label
		progname = Gtk.Label(label=constants.prog_names[index])
		progname.set_halign(Gtk.Align.END)

		#attach elements to grid
		self.attach(drawarea, 0, 0, 2, 1)
		self.attach(progname, 0, 1, 1, 1)
		self.attach(volbtn, 1, 1, 1, 1)

#A grid of video renderers
class Renderer(Gtk.FlowBox):
	def __init__(self, progNum):
		Gtk.FlowBox.__init__(self)

		##should be horizontally expandable and fill all available space
		self.set_hexpand_set(True)
		self.set_hexpand(True)
		self.set_halign(Gtk.Align.FILL)
		self.set_valign(Gtk.Align.FILL)

		#set selection mode to None
		self.set_selection_mode(0)

		#set rows and cols homogeneous
		self.set_homogeneous(True)

		self.set_orientation(Gtk.Orientation.HORIZONTAL)

		#set some space between renderers
		self.set_column_spacing(constants.DEF_COL_SPACING)
		self.set_row_spacing(constants.DEF_ROW_SPACING)

		#add renderers
		self.draw_renderers(progNum)

	#draw necessary number of renderers
	def draw_renderers(self, progNum):
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
		renderers = []
		for i in range(progNum):
			af = Gtk.AspectFrame()
			af.set(0.5, 0.5, 4/3, False)
			renderers.append(RendererOne(i))
			af.add(renderers[i])
			self.insert(af, -1)
		self.show_all()
		print("renderers added: " + str(progNum))

  	#delete all renderers
	def remove_renderers(self):
		children = self.get_children()
		for child in children:
			child.destroy()
