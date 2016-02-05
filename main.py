#!/usr/bin/python3
from gi.repository import Gtk

import constants
import menutoolbar
import progtable
import renderer

class MyWindow(Gtk.Window):

	revealer = Gtk.Revealer()
	def __init__(self):
		Gtk.Window.__init__(self, title="Анализатор АТС-3")
		self.set_default_size(200,200)
		self.set_border_width(constants.DEF_SPACING)

		#creating left side bar with buttons
		BtnToolbarCreator = menutoolbar.BtnToolbar();
		toolbar = BtnToolbarCreator.create_toolbar()
		#creating prog table
		prgtbl = progtable.ProgramTable()
		#creating renderer
		RendererCreator = renderer.Renderer()
		rend = RendererCreator.create_renderer()

		#main gui grid
		grid = Gtk.Grid()
		grid.set_column_spacing(constants.DEF_SPACING)
		grid.set_row_spacing(constants.DEF_SPACING*2)
		#attach - left, top, width, height
		grid.attach(toolbar, 0, 0, 1, 2)
		grid.attach(rend, 1, 0, 1, 1)
		grid.attach(prgtbl, 1, 1, 1, 1)

		#revealer = Gtk.Revealer()
		self.revealer.set_reveal_child(Gtk.Label(label="123"))
		self.revealer.set_transition_type(4)
		self.revealer.set_reveal_child(True)
		self.revealer.show_all()
		#grid.attach(self.revealer, 1, 0, 1, 1)
		btn = Gtk.Button("reveal")
		btn.connect("clicked", self.reveal_child)
		#grid.attach(btn, 0,1,1,1)

		#set grid alignment
		grid.set_valign(Gtk.Align.FILL)
		self.add(grid)

	def reveal_child(self, button):
		if(self.revealer.get_reveal_child()):
			self.revealer.set_reveal_child(False)
		else:
			self.revealer.set_reveal_child(True)

win = MyWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
