from gi.repository import Gtk, GdkPixbuf

# version number
# major, minor, revision
VERSION = "0.4.0a"


# about ats analyzer dialog based on Gtk.AboutDialog
class AboutDialog(Gtk.AboutDialog):
    def __init__(self, aboutParent):
        Gtk.AboutDialog.__init__(self, parent=aboutParent)
        # about dialog should be modal - no other windows are active
        self.set_modal(True)

        # adding information to about dialog
        self.set_property("program-name", 'Анализатор АТС-3-QoE')
        self.set_property("version", "Версия " + VERSION)
        self.add_credit_section("Разработчики",
                                ["Инженеры отдела НТК-18:",
                                 "Булавин Евгений",
                                 "Максименков Фёдор",
                                 "Янин Александр"])
        self.set_property("comments",
                          "Анализ качества изображения и звука "
                          "в цифровых ТВ программах")
        self.set_property("copyright", '© 2016 АО "НИИ телевидения"')

        try:
            logo = GdkPixbuf.Pixbuf.new_from_file(
                './Gui/AboutDialog/logo_square.png')
            logo = logo.scale_simple(128, 128, GdkPixbuf.InterpType.BILINEAR)
            self.set_property("logo", logo)
        except:
            self.set_property("logo-icon-name", "help-about")

