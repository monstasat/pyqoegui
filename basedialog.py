#!/usr/bin/python3

from gi.repository import Gtk, Gio

import constants

class BaseDialog(Gtk.Dialog):
	def __init__(self, myTitle, parent):
		Gtk.Dialog.__init__(self, myTitle, parent, Gtk.DialogFlags.USE_HEADER_BAR)
		self.set_modal(True)
		self.set_border_width(constants.DEF_BORDER)
		# self.set_resizable(False)
		self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
		self.set_default_size(500, 500)

		# custom header bar
		header = Gtk.HeaderBar(title=myTitle)
		# not showing 'x' at the header bar
		header.set_show_close_button(False)
		cancelBtn = Gtk.Button(stock=Gtk.STOCK_CANCEL)
		cancelBtn.connect('clicked', self.on_btn_clicked_cancel)
		header.pack_start(cancelBtn)
		applyBtn = Gtk.Button(stock=Gtk.STOCK_APPLY)
		applyBtn.connect('clicked', self.on_btn_clicked_apply)
		applyBtn.get_style_context().add_class(Gtk.STYLE_CLASS_SUGGESTED_ACTION)
		header.pack_end(applyBtn)
		self.set_titlebar(header)

		mainBox = self.get_content_area()
		mainBox.set_spacing(constants.DEF_COL_SPACING)
		mainBox.set_orientation(Gtk.Orientation.VERTICAL)
		mainBox.set_halign(Gtk.Align.FILL)
		mainBox.set_valign(Gtk.Align.FILL)
		mainBox.set_hexpand(True)
		mainBox.set_vexpand(True)

	def on_btn_clicked_apply(self, widget):
		self.response(Gtk.ResponseType.APPLY)

	def on_btn_clicked_cancel(self, widget):
		self.response(Gtk.ResponseType.CANCEL)

