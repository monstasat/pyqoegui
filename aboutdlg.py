#!/usr/bin/python
from gi.repository import Gtk, Gio

import constants

class AtsAboudDlg(Gtk.AboutDialog):
	def __init__(self):
		Gtk.AboutDialog.__init__(self)
		self.set_modal(True)
		self.set_property("program-name", "Анализатор АТС-3")
		self.set_property("version", "Версия " + constants.VERSION)
		self.add_credit_section("Разработчики", ["Инженеры отдела НТК-18, в том числе:", "Янин Александр", "Булавин Евгений", "Максименков Федор"])
		self.set_property("comments", "Анализ качества изображения и звука в цифровых ТВ программах")
		self.set_property("copyright", '© 2016 АО "НИИ телевидения"')
		self.set_property("logo-icon-name", "help-about")

