from gi.repository import Gtk, Gdk
from Gui import Spacing

class PlotBottomBarChild(Gtk.Box):
	def __init__(self, progName, color, index):
		Gtk.Box.__init__(self)

		# value unit
		self.unit = ""

		# child index in bottom bar
		self.index = index

		# set left margin
		self.set_property('margin-start', 57)

		# set horizontal orientation
		self.set_orientation(Gtk.Orientation.HORIZONTAL)
		# set spacing
		self.set_spacing(Spacing.ROW_SPACING)

		# plot color button
		self.color_btn = Gtk.ColorButton.new_with_rgba(color)

		# prog name label
		self.prog_name = Gtk.Label(label=progName)

		# value label
		self.value = Gtk.Label()

		# add widgets to box
		self.add(self.color_btn)
		self.add(self.prog_name)
		self.add(self.value)

	def set_value(self, value):
		self.value.set_text("%g"%float(value) + " " + self.unit)

	def set_unit(self, unit):
		self.unit = unit

class PlotBottomBar(Gtk.FlowBox):

	def __init__(self, selected_progs):
		Gtk.FlowBox.__init__(self)

		self.default_colors = ( Gdk.RGBA(0.529412, 0.807843, 0.921569, 1.0), #skyblue
								Gdk.RGBA(0.486275, 0.988235, 0.000000, 1.0), #lawngreen
								Gdk.RGBA(1.000000, 0.627451, 0.478431, 1.0), #lightsalmon
								Gdk.RGBA(0.517647, 0.439216, 1.000000, 1.0), #lightslateblue
								Gdk.RGBA(1.000000, 0.000000, 1.000000, 1.0), #magenta
								Gdk.RGBA(0.941176, 0.901961, 0.549020, 1.0), #khaki
								Gdk.RGBA(1.000000, 0.941176, 0.960784, 1.0), #lavenderblush
								Gdk.RGBA(1.000000, 0.980392, 0.803922, 1.0), #lemonchiffon
								Gdk.RGBA(0.294118, 0.000000, 0.509804, 1.0), #indigo
								Gdk.RGBA(0.827451, 0.827451, 0.827451, 1.0), #lightgrey
								Gdk.RGBA(0.400000, 0.803922, 0.666667, 1.0), #mediumaquamarine
								Gdk.RGBA(0.117647, 0.564706, 1.000000, 1.0), #dodgerblue
								Gdk.RGBA(0.960784, 0.960784, 0.960784, 1.0), #whitesmoke
								Gdk.RGBA(0.956863, 0.643137, 0.376471, 1.0), #sandybrown
								Gdk.RGBA(0.854902, 0.439216, 0.839216, 1.0), #orchid
								Gdk.RGBA(1.000000, 0.843137, 0.000000, 1.0), #gold
								Gdk.RGBA(0.000000, 1.000000, 1.000000, 1.0), #cyan
								Gdk.RGBA(0.862745, 0.078431, 0.235294, 1.0), #crimson
								Gdk.RGBA(0.854902, 0.647059, 0.125490, 1.0), #goldenrod
								Gdk.RGBA(0.866667, 0.627451, 0.866667, 1.0)) #plum

		# bottom bar child list
		self.children = []

		# should be horizontally expandable and fill all available space
		self.set_hexpand(True)
		#self.set_vexpand(True)
		self.set_halign(Gtk.Align.FILL)
		self.set_valign(Gtk.Align.FILL)

		# set selection mode to None
		self.set_selection_mode(Gtk.SelectionMode.NONE)

		# set rows and cols homogeneous
		self.set_homogeneous(True)

		# flow box should have horizontal orientation
		self.set_orientation(Gtk.Orientation.HORIZONTAL)

		# set some space between renderers
		self.set_column_spacing(Spacing.COL_SPACING)
		self.set_row_spacing(Spacing.ROW_SPACING)

		# init colors with default_colors
		self.colors = list(self.default_colors)

		# add children to flowbox
		self.add_children(selected_progs)

	def add_children(self, selected_progs):
		# remove previous children from flow box
		for child in self.children:
			self.remove(child)
		# clear children list
		self.children.clear()
		# add new children
		for i, prog in enumerate(selected_progs):
			child = PlotBottomBarChild(prog[2], self.colors[i], i)
			child.color_btn.connect('color-set', self.on_color_chosen)
			self.children.append(child)
			self.insert(child, -1)
		# show all children
		self.show_all()

	# set value unit
	def set_unit(self, unit):
		for child in self.children: child.set_unit(unit)

	# if color was chosen
	def on_color_chosen(self, color_btn):
		index = color_btn.get_parent().index
		rgba = color_btn.get_rgba()
		self.colors[index] = rgba
		print(rgba)

	def set_value(self, value, index):
		self.children[index].set_value(value)
