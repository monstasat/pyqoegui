#!/usr/bin/python3
from gi.repository import Gtk,Gdk

import constants

class RendererOne():

	def __init__(self):
		pass

	def create_renderer(self, index):
		grid = Gtk.Grid()
		grid.set_hexpand_set(True)
		grid.set_hexpand(True)
		grid.set_halign(Gtk.Align.FILL)
		grid.set_valign(Gtk.Align.FILL)


		drawarea = Gtk.DrawingArea()
		drawarea.set_size_request(200,200)
		drawarea.set_hexpand(True)
		drawarea.set_vexpand(True)
		color = Gdk.color_parse("black")
		rgba = Gdk.RGBA.from_color(color)
		drawarea.override_background_color(0, rgba)
		volbtn = Gtk.VolumeButton()
		volbtn.set_halign(Gtk.Align.END)
		progname = Gtk.Label(label=constants.prog_names[index])
		progname.set_halign(Gtk.Align.END)
		grid.attach(drawarea, 0, 0, 2, 1)
		grid.attach(progname, 0, 1, 1, 1)
		grid.attach(volbtn, 1, 1, 1, 1)
		return grid

class Renderer:
	def __init__(self):
		pass

	def create_renderer(self):
		grid = Gtk.Grid()
		grid.set_hexpand_set(True)
		grid.set_hexpand(True)
		grid.set_halign(Gtk.Align.FILL)
		grid.set_valign(Gtk.Align.FILL)
		grid.set_column_spacing(constants.DEF_SPACING)

		for i in range(5):
			rend = RendererOne()
			grid.attach(rend.create_renderer(i), i, 0, 1, 1)

		for i in range(5):
			rend = RendererOne()
			grid.attach(rend.create_renderer(i+5), i, 1, 1, 1)

		return grid
