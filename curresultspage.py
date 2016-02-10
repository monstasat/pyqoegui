#!/usr/bin/python
from gi.repository import Gtk, Gio

import constants
import renderer
import progtable
from placeholder import Placeholder

class CurResultsPage(Gtk.Grid):
	def __init__(self, progNum):
		Gtk.Grid.__init__(self)

     	#creating renderers
		rend = renderer.Renderer(progNum)

		#creating renderers overlay
		overlay = Gtk.Overlay()
		overlay.add(rend)
		holder = Placeholder("face-smirk-symbolic", 'Нет анализируемых программ :( \nНо их можно добавить в меню "Выбор программ для анализа"!', 72)
		overlay.add_overlay(holder)
		overlay.set_valign(Gtk.Align.FILL)
		overlay.set_hexpand(True)
		overlay.set_vexpand(True)

		#creating prog table
		prgtbl = progtable.ProgramTable(progNum)
		prgtbl.add_rows(0, prgtbl.test)

		#creating prog table revealer
		tableRevealer = Gtk.Revealer()
		tableRevealer.add(prgtbl)
		tableRevealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_UP)
		tableRevealer.set_reveal_child(True)
		tableRevealer.set_valign(Gtk.Align.END)
		tableRevealer.hide()

		#attach - left, top, width, height
		self.attach(overlay, 0, 0, 1, 1)
		self.attach(tableRevealer, 0, 1, 1, 1)

		#set grid alignment and spacing
		self.set_valign(Gtk.Align.FILL)
		self.set_column_spacing(constants.DEF_COL_SPACING)
		self.set_row_spacing(constants.DEF_ROW_SPACING)

