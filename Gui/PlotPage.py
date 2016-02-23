from gi.repository import Gtk
from Gui.Placeholder import Placeholder, PlaceholderWithButton
from Gui.Icon import Icon
from Gui.Plot.Plot import Plot
from Gui.Plot import GraphTypes

class PlotPage(Gtk.Box):
	def __init__(self):
		Gtk.Box.__init__(self)
		self.set_orientation(Gtk.Orientation.VERTICAL)
		self.set_vexpand(True)
		self.set_hexpand(True)
		self.set_halign(Gtk.Align.FILL)
		self.set_valign(Gtk.Align.CENTER)
		self.addBtn = Gtk.Button(label="Добавить график")
		#addBtn.set_image(Icon("list-add-symbolic"))
		#addBtn.set_image_position(Gtk.PositionType.TOP)
		self.addBtn.set_always_show_image(True)
		self.addBtn.get_style_context().add_class(Gtk.STYLE_CLASS_SUGGESTED_ACTION)

		actionBar = Gtk.ActionBar(hexpand=True, vexpand=False, halign=Gtk.Align.FILL, valign=Gtk.Align.END)
		actionBar.pack_end(self.addBtn)

		self.placeholder = PlaceholderWithButton("list-add-symbolic", "Для добавления нового графика нажмите кнопку", 72, "Добавить график")
		self.placeholder.set_valign(Gtk.Align.CENTER)

		# connect buttons to callbacks
		self.placeholder.btn.connect('clicked', self.on_graph_add)
		self.addBtn.connect('clicked', self.on_graph_add)

		self.add(self.placeholder)
		#self.add(actionBar)

	def on_graph_add(self, widget):
		self.placeholder.hide()
		children = self.get_children()
		for child in children:
			if child is self.placeholder:
				self.remove(child)
		plot = Plot()
		plot.set_title("10 РЕН-ТВ. Громкость, LUFS")
		plot.add_interval(0.25, GraphTypes.ERROR, True)
		plot.add_interval(0.05, GraphTypes.WARNING)
		plot.add_interval(0.4, GraphTypes.NORMAL)
		plot.add_interval(0.05, GraphTypes.WARNING)
		plot.add_interval(0.25, GraphTypes.ERROR)
		plot.set_min_max(-40, -14)
		plot.set_y_type(" LUFS")
		self.add(plot)
		self.set_valign(Gtk.Align.FILL)
		self.show_all()
