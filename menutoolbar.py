#!/usr/bin/python
from gi.repository import Gtk, Gio

class BtnToolbar(Gtk.Toolbar):

	#themed icon names
	ico_arr = ["media-playback-start", "tv-symbolic", "network-wireless", "gnome-tweak-tool",
		   "drive-harddisk", "help-about","application-exit"]

	#button labels
	text_arr = ["Старт","Выбор программ", "Настройки RF", "Настройки анализа",
				"Запись потока", "О программе", "Выход"]

	#button tooltip text
	tooltip_arr = ["Запуск/остановка анализа","Выбор программ для анализа",
			"Настройки ТВ тюнера",
			"Настройки параметров определения искажений изображения и звука",
			"Запись потока на внутренний диск или съемный носитель",
			"О программе",
			"Выход из программы"]

	#array with gtk toolbuttons
	btn_arr = []

	#create a toolbar
	def __init__(self):
		Gtk.Toolbar.__init__(self)
		#setting this toolbar as primary for the window
		self.get_style_context().add_class(Gtk.STYLE_CLASS_PRIMARY_TOOLBAR)

		#create tool buttons
		for i in range(len(self.ico_arr) - 1):
			self.btn_arr.append(Gtk.ToolButton.new(self.create_icon_from_name(self.ico_arr[i]), self.text_arr[i]))
			self.btn_arr[i].set_is_important(True)
			self.btn_arr[i].set_has_tooltip(True)
			self.btn_arr[i].set_tooltip_text(self.tooltip_arr[i])
			self.insert(self.btn_arr[i], i)
			self.btn_arr[i].show()

   		#associate buttons with functions
		#exit
		#self.btn_arr[-1].connect("clicked", self.on_app_exit)
		#start/stop
		self.btn_arr[0].connect("clicked", self.on_start)

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

	#on exit button
	def on_app_exit(self, widget):
		 Gtk.main_quit()

	#on start/stop button
	def on_start(self, widget):
		#if current state is "start"
		if widget.get_label() == "Старт":
			#change label and icon of toolbutton
			widget.set_label("Стоп")
			widget.set_icon_widget(self.create_icon_from_name("media-playback-stop"))
		#if current state is "stop"
		else:
			#change label and icon of toolbutton
			widget.set_label("Старт")
			widget.set_icon_widget(self.create_icon_from_name("media-playback-start"))

	#for creating Gtk.Image from themed icon name
	def create_icon_from_name(self, iconName):
		icon = Gio.ThemedIcon(name=iconName)
		image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
		image.show()
		return image
		
