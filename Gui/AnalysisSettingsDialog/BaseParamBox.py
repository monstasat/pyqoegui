from gi.repository import Gtk

from Gui.BaseDialog import Switch
from Gui import Spacing

class BaseParamBox(Gtk.Box):
    def __init__(self):

        Gtk.Box.__init__(self, halign=Gtk.Align.FILL, valign=Gtk.Align.FILL,
                         hexpand=True, vexpand=True,
                         spacing=Spacing.ROW_SPACING,
                         orientation=Gtk.Orientation.VERTICAL,)

        # create peak box
        peak_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,
                           hexpand=True, vexpand=True,
                           halign=Gtk.Align.FILL, valign=Gtk.Align.FILL)
        peak_box.add(Switch('Пиковые ошибки'))

        # create cont box
        cont_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,
                           hexpand=True, vexpand=True,
                           halign=Gtk.Align.FILL, valign=Gtk.Align.FILL)
        cont_box.add(Switch('Длительные ошибки'))

        self.add(peak_box)
        self.add(Gtk.HSeparator())
        self.add(cont_box)
