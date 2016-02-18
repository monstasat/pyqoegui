from gi.repository import Gtk

# version number
VERSION = "0.1.0a"

# about ats analyzer dialog based on Gtk.AboutDialog
class AboutDialog(Gtk.AboutDialog):
	def __init__(self, aboutParent):
		Gtk.AboutDialog.__init__(self, parent=aboutParent)
		#about dialog should be modal - no other windows are active
		self.set_modal(True)

		#adding information to about dialog
		self.set_property("program-name", 'Анализатор АТС-3-QoE')
		self.set_property("version", "Версия " + VERSION)
		self.add_credit_section("Разработчики", ["Инженеры отдела НТК-18:", "Булавин Евгений", "Максименков Фёдор", "Янин Александр"])
		self.set_property("comments", "Анализ качества изображения и звука в цифровых ТВ программах")
		self.set_property("copyright", '© 2016 АО "НИИ телевидения"')
		self.set_property("logo-icon-name", "help-about")

