import os
import inspect

from gi.repository import Gtk, GdkPixbuf

# version number
# major, minor, revision
VERSION = "0.6.3b"


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
        self.add_credit_section("Разработчики:",
                                ["Инженеры отдела НТК-18"])

        try:
            filename = inspect.getfile(inspect.currentframe())
            path = os.path.dirname(os.path.abspath(filename))
            logo = GdkPixbuf.Pixbuf.new_from_file(
                path + '/logo_square.png')
            logo = logo.scale_simple(128, 128, GdkPixbuf.InterpType.TILES)
            self.set_property("logo", logo)
        except:
            self.set_property("logo-icon-name", "help-about")

