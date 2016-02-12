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

from functools import reduce
from constants import create_icon_from_name
from aboutdlg import AtsAboudDlg
from constants import Placeholder

class MyWindow(Gtk.ApplicationWindow):

	edit = Gtk.Entry()
	def __init__(self, app):
		Gtk.Window.__init__(self, application=app)

		#main window border width
		self.set_border_width(constants.DEF_BORDER)
		#self.maximize()
		#self.set_resizable(False)
		#can't resize window by double click on header bar
		settings = Gtk.Settings.get_default()
		#settings.set_property("gtk-titlebar-double-click", 'none')

		#add header bar to the window
		hb = Gtk.HeaderBar(title="Анализатор АТС-3")
		self.set_titlebar(hb)

		#add menu button to header bar
		menuBtn = Gtk.MenuButton(name="menu", always_show_image=True, has_tooltip=True, tooltip_text="Меню",
					image=create_icon_from_name("open-menu-symbolic"))
		popover = Gtk.PopoverMenu(border_width=constants.DEF_BORDER)
		popBox = Gtk.HBox(spacing=constants.DEF_COL_SPACING)
		darkThemeCheck = Gtk.Switch()
		darkThemeCheck.connect('state-set', self.on_dark_theme_check)
		popBox.add(darkThemeCheck)
		popBox.add(Gtk.Label(label='Использовать тёмное оформление'))
		popBox.show_all()
		popover.add(popBox)
		menuBtn.set_popover(popover)
		hb.pack_end(menuBtn)

		#create stack pages
		pages = []
		pages.append((curresultspage.CurResultsPage(), "cur_results", "Текущие результаты"))
		pages.append((plotpage.PlotPage(), "plots", "Графики"))
		pages.append((allrespage.AllResPage(), "all_results", "Общие результаты"))

		#create stack
		myStack = Gtk.Stack()
		myStack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
		#add callback when page is switched
		myStack.connect("notify::visible-child", self.page_switched)
		#add pages to stack
		for page in pages:
			myStack.add_titled(page[0], page[1], page[2])

		#create stack switcher
		switch = Gtk.StackSwitcher(stack=myStack)
		#add stack switcher to the header bar
		hb.set_custom_title(switch)

		#creating left side bar with buttons
		toolbar = menutoolbar.BtnToolbar()

		#main window grid
		mainGrid = Gtk.Grid(row_spacing=constants.DEF_ROW_SPACING, column_spacing=constants.DEF_COL_SPACING,
							halign=Gtk.Align.FILL, valign=Gtk.Align.FILL)
		mainGrid.attach(toolbar, 0, 0, 1, 1)
		mainGrid.attach(myStack, 1, 0, 1, 1)

		#top window can have only one widget - this is Gtk.Stack in our case
		self.add(mainGrid)

		#add prgtbl button to header bar
		showTableBtn = Gtk.ToggleButton(always_show_image=True, name="table_btn", active=False,
						has_tooltip=True, image=create_icon_from_name("pan-down-symbolic"))
		#connect to the callback function of the tooltip
		showTableBtn.connect("query-tooltip", self.tooltip_callback)
		showTableBtn.connect("clicked", self.reveal_child, self.get_table_revealer())
		hb.pack_end(showTableBtn)

		#connect buttons to events
		#get start button
		btnCallbacks = [self.on_start_clicked, self.on_prog_select_clicked,
						self.on_rf_set_clicked, self.on_analysis_set_clicked,
						self.on_dump_clicked, self.on_about_clicked]
		btns = toolbar.get_children()
		for i, func in enumerate(btnCallbacks):
			btns[i].connect('clicked', func)

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
					#child.set_visible(True)
					self.check_prog_table_visible(self.get_prog_table())

	#called to hide header bar button if table is invisible
	def check_prog_table_visible(self, table):
		hb = self.get_titlebar()
		children = hb.get_children()
		for child in children:
			if(child.get_name() == 'table_btn'):
				if table.get_visible():
					if self.get_cur_results_page().get_parent().get_visible_child_name() == "cur_results":
						child.set_visible(True)
				else:
					child.set_visible(False)

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

		#here we receive program string
		#should modify its content slightly
		if responce == Gtk.ResponseType.APPLY:
			progNum = progDlg.get_prog_num()
			progList = progDlg.get_prog_list()
			progs = progList.split(':*:')

			progNames = []
			for prog in progs[1:]:
				params = prog.split('^:')
				progNames.append(params[1])

			self.on_new_prog_list(progNum, progNames)

			renderers = self.get_renderers_grid()
			xids = renderers.get_renderers_xid()

			#for i, prog in enumerate(progs[1:]):
			#	params = prog.split('^:')
			#	params[4 + int(params[3])*3] = str(xids[i])
			#	progs[i+1] = self.concatenate_string(params, '^:')

			#cat_progs = self.concatenate_string(progs, ':*:')
			#print(cat_progs)

		progDlg.destroy()

	def concatenate_string(self, arr, separator):
		cat_str = ""
		for i in range(len(arr)):
			if i < len(arr)-1:
				cat_str = cat_str + arr[i] + separator
			else:
				cat_str = cat_str + arr[i]
		return cat_str


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
		aboutDlg = AtsAboudDlg(self)
		responce = aboutDlg.run()
		if responce == Gtk.ResponseType.DELETE_EVENT or responce == Gtk.ResponseType.CANCEL:
			aboutDlg.hide()

	def on_dark_theme_check(self, widget, gparam):
		settings = Gtk.Settings.get_default()
		settings.set_property("gtk-application-prefer-dark-theme", widget.get_active())

	def on_new_prog_list(self, progNum, progNames):
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
		flowbox.draw_renderers(num, progNames)

		table.add_rows(num, progNames)
		self.check_prog_table_visible(table)

class MyApplication(Gtk.Application):

	def __init__(self):
		Gtk.Application.__init__(self)

	def do_activate(self):
		win = MyWindow(self)
		win.show_all()

		#code to set some elements initially visible/invisible
		revealer = win.get_table_revealer()
		table = revealer.get_child()

		#if table does not have any rows, hide it
		if len(table.get_model()) < 1:
			table.hide()
		#if rows added, hide renderers overlay
		else:
			overlay = win.get_renderers_grid().get_parent()
			overlay.get_children()[1].hide()
		#if table is invisible, hide the button
		win.check_prog_table_visible(table)


	def do_startup(self):
		Gtk.Application.do_startup(self)

app = MyApplication()
exit_status = app.run(sys.argv)
sys.exit(exit_status)
