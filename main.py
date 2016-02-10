#!/usr/bin/python3
from gi.repository import Gtk, Gio, GObject

import sys
import constants
import menutoolbar
import progtable
import renderer
import progselectdlg
import curresultspage
import plotpage
import allrespage
import basedialog

from constants import create_icon_from_name
from aboutdlg import AtsAboudDlg
from constants import Placeholder

class MyWindow(Gtk.ApplicationWindow):

	edit = Gtk.Entry()
	def __init__(self, app):
		Gtk.Window.__init__(self, title="Анализатор АТС-3", application=app)

		#main window border width
		self.set_border_width(constants.DEF_BORDER)
		#set maximized
		self.maximize()
		self.set_resizable(False)
		#can't resize window by double click on header bar
		settings = Gtk.Settings.get_default()
		settings.set_property("gtk-titlebar-double-click", 'none')

  		#add header bar to the window
		hb = Gtk.HeaderBar()
		#hb.set_show_close_button(True)
		hb.props.title = "Анализатор АТС-3"
		self.set_titlebar(hb)

		#temp
		self.edit.connect('activate', self.on_entry_enter)
		hb.pack_end(self.edit)

		#add menu button to header bar
		menuBtn = Gtk.MenuButton(name="menu", always_show_image=True)
		menuBtn.set_image(create_icon_from_name("open-menu-symbolic"))
		menuBtn.set_property("has-tooltip", True)
		menuBtn.set_tooltip_text("Меню")
		popover = Gtk.PopoverMenu()
		darkThemeCheck = Gtk.CheckButton(label='Использовать тёмное оформление')
		darkThemeCheck.show()
		darkThemeCheck.connect('toggled', self.on_dark_theme_check)
		popover.add(darkThemeCheck)
		menuBtn.set_popover(popover)
		hb.pack_end(menuBtn)

		#create stack pages
		pages = []
		pages.append((curresultspage.CurResultsPage(0), "cur_results", "Текущие результаты"))
		pages.append((plotpage.PlotPage(), "plots", "Графики"))
		pages.append((allrespage.AllResPage(), "all_results", "Общие результаты"))

		#create stack
		stack = Gtk.Stack()
		stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
		#add pages to stack
		for i in pages:
			stack.add_titled(i[0], i[1], i[2])

		#create stack switcher
		switch = Gtk.StackSwitcher()
		switch.set_stack(stack)
		#add callback when page is switched
		stack.connect("notify::visible-child", self.page_switched)
		#add stack switcher to the header bar
		hb.set_custom_title(switch)

		#creating left side bar with buttons
		toolbar = menutoolbar.BtnToolbar()

		#main window grid
		mainGrid = Gtk.Grid()
		mainGrid.attach(toolbar, 0, 0, 1, 1)
		mainGrid.attach(stack, 1, 0, 1, 1)
		mainGrid.set_row_spacing(constants.DEF_ROW_SPACING)
		mainGrid.set_column_spacing(constants.DEF_COL_SPACING)
		mainGrid.set_halign(Gtk.Align.FILL)
		mainGrid.set_valign(Gtk.Align.FILL)

		#top window can have only one widget - this is Gtk.Stack in our case
		self.add(mainGrid)

		#add prgtbl button to header bar
		showTableBtn = Gtk.ToggleButton(always_show_image=True, name="table_btn")
		showTableBtn.set_active(False)
		showTableBtn.set_image(create_icon_from_name("pan-down-symbolic"))
		showTableBtn.set_property("has-tooltip", True)
		#connect to the callback function of the tooltip
		showTableBtn.connect("query-tooltip", self.tooltip_callback)
		showTableBtn.connect("clicked", self.reveal_child, self.get_table_revealer())
		hb.pack_end(showTableBtn)

		#connect buttons to events
		#get start button
		startBtn = toolbar.get_nth_item(0)
		startBtn.connect('clicked', self.on_start_clicked)
		#get analysis settings button
		progSelectBtn = toolbar.get_nth_item(1)
		progSelectBtn.connect('clicked', self.on_prog_select_clicked)
		#get rf settings
		rfSetBtn = toolbar.get_nth_item(2)
		rfSetBtn.connect('clicked', self.on_rf_set_clicked)
		#get analysis settings button
		analysisSetBtn = toolbar.get_nth_item(3)
		analysisSetBtn.connect('clicked', self.on_analysis_set_clicked)
		#get dump button from toolbar
		dumpBtn = toolbar.get_nth_item(4)
		dumpBtn.connect('clicked', self.on_dump_clicked)
		#get about button from toolbar
		aboutBtn = toolbar.get_nth_item(5)
		aboutBtn.connect('clicked', self.on_about_clicked)

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
		overlay = curResultsPage.get_child_at(0, 0)
		return overlay.get_child()

	def get_table_revealer(self):
		curResultsPage = self.get_cur_results_page()
		return curResultsPage.get_child_at(0, 1)

	def get_prog_table(self):
		curResultsPage = self.get_cur_results_page()
		revealer = curResultsPage.get_child_at(0,1)
		return revealer.get_child()

	#returns first stack page (cur results)
	def get_cur_results_page(self):
		grid = self.get_child()
		stack = grid.get_child_at(1, 0)
		return stack.get_child_by_name("cur_results")

	#start button was clicked
	def on_start_clicked(self, widget):
		hb = widget.get_parent()
		hb.change_start_icon(widget)

	#prog select button was clicked
	def on_prog_select_clicked(self, widget):
		progDlg = progselectdlg.ProgSelectDlg(self)
		responce = progDlg.run()
		progDlg.destroy()

	#rf settings button was clicked
	def on_rf_set_clicked(self, widget):
		rfDlg = basedialog.BaseDialog("Настройки тюнера", self)
		rfDlg.show_all()
		responce = rfDlg.run()
		rfDlg.destroy()

	#analysis settings button was clicked
	def on_analysis_set_clicked(self, widget):
		pass

	#dump button was clicked
	def on_dump_clicked(self, widget):
		pass

	#about button was clicked
	def on_about_clicked(self, widget):
		aboutDlg = AtsAboudDlg()
		aboutDlg.set_transient_for(self)
		responce = aboutDlg.run()
		if responce == Gtk.ResponseType.DELETE_EVENT or responce == Gtk.ResponseType.CANCEL:
			aboutDlg.hide()

	def on_dark_theme_check(self, widget):
		settings = Gtk.Settings.get_default()
		settings.set_property("gtk-application-prefer-dark-theme", widget.get_active())

	def on_entry_enter(self, widget):
		num = self.edit.get_text()
		self.on_new_prog_list(num)

	def on_new_prog_list(self, progNum):
		page = self.get_cur_results_page()
		table = self.get_prog_table()

		overlay = page.get_child_at(0, 0)
		children = overlay.get_children()

		if progNum == "" or int(progNum) == 0 :
			children[1].show()
			table.hide()
			num = 0
		else:
			children[1].hide()
			table.show_all()
			num = int(progNum)

		flowbox = self.get_renderers_grid()
		flowbox.draw_renderers(num)

		table.add_rows(num, table.test)

class MyApplication(Gtk.Application):

	def __init__(self):
		Gtk.Application.__init__(self)

	def do_activate(self):
		win = MyWindow(self)
		win.show_all()

	def do_startup(self):
		Gtk.Application.do_startup(self)

app = MyApplication()
exit_status = app.run(sys.argv)
sys.exit(exit_status)
