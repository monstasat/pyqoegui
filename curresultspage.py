#!/usr/bin/python3

from gi.repository import Gtk, Gio

import constants
import renderer
import progtable
from constants import Placeholder

class CurResultsPage(Gtk.Grid):
	def __init__(self):
		Gtk.Grid.__init__(self)

		#creating renderers
		rend = renderer.Renderer()

		#creating renderers overlay
		overlay = Gtk.Overlay(valign=Gtk.Align.FILL, hexpand=True, vexpand=True)
		overlay.add(rend)
		holder = Placeholder("face-smirk-symbolic", 'Нет анализируемых программ :( \nНо их можно добавить в меню "Выбор программ для анализа"!', 72)
		overlay.add_overlay(holder)

		#creating prog table
		prgtbl = progtable.ProgramTable()
		#prgtbl.add_rows(progNum, prgtbl.test)

		#creating prog table revealer
		tableRevealer = Gtk.Revealer(reveal_child=True, valign=Gtk.Align.END, transition_type=Gtk.RevealerTransitionType.SLIDE_UP)
		tableRevealer.add(prgtbl)

		#attach - left, top, width, height
		self.attach(overlay, 0, 0, 1, 1)
		self.attach(tableRevealer, 0, 1, 1, 1)

		#set grid alignment and spacing
		self.set_valign(Gtk.Align.FILL)
		self.set_column_spacing(constants.DEF_COL_SPACING)
		self.set_row_spacing(constants.DEF_ROW_SPACING)

