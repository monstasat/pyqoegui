from gi.repository import Gtk, Gdk
from Gui.Plot.PlotDrawingArea import PlotDrawingArea

class Plot(Gtk.Box):
	def __init__(self):
		Gtk.Box.__init__(self)

		# plot parameters
		self.draw_width = 0
		self.draw_height = 0

		self.set_orientation(Gtk.Orientation.VERTICAL)
		self.da = PlotDrawingArea()
		self.da.set_hexpand(True)
		self.da.set_vexpand(True)
		self.da.set_halign(Gtk.Align.FILL)
		self.da.set_valign(Gtk.Align.FILL)
		self.da.set_size_request(250, 40)
		self.da.connect('draw', self.da.graph_draw)
		self.da.connect('configure_event', self.da.graph_configure)
		self.da.connect('destroy', self.da.graph_destroy)
		self.da.connect('state-flags-changed', self.da.graph_state_changed)

		self.da.set_events(Gdk.EventMask.EXPOSURE_MASK)

		self.label = Gtk.Label(halign=Gtk.Align.START, hexpand=True, vexpand=False, label="")

		self.add(self.label)
		self.add(self.da)
		self.set_spacing(6)

	# set graph title
	def set_title(self, text):
		self.label.set_text(text)

	def add_interval(self, width, type, clear_previous=False):
		if clear_previous is True:
			self.da.intervals.clear()
		self.da.add_interval(width, type)

	def set_min_max(self, min, max):
		self.da.set_min_max(min, max)

	def set_y_type(self, text):
		self.da.set_y_type(text)
