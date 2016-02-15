#!/usr/bin/python3
from gi.repository import Gtk, Gio, GObject, GLib

import sys
import common
import menutoolbar
import progtable
import renderer
import progselectdlg
import curresultspage
import plotpage
import allrespage

from common import create_icon_from_name
from aboutdlg import AtsAboudDlg
from common import write_log_message

class MyWindow(Gtk.ApplicationWindow):

	edit = Gtk.Entry()
	def __init__(self, app):
		Gtk.Window.__init__(self, application=app)

		# main window border width
		self.set_border_width(common.DEF_BORDER)
		self.maximize()
		#self.set_resizable(False)
		# can't resize window by double click on header bar
		settings = Gtk.Settings.get_default()
		#settings.set_property("gtk-titlebar-double-click", 'none')

		self.progDlg = progselectdlg.ProgSelectDlg(self)
		self.progDlg.hide()

		# add header bar to the window
		hb = Gtk.HeaderBar(title="Анализатор АТС-3")
		self.set_titlebar(hb)

		# add menu button to header bar
		menuBtn = Gtk.MenuButton(name="menu", always_show_image=True, has_tooltip=True, tooltip_text="Меню",
					image=create_icon_from_name("open-menu-symbolic"))
		popover = Gtk.PopoverMenu(border_width=common.DEF_BORDER)
		popBox = Gtk.HBox(spacing=common.DEF_COL_SPACING)
		darkThemeCheck = Gtk.Switch()
		darkThemeCheck.connect('state-set', self.on_dark_theme_check)
		popBox.add(darkThemeCheck)
		popBox.add(Gtk.Label(label='Использовать тёмное оформление'))
		popBox.show_all()
		popover.add(popBox)
		menuBtn.set_popover(popover)
		hb.pack_end(menuBtn)

		# create stack pages
		self.cur_results_page = curresultspage.CurResultsPage()
		self.plot_page = plotpage.PlotPage()
		self.all_results_page = allrespage.AllResPage()
		pages = []
		pages.append((self.cur_results_page, "cur_results", "Текущие результаты"))
		pages.append((self.plot_page, "plots", "Графики"))
		pages.append((self.all_results_page, "all_results", "Общие результаты"))

		# create stack
		self.myStack = Gtk.Stack()
		self.myStack.set_transition_duration(200)
		self.myStack.set_transition_type(Gtk.StackTransitionType.NONE)
		# add callback when page is switched
		self.myStack.connect("notify::visible-child", self.page_switched)
		#add pages to stack
		for page in pages:
			self.myStack.add_titled(page[0], page[1], page[2])

		# create stack switcher
		switch = Gtk.StackSwitcher(stack=self.myStack)
		# add stack switcher to the header bar
		hb.set_custom_title(switch)

		# creating left side bar with buttons
		toolbar = menutoolbar.BtnToolbar()

		# main window grid
		mainGrid = Gtk.Grid(row_spacing=common.DEF_ROW_SPACING, column_spacing=common.DEF_COL_SPACING,
							halign=Gtk.Align.FILL, valign=Gtk.Align.FILL)
		mainGrid.attach(toolbar, 0, 0, 1, 1)
		mainGrid.attach(self.myStack, 1, 0, 1, 1)

		# top window can have only one widget - this is Gtk.Stack in our case
		self.add(mainGrid)

		# add prgtbl button to header bar
		self.showTableBtn = Gtk.ToggleButton(always_show_image=True, name="table_btn", active=False,
						has_tooltip=True, image=create_icon_from_name("pan-down-symbolic"))
		# connect to the callback function of the tooltip
		self.showTableBtn.connect("query-tooltip", self.tooltip_callback)
		self.showTableBtn.connect("clicked", self.reveal_child, self.cur_results_page.get_table_revealer())
		hb.pack_end(self.showTableBtn)

		# connect buttons to events
		# get start button
		btnCallbacks = [self.on_start_clicked, self.on_prog_select_clicked,
						self.on_rf_set_clicked, self.on_analysis_set_clicked,
						self.on_dump_clicked, self.on_about_clicked]
		btns = toolbar.get_children()
		for i, func in enumerate(btnCallbacks):
			btns[i].connect('clicked', func)

	# on reveal table button (in header bar) clicked
	def reveal_child(self, button, revealer):
		revealer.set_reveal_child(not revealer.get_reveal_child())

	# tooltip callback for reveal table button (in header bar)
	def tooltip_callback(self, widget, x, y, keyboad_mode, tooltip):
		if widget.get_active() == False:
			tooltip.set_text("Скрыть таблицу результатов")
		else:
			tooltip.set_text("Показать таблицу результатов")
		return True

	# called when a stackswitcher switches a page. Hides a table revealer button
	def page_switched(self, stack, gparam):
		self.manage_table_revealer_button_visibility()

	# called to hide header bar button if table is invisible
	def manage_table_revealer_button_visibility(self):
		if(self.myStack.get_visible_child_name() != "cur_results"):
			self.showTableBtn.set_visible(False)
		else:
			if self.cur_results_page.get_prog_table_visible():
				self.showTableBtn.set_visible(True)
			else:
				self.showTableBtn.set_visible(False)

	# start button was clicked
	def on_start_clicked(self, widget):
		hb = widget.get_parent()
		hb.change_start_icon(widget)

	# prog select button was clicked
	def on_prog_select_clicked(self, widget):

		#run the dialog
		responce = self.progDlg.run()

		# if new program list was chosen
		if responce == Gtk.ResponseType.APPLY:
			progParams = self.progDlg.get_selected_prog_params()
			self.cur_results_page.on_prog_list_changed(progParams[0], progParams[1])

			# determine wether table revealer button should be visible
			self.manage_table_revealer_button_visibility()

			# get renderers xids from cur result page
			xids = self.cur_results_page.get_renderers_xid()

			prog_msg = common.prog_string_to_byte(progParams[2], xids)
			try:
				self.get_application().send_message(prog_msg, common.GS_PIPELINE_PORT)
			except GLib.Error:
				write_log_message("failed to send prog list message to gstreamer pipeline", event_type=common.TYPE_ERROR)
			else:
				write_log_message("prog list message successfully sent to gstreamer pipeline")

		self.progDlg.hide()

	def concatenate_string(self, arr, separator):
		cat_str = ""
		for i in range(len(arr)):
			if i < len(arr)-1:
				cat_str = cat_str + arr[i] + separator
			else:
				cat_str = cat_str + arr[i]
		return cat_str

	# rf settings button was clicked
	def on_rf_set_clicked(self, widget):
		pass

	# analysis settings button was clicked
	def on_analysis_set_clicked(self, widget):
		pass

	# dump button was clicked
	def on_dump_clicked(self, widget):
		pass

	# about button was clicked
	def on_about_clicked(self, widget):
		aboutDlg = AtsAboudDlg(self)
		responce = aboutDlg.run()
		if responce == Gtk.ResponseType.DELETE_EVENT or responce == Gtk.ResponseType.CANCEL:
			aboutDlg.destroy()

	# dark theme switch button was activated
	def on_dark_theme_check(self, widget, gparam):
		settings = Gtk.Settings.get_default()
		settings.set_property("gtk-application-prefer-dark-theme", widget.get_active())

class MyApplication(Gtk.Application):

	def __init__(self):
		Gtk.Application.__init__(self)
		write_log_message("application launched", True)

	def send_message(self, msg, destination):
		client = Gio.SocketClient.new()
		connection = client.connect_to_host("localhost", destination, None)
		istream = connection.get_input_stream()
		ostream = connection.get_output_stream()

		# send message
		ostream.write(msg)

		# close connection
		connection.close(None)

	def incoming_callback(self, obj, conn, source, data):
		istream = conn.get_input_stream()
		ostream = conn.get_output_stream()
		buffer = istream.read_bytes(1000)
		data[0] = buffer.get_data()

		#decode string back to unicode
		wstr = data[0].decode('utf-8', 'ignore')

		if len(wstr) > 0:
			# if received program list
			if wstr[0] == 'p':
				write_log_message("message with program list received from gstreamer pipeline (stream_id = " + wstr[1] + ")")
				self.win.progDlg.show_prog_list(wstr[1:])

	def do_activate(self):
		self.win = MyWindow(self)
		self.win.connect('delete-event', self.on_exit)
		self.win.show_all()

		# code to set some elements initially visible/invisible
		self.win.cur_results_page.hide_renderer_and_table()
		# if table is invisible, hide the button
		self.win.manage_table_revealer_button_visibility()

		# server for recieving messages from gstreamer pipeline
		x = ["foo"]
		server = Gio.SocketService.new()
		server.add_inet_port(common.GUI_PORT, None)
		# x - data to be passed to callback
		server.connect("incoming", self.incoming_callback, x)
		server.start()

	def on_exit(self, event, data):
		write_log_message("application closed")

	def do_startup(self):
		Gtk.Application.do_startup(self)

app = MyApplication()
exit_status = app.run(sys.argv)
sys.exit(exit_status)
