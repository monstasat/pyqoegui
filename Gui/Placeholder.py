from gi.repository import Gtk

from Gui.Icon import Icon
from Gui import Spacing


# base placeholder class
class Placeholder(Gtk.VBox):
    def __init__(self, ico_name, label_text, size):
        Gtk.VBox.__init__(self,
                          valign=Gtk.Align.CENTER, halign=Gtk.Align.CENTER)

        # construct image
        image = Icon(ico_name)
        image.set_pixel_size(size)
        image.get_style_context().add_class(Gtk.STYLE_CLASS_DIM_LABEL)

        # construct label
        self.label = Gtk.Label(label=label_text,
                               justify=Gtk.Justification.CENTER)
        self.label.get_style_context().add_class(Gtk.STYLE_CLASS_DIM_LABEL)

        # add elements to vbox
        list(map(lambda x: self.add(x), [image, self.label]))

    def set_text(self, text):
        self.label.set_text(text)

