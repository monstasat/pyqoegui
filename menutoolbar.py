#!/usr/bin/python3

from gi.repository import Gtk, Gio

from constants import create_icon_from_name
from constants import toolbar_buttons_text

#themed icon names
ico_arr = ["media-playback-start", "video-display", "network-wireless", "gnome-tweak-tool",
	   "drive-harddisk", "help-about"]

ico_arr = ["media-playback-start-symbolic", "tv-symbolic", "network-wireless-symbolic", "gnome-tweak-tool-symbolic",
	   "drive-harddisk-symbolic", "help-about-symbolic"]


#button tooltip text
tooltip_arr = ["Запустить анализ","Выбор программ для анализа",
		"Настройки ТВ тюнера",
		"Настройки алгоритмов определения искажений изображения и звука",
		"Запись потока на внутренний диск или съемный носитель",
		"О программе"]

class BtnToolbar(Gtk.Toolbar):

	#array with gtk toolbuttons
	btn_arr = []

	#create a toolbar
	def __init__(self):
		Gtk.Toolbar.__init__(self)
		#setting this toolbar as primary for the window
		self.get_style_context().add_class(Gtk.STYLE_CLASS_PRIMARY_TOOLBAR)

		#create tool buttons
		for i in range(len(ico_arr)):
			self.btn_arr.append(Gtk.ToolButton.new(create_icon_from_name(ico_arr[i]), toolbar_buttons_text[i]))
			self.btn_arr[i].set_is_important(True)
			self.btn_arr[i].set_has_tooltip(True)
			self.btn_arr[i].set_tooltip_text(tooltip_arr[i])
			self.insert(self.btn_arr[i], i)
			self.btn_arr[i].show()

		#how to show buttons in toolbar
		#ICONS, TEXT, BOTH, BOTH_HORIZ
		self.set_style(Gtk.ToolbarStyle.ICONS)

		#we want a vertical toolbar
		self.set_orientation(Gtk.Orientation.VERTICAL)

		#toolbar shouldn't expand horizontally
		self.set_hexpand_set(True)
		self.set_hexpand(False)
		#toolbar should expand vertically
		self.set_vexpand_set(True)
		self.set_vexpand(True)

		#show the toolbar
		self.show()

	def change_start_icon(self, widget):
		#if current state is "start"
		if widget.get_label() == "Старт":
			#change label and icon of toolbutton
			tooltip_arr[0] = "Остановить анализ"
			widget.set_label("Стоп")
			widget.set_icon_widget(create_icon_from_name("media-playback-stop-symbolic"))
		#if current state is "stop"
		else:
			#change label and icon of toolbutton
			tooltip_arr[0] = "Запустить анализ"
			widget.set_label("Старт")
			widget.set_icon_widget(create_icon_from_name("media-playback-start-symbolic"))
		widget.set_tooltip_text(tooltip_arr[0])

		
