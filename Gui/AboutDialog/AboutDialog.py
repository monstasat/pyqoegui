from gi.repository import Gtk, GdkPixbuf

# version number
# major, minor, revision
VERSION = "0.5.0b"


# about ats analyzer dialog based on Gtk.AboutDialog
class AboutDialog(Gtk.AboutDialog):
    def __init__(self, aboutParent):
        comments = "Анализ качества изображения и звука " \
                   "в цифровых ТВ программах"
        Gtk.AboutDialog.__init__(self, parent=aboutParent, modal=True,
                                 program_name='Анализатор АТС-3-QoE',
                                 version="Версия " + VERSION,
                                 copyright='© 2016 АО "НИИ телевидения"',
                                 comments=comments)

        # adding information to about dialog
        self.add_credit_section("Разработчики",
                                ["Инженеры отдела НТК-18:",
                                 "Булавин Евгений",
                                 "Максименков Фёдор",
                                 "Янин Александр"])

        try:
            logo = GdkPixbuf.Pixbuf.new_from_file(
                './Gui/AboutDialog/logo_square.png')
            logo = logo.scale_simple(128, 128, GdkPixbuf.InterpType.BILINEAR)
            self.set_property("logo", logo)
        except:
            self.set_property("logo-icon-name", "help-about")

