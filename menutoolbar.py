#!/usr/bin/python
from gi.repository import Gtk

class BtnToolbar():

	ico_arr = ["./television_gear.ico", "./transmit.png", "./mixer.png",
		   "./database_save.ico"]

	text_arr = ["Выбор программ", "Настройки RF", "Настройки анализа",
				"Запись потока"]

	tooltip_arr = ["Выбор программ для анализа",
			"Настройки ТВ тюнера",
			"Настройки параметров определения искажений изображения и звука",
			"Запись потока на внутренний диск или съемный носитель"]

	def __init__(self):
		pass

	def create_toolbar(self):
		toolbar = Gtk.Toolbar()
		toolbar.get_style_context().add_class(Gtk.STYLE_CLASS_PRIMARY_TOOLBAR)
		#create buttons
		for i in range(4):
			image = Gtk.Image()
			image.set_from_file(self.ico_arr[i])
			button = Gtk.ToolButton.new(image, self.text_arr[i])
			button.set_is_important(True)
			button.set_has_tooltip(True)
			button.set_tooltip_text(self.tooltip_arr[i])
			toolbar.insert(button, i)
			button.show()
		toolbar.set_hexpand(True)
		toolbar.show()
		#ICONS, TEXT, BOTH, BOTH_HORIZ
		toolbar.set_style(Gtk.ToolbarStyle.ICONS)
		toolbar.set_orientation(Gtk.Orientation.VERTICAL)
		toolbar.set_hexpand_set(True)
		toolbar.set_hexpand(False)
		toolbar.set_vexpand_set(True)
		toolbar.set_vexpand(True)

		return toolbar
