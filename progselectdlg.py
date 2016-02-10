#!/usr/bin/python3

from gi.repository import Gtk, Gio

import constants
import basedialog

btn_txt = [">", ">>", "<", "<<"]

class ProgSelectDlg(basedialog.BaseDialog):

	def __init__(self, parent):
		basedialog.BaseDialog.__init__(self, "Выбор программ для анализа", parent)
		self.set_default_size(500,0)

		#get dialog box
		mainBox = self.get_content_area()

		#adding a button box
		buttonBox = Gtk.ButtonBox()
		buttonBox.set_halign(Gtk.Align.CENTER)
		buttonBox.set_valign(Gtk.Align.CENTER)
		buttonBox.set_orientation(Gtk.Orientation.VERTICAL)
		buttonBox.set_layout(Gtk.ButtonBoxStyle.EXPAND)
		for i in range(4):
			buttonBox.add(Gtk.Button(label=btn_txt[i]))

		#packing elements to dialog
		box = Gtk.Box()
		box.set_spacing(constants.DEF_COL_SPACING)
		box.add(ProgList())
		box.add(buttonBox)
		box.add(ProgList())
		box.set_halign(Gtk.Align.FILL)
		box.set_valign(Gtk.Align.FILL)
		box.set_hexpand(True)
		box.set_vexpand(True)

		mainBox.add(box)

		self.show_all()

class ProgList(Gtk.TreeView):

	def __init__(self):
		Gtk.TreeView.__init__(self)
		self.set_hexpand(True)
		self.set_vexpand(True)
		self.set_halign(Gtk.Align.FILL)
		self.set_valign(Gtk.Align.FILL)
  		
