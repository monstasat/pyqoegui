#!/usr/bin/python3
from gi.repository import Gtk, Gio

import constants
from constants import Placeholder

class AllResPage(Gtk.VBox):
	def __init__(self):
		Gtk.VBox.__init__(self)
		self.add(Placeholder("action-unavailable-symbolic", constants.unavailable, 72))
