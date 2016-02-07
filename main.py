#!/usr/bin/python3
from gi.repository import Gtk, Gio

import constants
import menutoolbar
import progtable
import renderer

from constants import create_icon_from_name
from aboutdlg import AtsAboudDlg

class MyWindow(Gtk.Window):

	edit = Gtk.Entry()
	def __init__(self):
		Gtk.Window.__init__(self, title="Анализатор АТС-3")
		self.set_border_width(constants.DEF_BORDER)
		#self.maximize()

  		#add header bar to the window
		hb = Gtk.HeaderBar()
		#hb.set_show_close_button(True)
		hb.props.title = "Анализатор АТС-3"
		self.set_titlebar(hb)

		#temp
		hb.pack_end(self.edit)

		#creating left side bar with buttons
		toolbar = menutoolbar.BtnToolbar()
		#creating prog table
		prgtbl = progtable.ProgramTable(constants.DEF_PROG_NUM)
		#creating renderer
		rend = renderer.Renderer(constants.DEF_PROG_NUM)
		#creating prog table revealer
		tableRevealer = Gtk.Revealer()
		tableRevealer.add(prgtbl)
		tableRevealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_UP)
		tableRevealer.set_reveal_child(True)
		tableRevealer.show_all()

		#add prgtbl button to header bar
		showTableBtn = Gtk.ToggleButton(always_show_image=True, name="table_btn")
		icon = Gio.ThemedIcon(name="go-bottom-symbolic")
		image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
		showTableBtn.set_image(image)
		showTableBtn.set_property("has-tooltip", True)
		#connect to the callback function of the tooltip
		showTableBtn.connect("query-tooltip", self.tooltip_callback)
		showTableBtn.connect("clicked", self.reveal_child, tableRevealer)
		hb.pack_end(showTableBtn)

		#main gui grid
		grid = Gtk.Grid()
		grid.set_column_spacing(constants.DEF_COL_SPACING)
		grid.set_row_spacing(constants.DEF_ROW_SPACING)
		#attach - left, top, width, height
		grid.attach(toolbar, 0, 0, 1, 2)
		grid.attach(rend, 1, 0, 1, 1)
		grid.attach(tableRevealer, 1, 1, 1, 1)
		#set grid alignment
		grid.set_valign(Gtk.Align.FILL)

		#add page switcher (Gtk.StackSwitcher) to the header bar
		#add stack
		stack = Gtk.Stack()
		stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
		stack.add_titled(grid, "cur_results", "Текущие результаты")
		unavailable = "Ведётся разработка интерфейса. Окно временно недоступно."
		stack.add_titled(Gtk.Label(label=unavailable), "plots", "Графики")
		stack.add_titled(Gtk.Label(label=unavailable), "all_results", "Общие результаты")
		#add stack switcher
		switch = Gtk.StackSwitcher()
		switch.set_stack(stack)
		stack.connect("notify::visible-child", self.page_switched)
		hb.set_custom_title(switch)

		#connect buttons to events
		#get dump button from toolbar
		dumpBtn = toolbar.get_nth_item(4)
		dumpBtn.connect('clicked', self.on_dump_clicked)
		#get about button from toolbar
		aboutBtn = toolbar.get_nth_item(5)
		aboutBtn.connect('clicked', self.on_about_clicked)

		#top window can have only one widget - this is Gtk.Stack in our case
		self.add(stack)

	#on reveal table button (in header bar) clicked
	def reveal_child(self, button, revealer):
		revealer.set_reveal_child(not revealer.get_reveal_child())

	#tooltip callback for reveal table button (in header bar)
	def tooltip_callback(self, widget, x, y, keyboad_mode, tooltip):
		if widget.get_active() == False:
			tooltip.set_text("Скрыть таблицу результатов")
		else:
			tooltip.set_text("Показать таблицу результатов")
		return True

	#called when a stackswitcher switches a page. Hides a table revealer button
	def page_switched(self, stack, gparam):
		hb = self.get_titlebar()
		children = hb.get_children()
		for child in children:
			if(child.get_name() == 'table_btn'):
				if(stack.get_visible_child_name() != "cur_results"):
					child.set_visible(False)
				else:
					child.set_visible(True)

	#return flowbox with renderers
	def get_renderers_grid(self):
		curResultsPage = self.get_cur_results_page()
		return curResultsPage.get_child_at(1, 0)

	#returns first stack page (cur results)
	def get_cur_results_page(self):
		stack = self.get_child()
		return stack.get_child_by_name("cur_results")

	#start button was clicked
	def on_start_clicked(self, widget):
		pass

	#prog select button was clicked
	def on_prog_select_clicked(self, widget):
		pass

	#analysis settings button was clicked
	def on_analysis_set_clicked(self, widget):
		pass

	#dump button was clicked (temporary for drawing renderers)
	def on_dump_clicked(self, widget):
		num = self.edit.get_text()
		page = self.get_cur_results_page()
		flowbox = page.get_child_at(1, 0)
		flowbox.draw_renderers(int(num))

	#about button was clicked
	def on_about_clicked(self, widget):
		aboutDlg = AtsAboudDlg()
		aboutDlg.set_transient_for(self)
		responce = aboutDlg.run()
		if responce == Gtk.ResponseType.DELETE_EVENT or responce == Gtk.ResponseType.CANCEL:
			aboutDlg.hide()

win = MyWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
