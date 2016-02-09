#!/usr/bin/python
from gi.repository import Gtk, Gio

import constants

btn_txt = [">", ">>", "<", "<<"]

class ProgSelectDlg(Gtk.Window):
	def __init__(self):
		Gtk.Window.__init__(self, title=constants.toolbar_buttons_text[1])
		self.set_modal(True)
		self.set_border_width(constants.DEF_BORDER)
		self.set_resizable(False)
		self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)

		#adding a button box
		buttonBox = Gtk.ButtonBox()
		buttonBox.set_orientation(Gtk.Orientation.VERTICAL)
		buttonBox.set_layout(Gtk.ButtonBoxStyle.EXPAND)
		for i in range(4):
			buttonBox.add(Gtk.Button(label=btn_txt[i]))

		#adding a grid
		grid = Gtk.Grid()
		grid.set_column_spacing(constants.DEF_COL_SPACING)
		grid.attach(Gtk.Label(label="stream list"), 0, 0, 1, 1)
		grid.attach(buttonBox, 1, 0, 1, 1)
		grid.attach(Gtk.Label(label="analyzed list"), 2, 0, 1, 1)

		grid.show_all()

		self.add(grid)
