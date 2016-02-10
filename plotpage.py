#!/usr/bin/python
from gi.repository import Gtk, Gio

import constants
from placeholder import Placeholder

class PlotPage(Gtk.VBox):
	def __init__(self):
		Gtk.VBox.__init__(self)
		self.add(Placeholder("action-unavailable-symbolic", constants.unavailable, 72))
