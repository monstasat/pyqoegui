from gi.repository import Gtk
from Gui.BaseDialog import BaseDialog

class PlotTypeSelectDialog(BaseDialog):
	def __init__(self, parent):

		self.video_plot_types = ("Количество чёрных пикселей, %", "Количество идентичных пикселей, %",
							"Уровень блочности", "Средняя яркость кадра", "Среднее различие между кадрами")

		self.audio_plot_types = ("Моментальная громкость, LUFS", "Кратковременная громкость, LUFS")

		BaseDialog.__init__(self, "Выбор вида графика", parent)
		mainBox = self.get_content_area()
		print(mainBox.get_children())

		# create type select page
		self.type_select_page = Gtk.ListBox(hexpand=True)
		# add video types to list
		for type in self.video_plot_types:
			row = Gtk.Label(label=type)
			self.type_select_page.insert(row, -1)
		# add audio types to list
		for type in self.audio_plot_types:
			row = Gtk.Label(label=type)
			self.type_select_page.insert(row, -1)
		# selecting first type
		self.type_select_page.select_row(self.type_select_page.get_row_at_index(0))

		# create program select page
		self.prog_select_page = Gtk.TreeView(hexpand=True)
		self.prog_select_page.set_model(parent.progDlg.progTree.store)
		# the cellrenderer for the first column - icon
		renderer_icon = Gtk.CellRendererPixbuf()
		renderer_icon.set_alignment(0.5, 0.5)
		# the cellrenderer for the first column - text
		renderer_text = Gtk.CellRendererText()
		# the cellrenderer for the second column - toogle
		renderer_check = Gtk.CellRendererToggle()
		renderer_check.set_alignment(0.5, 0.5)
		#renderer_check.connect('toggled', self.on_toggled)
		# create first column
		column_prog = Gtk.TreeViewColumn("Найденные программы")
		column_prog.set_alignment(0.5)
		column_prog.set_expand(True)
		column_prog.pack_start(renderer_icon, False)
		column_prog.pack_start(renderer_text, True)
		column_prog.add_attribute(renderer_icon, "icon-name", 0)
		column_prog.add_attribute(renderer_text, "text", 1)
		# append first column
		self.prog_select_page.append_column(column_prog)
		# create second column
		column_check = Gtk.TreeViewColumn("Отображать?")
		column_check.set_alignment(0.5)
		column_check.set_expand(False)
		column_check.pack_start(renderer_check, False)
		column_check.add_attribute(renderer_check, "active", 2)
		column_check.add_attribute(renderer_check, "inconsistent", 3)
		# append second column
		self.prog_select_page.append_column(column_check)

		# fill page list with created pages
		pages = []
		pages.append((self.type_select_page, "type_select", "Тип графика"))
		pages.append((self.prog_select_page, "prog_select", "Программы на графике"))

		# create stack
		self.stack = Gtk.Stack(halign=Gtk.Align.FILL, hexpand=True)
		#self.stack.set_transition_duration(200)
		self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_UP_DOWN)
		# add callback when page is switched
		self.stack.connect("notify::visible-child", self.on_page_switched)
		#add pages to stack
		for page in pages:
			self.stack.add_titled(page[0], page[1], page[2])

		self.stackSidebar = Gtk.StackSidebar(vexpand=True, hexpand=False, halign=Gtk.Align.START)
		self.stackSidebar.set_stack(self.stack)
		self.stackSidebar.show()

		self.applyBtn.set_property('label', Gtk.STOCK_GO_FORWARD)


		mainBox.set_orientation(Gtk.Orientation.HORIZONTAL)
		mainBox.pack_start(self.stackSidebar, False, False, 0)
		separator = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
		mainBox.pack_start(separator, False, False, 0)
		mainBox.pack_start(self.stack, True, True, 0)
		children = mainBox.get_children()
		print(children)

	def on_btn_clicked_apply(self, widget):
		visible_page = self.stack.get_visible_child()
		if visible_page is self.type_select_page:
			self.stack.set_visible_child(self.prog_select_page)
			self.applyBtn.set_property('label', Gtk.STOCK_APPLY)
		else:
			BaseDialog.on_btn_clicked_apply(self, widget)

	def on_page_switched(self, stack, gparam):
		visible_page = self.stack.get_visible_child()
		if visible_page is self.type_select_page:
			self.applyBtn.set_property('label', Gtk.STOCK_GO_FORWARD)
		else:
			self.applyBtn.set_property('label', Gtk.STOCK_APPLY)


