#!/usr/bin/python3

from gi.repository import Gtk, Gio
from datetime import datetime
import os

# spacing between elements
DEF_COL_SPACING = 12
DEF_ROW_SPACING = 6
DEF_BORDER = 18
# default prog num
DEF_PROG_NUM = 10
# version number
VERSION = "0.1"

# log event types
TYPE_INFO = 0
TYPE_WARNING = 1
TYPE_ERROR = 2

# dividers for string with program parameters

PROG_DIVIDER = ':*:'
PARAM_DIVIDER = '^:'

# prog table column names
heading_labels = ["№",         "Программа", 	"Громкость",
					  "Нет видео", "Чёрный кадр",	"Заморозка",
					  "Блочность", "Нет аудио", 	"Тихо",
					  "Громко"]

unavailable = "Окно временно недоступно. Ведётся разработка интерфейса."

# button labels
toolbar_buttons_text = ["Старт","Выбор программ", "Настройки тюнера", "Настройки анализа",
		"Запись потока", "О программе"]

# for creating Gtk.Image from themed icon name
def create_icon_from_name(iconName):
	icon = Gio.ThemedIcon(name=iconName)
	image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
	image.show()
	return image

def write_log_message(msg, from_new_string=False, event_type=TYPE_INFO):
	f = open('log.txt', 'a')

	if event_type == TYPE_INFO:
		type_str = "[info] "
	elif event_type == TYPE_WARNING:
		type_str = "[warning] "
	elif event_type == TYPE_ERROR:
		type_str = "[error] "
	else:
		type_str = "[unknown] "

	time = datetime.now().strftime('[%Y-%m-%d %H:%M:%S] ')
	if from_new_string and (os.stat('log.txt').st_size != 0):
		f.write("\n" + time + type_str + msg + "\n")
	else:
		f.write(time + type_str + msg + "\n")

	f.close()

def write_log_message_submessage(msg, from_new_string=False):
	f = open('log.txt', 'a')
	if from_new_string and (os.stat('log.txt').st_size != 0):
		f.write("\n" + "\t" + msg + "\n")
	else:
		f.write("\t" + msg + "\n")

	f.close()


# base placeholder class
class Placeholder(Gtk.VBox):

	# init func
	def __init__(self, ico_name, label_text, size):
		Gtk.VBox.__init__(self)

		# set alignment
		self.set_valign(Gtk.Align.CENTER)
		self.set_halign(Gtk.Align.CENTER)
		self.set_spacing(DEF_ROW_SPACING)

		# construct image
		image = Gtk.Image()
		image.set_from_icon_name(ico_name, Gtk.IconSize.DIALOG)
		image.set_pixel_size(size)
		styleContext = image.get_style_context()
		styleContext.add_class(Gtk.STYLE_CLASS_DIM_LABEL)

		# construct label
		label = Gtk.Label(label=label_text)
		styleContext = label.get_style_context()
		styleContext.add_class(Gtk.STYLE_CLASS_DIM_LABEL)
		label.set_justify(Gtk.Justification.CENTER)

		# add elements to vbox
		self.add(image)
		self.add(label)
