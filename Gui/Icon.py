from gi.repository import Gtk, Gio

class Icon(Gtk.Image):
    def __init__(self, ico_name):
        ico = Gio.ThemedIcon(name=ico_name)
        Gtk.Image.__init__(self, gicon=ico, icon_size=Gtk.IconSize.BUTTON)
