from gi.repository import Gtk
from Gui.Placeholder import Placeholder, PlaceholderWithButton
from Gui.Icon import Icon
from Gui.PlotPage.Plot.Plot import Plot
from Gui.PlotPage.Plot import GraphTypes
from Gui.PlotPage.PlotTypeSelectDialog import PlotTypeSelectDialog

class PlotPage(Gtk.Box):
	def __init__(self, mainWnd):
		Gtk.Box.__init__(self)

		# main window
		self.mainWnd = mainWnd

		# child array
		self.plots = []

		# plot page is a box with vertical orientation
		self.set_orientation(Gtk.Orientation.VERTICAL)

		# page must be expandable
		self.set_vexpand(True)
		self.set_hexpand(True)
		# set alignment
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
		plotTypeDlg = PlotTypeSelectDialog(self.mainWnd)
		plotTypeDlg.show_all()
		responce = plotTypeDlg.run()

		if responce == Gtk.ResponseType.APPLY:

			# get selected plot parameters
			selected_type = plotTypeDlg.get_selected_plot_type()
			selected_progs = plotTypeDlg.get_selected_programs()
			# unselectd all programs
			plotTypeDlg.prog_select_page.unselect_all()

			plot_index = selected_type.get_index()
			plot_info = plotTypeDlg.plot_types[plot_index]
			plot_title = plot_info[0]
			plot_unit = plot_info[1]
			plot_range = plot_info[2]

			#self.placeholder.hide()
			#children = self.get_children()
			#for child in children:
				#if child is self.placeholder:
					#self.remove(child)

			plot = Plot(selected_progs, plot_index)

			if plot_unit is not '':
				plot_title += ", " + plot_unit

			plot.set_title(plot_title)
			plot.add_interval(0.25, GraphTypes.ERROR, True)
			plot.add_interval(0.05, GraphTypes.WARNING)
			plot.add_interval(0.4, GraphTypes.NORMAL)
			plot.add_interval(0.05, GraphTypes.WARNING)
			plot.add_interval(0.25, GraphTypes.ERROR)
			plot.set_min_max(plot_range[0], plot_range[1])

			# if y axis unit is %, slightly modify string (for future formatting puproses)
			plot.set_y_axis_unit(plot_unit)
			self.add(plot)
			self.set_valign(Gtk.Align.FILL)

			self.plots.append(plot)

		plotTypeDlg.hide()

		self.show_all()

	# filtering function that passes data to plots if they need it
	def on_incoming_data(self, data):
		for plot in self.plots:
			# if plot requires data for this stream/prog/pid
			if data[0] in plot.progs:
				plot.on_incoming_data([data[0], data[1][plot.minor_type]])
