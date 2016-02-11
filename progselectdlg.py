#!/usr/bin/python3

from gi.repository import Gtk, Gio

import constants
import basedialog

btn_txt = [">", ">>", "<", "<<"]

tree_icons = {"ts" : "view-grid-symbolic",
							"program" : "applications-multimedia-symbolic",
							"video" : "video-x-generic-symbolic",
							"audio" : "audio-x-generic-symbolic",}

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
		#box.add(buttonBox)
		#box.add(ProgList())
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
		self.set_grid_lines(Gtk.TreeViewGridLines.BOTH)
		self.set_show_expanders(True)
		self.set_enable_tree_lines(True)

		#data stored in treeview
		#icon, name, is_analyzed
		store = Gtk.TreeStore(str, str, bool)
		#fill the model
		for i in range(1):
			piter = store.append(None, [tree_icons["ts"], "TS 1", False])
			for j in range(1):
				ppiter = store.append(piter, [tree_icons["program"], "11 РЕН-ТВ", False])
				for k in range(2):
					store.append(ppiter, [tree_icons["audio"], "PID 2011", True])

		#the cellrenderer for the first column - icon
		renderer_icon = Gtk.CellRendererPixbuf()
		renderer_icon.set_alignment(0.5, 0.5)

		#the cellrenderer for the first column - text
		renderer_text = Gtk.CellRendererText()
		#renderer_text.set_alignment(0.5, 0.5)

		#the cellrenderer for the second column - toogle
		renderer_check = Gtk.CellRendererToggle()
		renderer_check.set_alignment(0.5, 0.5)

		#create first column
		column_prog = Gtk.TreeViewColumn("Найденные программы")
		column_prog.set_alignment(0.5)
		column_prog.set_expand(True)
		column_prog.pack_start(renderer_icon, False)
		column_prog.pack_start(renderer_text, True)
		column_prog.add_attribute(renderer_icon, "icon-name", 0)
		column_prog.add_attribute(renderer_text, "text", 1)
		#append first column
		self.append_column(column_prog)

		#create second column
		column_check = Gtk.TreeViewColumn("Анализировать?", renderer_check, active=1)
		column_check.set_alignment(0.5)
		column_check.set_expand(False)
		#column_check.pack_start(renderer_check, False)
		#append second column
		self.append_column(column_check)

		#set the model
		self.set_model(store)

		#open all program rows
		for row in range(len(store)):
			path = Gtk.TreePath(row)
			self.expand_row(path, False)


		self.show_all()
