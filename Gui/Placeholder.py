from gi.repository import Gtk
from Gui.Icon import Icon
from Gui import Spacing

# base placeholder class
class Placeholder(Gtk.VBox):

	# init func
	def __init__(self, ico_name, label_text, size):
		Gtk.VBox.__init__(self)

		# set alignment
		self.set_valign(Gtk.Align.CENTER)
		self.set_halign(Gtk.Align.CENTER)
		self.set_spacing(Spacing.ROW_SPACING)

		# construct image
		image = Icon(ico_name)
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
