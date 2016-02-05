#!/usr/bin/python3
from gi.repository import Gtk, Gio

import constants
import menutoolbar
import progtable
import renderer

class MyWindow(Gtk.Window):

	tableRevealer = Gtk.Revealer()
	rendererRevealer = Gtk.Revealer()
	def __init__(self):
		Gtk.Window.__init__(self, title="Анализатор АТС-3")
		self.set_border_width(constants.DEF_SPACING)
		self.set_hide_titlebar_when_maximized(False)
		#self.fullscreen()
		self.maximize()

  		#add header bar to the window
		hb = Gtk.HeaderBar()
		#hb.set_show_close_button(True)
		hb.props.title = "Анализатор АТС-3"
		self.set_titlebar(hb)

		#add rend button to header bar
		showRendBtn = Gtk.Button(always_show_image=True)
		icon = Gio.ThemedIcon(name="go-top-symbolic")
		image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
		showRendBtn.set_image(image)
		showRendBtn.connect("clicked", self.reveal_child, self.rendererRevealer)
		#hb.pack_end(showRendBtn)
		#add prgtbl button to header bar
		showTableBtn = Gtk.Button(always_show_image=True)
		icon = Gio.ThemedIcon(name="go-bottom-symbolic")
		image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
		showTableBtn.set_image(image)
		showTableBtn.connect("clicked", self.reveal_child, self.tableRevealer)
		hb.pack_end(showTableBtn)

		#creating left side bar with buttons
		toolbar = menutoolbar.BtnToolbar()
		#creating prog table
		prgtbl = progtable.ProgramTable(constants.DEF_PROG_NUM)
		#creating renderer
		rend = renderer.Renderer(constants.DEF_PROG_NUM)
		#creating prog table revealer
		self.tableRevealer.add(prgtbl)
		#0 - no transition
		#1 - fade in
		#2 - slide in from the left
		#3 - slide in from the right
		#4 - slide in from the bottom
		#5 - slide in from the top
		self.tableRevealer.set_transition_type(4)
		self.tableRevealer.set_reveal_child(True)
		self.tableRevealer.show_all()
		#creating renderer revealer
		self.rendererRevealer.add(rend)
		self.rendererRevealer.set_transition_type(5)
		self.rendererRevealer.set_reveal_child(True)
		self.rendererRevealer.show_all()


		#main gui grid
		grid = Gtk.Grid()
		grid.set_column_spacing(constants.DEF_SPACING)
		grid.set_row_spacing(constants.DEF_SPACING*2)
		#attach - left, top, width, height
		grid.attach(toolbar, 0, 0, 1, 2)
		grid.attach(self.rendererRevealer, 1, 0, 1, 1)
		grid.attach(self.tableRevealer, 1, 1, 1, 1)

		#set grid alignment
		grid.set_valign(Gtk.Align.FILL)
		self.add(grid)

	def reveal_child(self, button, revealer):
		if(revealer.get_reveal_child()):
			revealer.set_reveal_child(False)
		else:
			revealer.set_reveal_child(True)

win = MyWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
