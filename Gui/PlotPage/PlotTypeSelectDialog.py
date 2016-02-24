from gi.repository import Gtk
from Gui.BaseDialog import BaseDialog
from Gui.PlotPage.PlotProgramTreeView import PlotProgramTreeView

class PlotTypeSelectDialog(BaseDialog):
	def __init__(self, parent):

		self.video_plot_types = ("Количество чёрных пикселей, %", "Количество идентичных пикселей, %",
							"Уровень блочности", "Средняя яркость кадра", "Среднее различие между кадрами")

		self.audio_plot_types = ("Моментальная громкость, LUFS", "Кратковременная громкость, LUFS")

		BaseDialog.__init__(self, "Выбор вида графика", parent)
		mainBox = self.get_content_area()

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
		self.prog_select_page = PlotProgramTreeView(parent.analyzedStore)

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

		# connect to store signals
		parent.analyzedStore.connect('row-deleted', self.on_row_deleted)
		parent.analyzedStore.connect('row-inserted', self.on_row_inserted)

		self.show_all()
		# to determine if we need to display placeholder initially
		self.on_store_changed()


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

	def on_row_inserted(self, path, iter, user_data):
		self.on_store_changed()

	def on_row_deleted(self, path, user_data):
		self.on_store_changed()

	def on_store_changed(self):
		# if some streams are appended to store, do not show placeholder
		if len(self.prog_select_page.store) > 0:
			# open all program rows
			piter = self.prog_select_page.store.get_iter_first()
			while piter is not None:
				path = self.prog_select_page.store.get_path(piter)
				if self.prog_select_page.row_expanded(path) is False:
					self.prog_select_page.expand_row(path, False)
				piter = self.prog_select_page.store.iter_next(piter)
			# hide placeholder
			#self.holder.hide()
		else:
			pass
			#self.holder.set_text('Программ не найдено')
			#self.holder.show_all()


