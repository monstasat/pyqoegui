from gi.repository import Gtk
from Gui.BaseDialog import BaseDialog
from Gui import Spacing

class AnalysisSettingsDialog(BaseDialog):
	def __init__(self, parent):
		BaseDialog.__init__(self, "Настройки анализа", parent)

		mainBox = self.get_content_area()

		# fill page list with created pages
		pages = []
		pages.append((Gtk.Label(label='1'), "video_loss", "Пропадание видео"))
		pages.append((Gtk.Label(label='2'), "audio_loss", "Пропадание аудио"))
		pages.append((Gtk.Label(label='3'), "black_frame", "Чёрный кадр"))
		pages.append((Gtk.Label(label='4'), "freeze", '"Заморозка" видео"'))
		pages.append((Gtk.Label(label='5'), "blockiness", "Блочность"))
		pages.append((Gtk.Label(label='6'), "overload", '"Перегрузка" звука'))
		pages.append((Gtk.Label(label='7'), "silence", "Тишина"))

		# create stack
		self.stack = Gtk.Stack(halign=Gtk.Align.FILL, hexpand=True)
		#self.stack.set_transition_duration(200)
		self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_UP_DOWN)
		# add callback when page is switched
		#self.stack.connect("notify::visible-child", self.on_page_switched)
		#add pages to stack
		for page in pages:
			self.stack.add_titled(page[0], page[1], page[2])

		# create stack sidebar
		self.stackSidebar = Gtk.StackSidebar(vexpand=True, hexpand=False, halign=Gtk.Align.START)
		self.stackSidebar.set_stack(self.stack)
		self.stackSidebar.show()

		# configure main container orientation
		mainBox.set_orientation(Gtk.Orientation.HORIZONTAL)
		# pack items to main container
		mainBox.pack_start(self.stackSidebar, False, False, 0)
		separator = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
		mainBox.pack_start(separator, False, False, 0)
		mainBox.pack_start(self.stack, True, True, 0)

		self.show_all()
