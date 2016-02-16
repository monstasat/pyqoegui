#!/usr/bin/python3

from gi.repository import Gtk, Gio

import common
import renderer
import progtable
from common import Placeholder

class CurResultsPage(Gtk.Grid):
	def __init__(self):
		Gtk.Grid.__init__(self)

		# creating renderers
		self.rend = renderer.RendererGrid()

		# creating renderers overlay
		overlay = Gtk.Overlay(valign=Gtk.Align.FILL, hexpand=True, vexpand=True)
		overlay.add(self.rend)
		self.holder = Placeholder("face-smirk-symbolic", 'Нет анализируемых программ :( \nНо их можно добавить в меню "Выбор программ для анализа"!', 72)
		overlay.add_overlay(self.holder)

		# creating prog table
		self.prgtbl = progtable.ProgramTable()

		# creating prog table revealer
		self.tableRevealer = Gtk.Revealer(reveal_child=True, valign=Gtk.Align.END, transition_type=Gtk.RevealerTransitionType.SLIDE_UP)
		self.tableRevealer.add(self.prgtbl)

		# attach - left, top, width, height
		self.attach(overlay, 0, 0, 1, 1)
		#self.attach(self.rend, 0, 0, 1, 1)
		self.attach(self.tableRevealer, 0, 1, 1, 1)

		# set grid alignment and spacing
		self.set_valign(Gtk.Align.FILL)
		self.set_column_spacing(common.DEF_COL_SPACING)
		self.set_row_spacing(common.DEF_ROW_SPACING)

	def get_renderers_xid(self):
		return self.rend.get_renderers_xid()

	def on_prog_list_changed(self, progNum, progNames):
		if progNum == "" or int(progNum) == 0 :
			self.holder.show()
			self.prgtbl.hide()
			num = 0
		else:
			self.holder.hide()
			self.prgtbl.show_all()
			num = int(progNum)

		self.rend.draw_renderers(num, progNames)
		self.prgtbl.add_rows(num, progNames)

	def get_prog_table_visible(self):
		return self.prgtbl.get_visible()

	def hide_renderer_and_table(self):
		# if table does not have any rows, hide it
		if len(self.prgtbl.get_model()) < 1:
			self.prgtbl.hide()
		# if rows added, hide renderers overlay
		else:
			self.holder.hide()

	def get_table_revealer(self):
		return self.tableRevealer



