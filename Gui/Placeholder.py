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
		self.label = Gtk.Label(label=label_text)
		styleContext = self.label.get_style_context()
		styleContext.add_class(Gtk.STYLE_CLASS_DIM_LABEL)
		self.label.set_justify(Gtk.Justification.CENTER)

		# add elements to vbox
		self.add(image)
		self.add(self.label)

	def set_text(self, text):
		self.label.set_text(text)

class PlaceholderWithButton(Placeholder):
	def __init__(self, ico_name, label_text, size, btn_label):
		Placeholder.__init__(self, ico_name, label_text, size)
		self.btn = Gtk.Button(label=btn_label)
		self.btn.get_style_context().add_class(Gtk.STYLE_CLASS_SUGGESTED_ACTION)
		self.btn.set_hexpand(False)
		self.btn.set_halign(Gtk.Align.CENTER)
		self.add(self.btn)
