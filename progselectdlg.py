#!/usr/bin/python
from gi.repository import Gtk, Gio

import constants

btn_txt = [">", ">>", "<", "<<"]

class ProgSelectDlg(Gtk.Dialog):
	def __init__(self, parent):
		Gtk.Dialog.__init__(self, "Выбор программ для анализа", parent, Gtk.DialogFlags.USE_HEADER_BAR)
		self.set_modal(True)
		self.set_border_width(constants.DEF_BORDER)
		#self.set_resizable(False)
		self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
		self.set_default_size(500,0)

		#custom header bar
		header = Gtk.HeaderBar()
		#not showing 'x' at the header bar
		header.set_show_close_button(False)
		header.set_title("Выбор программ для анализа")
		cancelBtn = Gtk.Button(stock=Gtk.STOCK_CANCEL)
		cancelBtn.connect('clicked', self.on_btn_clicked_cancel)
		#cancelBtn.get_style_context().add_class(Gtk.STYLE_CLASS_DESTRUCTIVE_ACTION)
		header.pack_start(cancelBtn)
		applyBtn = Gtk.Button(stock=Gtk.STOCK_APPLY)
		applyBtn.connect('clicked', self.on_btn_clicked_apply)
		applyBtn.get_style_context().add_class(Gtk.STYLE_CLASS_SUGGESTED_ACTION)
		header.pack_end(applyBtn)
		self.set_titlebar(header)

		#get dialog box
		mainBox = self.get_content_area()
		mainBox.set_spacing(constants.DEF_COL_SPACING)
		mainBox.set_orientation(Gtk.Orientation.VERTICAL)

		#get dialog header bar
		hb = self.get_header_bar()
		print(hb)

		#adding a button box
		buttonBox = Gtk.ButtonBox()
		buttonBox.set_orientation(Gtk.Orientation.VERTICAL)
		buttonBox.set_layout(Gtk.ButtonBoxStyle.EXPAND)
		for i in range(4):
			buttonBox.add(Gtk.Button(label=btn_txt[i]))

		#packing elements to dialog
		box = Gtk.Box()
		box.set_spacing(constants.DEF_COL_SPACING)
		box.add(Gtk.Label(label="stream list"))
		box.add(buttonBox)
		box.add(Gtk.Label(label="analyzed list"))
		box.set_halign(Gtk.Align.CENTER)
		box.set_valign(Gtk.Align.CENTER)
		box.set_hexpand(True)
		box.set_vexpand(True)

		mainBox.add(box)
		mainBox.set_halign(Gtk.Align.FILL)
		mainBox.set_valign(Gtk.Align.FILL)
		mainBox.set_hexpand(True)
		mainBox.set_vexpand(True)

		self.show_all()

	def on_btn_clicked_apply(self, widget):
		self.response(Gtk.ResponseType.APPLY)

	def on_btn_clicked_cancel(self, widget):
		self.response(Gtk.ResponseType.CANCEL)
