import os
import re

from gi.repository import Gtk, Gdk, GObject

from Gui.ButtonToolbar import ButtonToolbar
from Gui.CurrentResultsPage.CurrentResultsPage import CurrentResultsPage
from Gui.PlotPage.PlotPage import PlotPage
from Gui.AllResultsPage.AllResultsPage import AllResultsPage
from Gui.ProgramTreeModel import ProgramTreeModel
from Gui.ProgramSelectDialog.ProgramSelectDialog import ProgramSelectDialog
from Gui.AnalysisSettingsDialog.AnalysisSettingsDialog import \
                                AnalysisSettingsDialog
from Gui.TunerSettingsDialog.TunerSettingsDialog import TunerSettingsDialog
from Gui.DumpSettingsDialog import DumpSettingsDialog
from Gui.AboutDialog.AboutDialog import AboutDialog
from Gui.Icon import Icon
from Gui import Spacing
from Control import CustomMessages
from BaseInterface import BaseInterface


class Gui(BaseInterface):

    # specific Gui signals
    __gsignals__ = {
        CustomMessages.VOLUME_CHANGED: (GObject.SIGNAL_RUN_FIRST,
                                        None, (int, int, int, int)),
        CustomMessages.COLOR_THEME: (GObject.SIGNAL_RUN_FIRST,
                                     None, (int,)),
        CustomMessages.PROG_TABLE_REVEALER: (GObject.SIGNAL_RUN_FIRST,
                                             None, (int,)),
        CustomMessages.PLOT_PAGE_CHANGED: (GObject.SIGNAL_RUN_FIRST,
                                           None, ())}

    def __init__(self, app):

        BaseInterface.__init__(self, app)

        self.window = Gtk.Window(decorated=False, resizable=False)

        settings = Gtk.Settings.get_default()
        # set default font
        settings.set_property("gtk-font-name", "Cantarell 11")

        # create program tree model for programs in stream
        self.stream_progs_model = ProgramTreeModel()
        # create program tree model for analyzed programs
        self.analyzed_progs_model = ProgramTreeModel(self.analyzed_prog_list)

        # create prog selection dialog
        self.progDlg = ProgramSelectDialog(self)
        # create tuner settings dialog
        self.tunerDlg = TunerSettingsDialog(self, self.tuner_settings)
        # create analysis settings dialog
        self.analysisSetDlg = AnalysisSettingsDialog(self,
                                                     self.analysis_settings)
        # create dump settings dialog
        self.dumpSetDlg = DumpSettingsDialog(self)

        # add menu button to header bar
        menuBtn = Gtk.MenuButton(name="menu", always_show_image=True,
                                 has_tooltip=True, tooltip_text="Меню",
                                 image=Icon("open-menu-symbolic"))

        popover = Gtk.Popover(border_width=Spacing.BORDER)
        popBox = Gtk.HBox(spacing=Spacing.COL_SPACING,
                          orientation=Gtk.Orientation.VERTICAL)

        dark_theme_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,
                                 spacing=Spacing.COL_SPACING)
        self.darkThemeCheck = Gtk.Switch()
        self.darkThemeCheck.connect('state-set', self.on_dark_theme_check)
        dark_theme_box.add(self.darkThemeCheck)
        dark_theme_box.add(Gtk.Label(label='Использовать тёмное оформление'))
        popBox.add(dark_theme_box)
        popBox.add(Gtk.HSeparator())

        self.cpu_load_val = Gtk.Label(label="")
        cpu_load_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        cpu_load_box.add(Gtk.Label(label="Загрузка процессора: "))
        cpu_load_box.add(self.cpu_load_val)
        cpu_load_box.set_halign(Gtk.Align.END)
        popBox.add(cpu_load_box)

        self.remote_clients_num_val = Gtk.Label(label="0")
        remote_clients_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        remote_clients_box.add(Gtk.Label(label="Удалённых подключений: "))
        remote_clients_box.add(self.remote_clients_num_val)
        remote_clients_box.set_halign(Gtk.Align.END)
        popBox.add(remote_clients_box)

        popBox.show_all()
        popover.add(popBox)
        menuBtn.set_popover(popover)

        # create stack pages
        self.cur_results_page = CurrentResultsPage(self)
        self.plot_page = PlotPage(self)
        self.all_results_page = AllResultsPage()
        pages = [(self.cur_results_page, "cur_results", "Текущие результаты"),
                 (self.plot_page, "plots", "Графики")]#,
                 #(self.all_results_page, "all_results", "Общие результаты")]

        # create stack
        self.myStack = Gtk.Stack(transition_duration=200,
                                 transition_type=Gtk.StackTransitionType.NONE)
        # add callback when page is switched
        self.myStack.connect("notify::visible-child", self.page_switched)
        # add pages to stack
        list(map(lambda x: self.myStack.add_titled(x[0], x[1], x[2]), pages))

        # create stack switcher
        switch = Gtk.StackSwitcher(stack=self.myStack, homogeneous=True)

        # creating left side bar with buttons
        self.toolbar = ButtonToolbar()

        # create prog table button
        self.showTableBtn = Gtk.ToggleButton(always_show_image=True,
                                             name="table_btn", active=False,
                                             has_tooltip=True,
                                             image=Icon("pan-down-symbolic"))
        # connect to the callback function of the tooltip
        self.showTableBtn.connect("query-tooltip", self.tooltip_callback)
        self.showTableBtn.connect("clicked", self.reveal_child,
                                  self.cur_results_page.get_table_revealer())

        # create header bar
        hb = Gtk.HeaderBar(custom_title=switch)
        list(map(lambda x: hb.pack_end(x), [menuBtn, self.showTableBtn]))

        # box that includes left-side button bar and page stack
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,
                       border_width=Spacing.BORDER,
                       spacing=Spacing.COL_SPACING)
        list(map(lambda x: hbox.add(x), [self.toolbar, self.myStack]))

        # main window box (with vertical orientation)
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        list(map(lambda x: vbox.add(x), [hb, hbox]))
        self.window.add(vbox)
        self.window.show_all()

        # code to set some elements initially visible/invisible
        self.cur_results_page.hide_renderer_and_table()
        # if table is invisible, hide the button
        self.manage_table_revealer_button_visibility()

        # connect buttons to events
        # get start button
        btnCallbacks = [self.on_start_clicked, self.on_prog_select_clicked,
                        self.on_rf_set_clicked, self.on_analysis_set_clicked,
                        self.on_dump_clicked, self.on_about_clicked]
        list(map(lambda btn, func: btn.connect('clicked', func),
                 self.toolbar.get_children(), btnCallbacks))

    def __destroy__(self):
        BaseInterface.__destroy__(self)
        self.window.destroy()

    def set_monitor_mode(self, screen):
        if screen is None:
            return True

        max_m = 0
        max_w = 0
        monitors = []
        nmons = screen.get_n_monitors()
        for m in range(nmons):
            mg = screen.get_monitor_geometry(m)
            name = screen.get_monitor_plug_name(m)
            if mg.width > max_w:
                max_m = m
                max_w = mg.width
            monitors.append(mg)

        mon_rect = monitors[max_m]

        self.window.realize()
        self.window.set_size_request(mon_rect.width, mon_rect.height)
        self.window.resize(mon_rect.width, mon_rect.height)

    def set_gui_params(self, width, height, fullscreen, debug, color_theme,
                       table_revealed, plot_info):

        # show/hide title bar and resizing cursors
        self.window.set_decorated(debug)
        self.window.set_resizable(debug)

        if debug is False:
            screen = self.window.get_screen()
            self.set_monitor_mode(screen)
            screen.connect("size-changed", self.set_monitor_mode)
            screen.connect("monitors-changed", self.set_monitor_mode)

        # show in fullscreen if necessary
        if fullscreen is True:
            self.window.fullscreen()

        # set initial gui view
        self.darkThemeCheck.set_active(color_theme)
        self.showTableBtn.set_active(table_revealed)
        for plot in plot_info:
            colors = []
            for color in plot[2]:
                colors.append(Gdk.RGBA(color[0], color[1], color[2], color[3]))
            self.plot_page.add_plot(plot[0], plot[1], colors)

        # temporary hide dump button
        toolbtns = self.toolbar.get_children()
        toolbtns[-2].hide()

    # Methods for interaction with Control
    # Common methods for Gui and Usb

    # called by Control to update stream prog list
    def update_stream_prog_list(self, prog_list):
        BaseInterface.update_stream_prog_list(self, prog_list)
        self.stream_progs_model.add_all_streams(prog_list)

    # called by Control to update analyzed prog list
    def update_analyzed_prog_list(self, prog_list):
        BaseInterface.update_analyzed_prog_list(self, prog_list)
        # apply prog list to analyzed progs model
        self.analyzed_progs_model.add_all_streams(prog_list)
        # add new programs to gui
        self.cur_results_page.on_prog_list_changed(prog_list)
        # determine wether table revealer button should be visible
        self.manage_table_revealer_button_visibility()

    # called by Control to update analysis settings
    def update_analysis_settings(self, analysis_settings):
        BaseInterface.update_analysis_settings(self, analysis_settings)
        # update analysis settings dialog
        self.analysisSetDlg.update_values(self.analysis_settings)
        for plot in self.plot_page.plots:
            self.plot_page.add_plot_intervals(plot,
                                              self.analysis_settings)

    # called by Control to update tuner settings
    def update_tuner_settings(self, tuner_settings):
        BaseInterface.update_tuner_settings(self, tuner_settings)
        # update tuner dialog
        self.tunerDlg.update_values(self.tuner_settings)

    # called by Control to update tuner status
    def update_tuner_status(self, status, hw_errors, temperature):
        BaseInterface.update_tuner_status(self, status, hw_errors, temperature)

    # called by Control to update tuner parameters
    def update_tuner_params(self, status, modulation, params):
        BaseInterface.update_tuner_params(self, status, modulation, params)
        if self.tunerDlg.get_visible() is True:
            self.tunerDlg.set_new_tuner_params(status, modulation, params)

    # called by Control to update tuner measured data
    def update_tuner_measured_data(self, measured_data):
        BaseInterface.update_tuner_measured_data(self, measured_data)
        if self.tunerDlg.get_visible() is True:
            self.tunerDlg.set_new_measured_data(measured_data)

    # called by Error Detector to update video status
    def update_video_status(self, results):
        BaseInterface.update_video_status(self, results)
        self.cur_results_page.prgtbl.update_video(results)

    # called by Error Detector to update audio status
    def update_audio_status(self, results):
        BaseInterface.update_audio_status(self, results)
        self.cur_results_page.prgtbl.update_audio(results)

    # called by Control to update lufs values in program table and plots
    def update_lufs(self, lufs):
        BaseInterface.update_lufs(self, lufs)
        self.plot_page.on_incoming_data(lufs)
        self.cur_results_page.prgtbl.update_lufs(lufs)

    # Control asks to return analyzed prog list
    def get_analyzed_prog_list(self):
        BaseInterface.get_analyzed_prog_list(self)
        return self.stream_progs_model.get_selected_list()

    # Control asks to return analysis settings
    def get_analysis_settings(self):
        BaseInterface.get_analysis_settings(self)
        return self.analysisSetDlg.get_analysis_settings()

    # Control asks to return tuner settings
    def get_tuner_settings(self):
        BaseInterface.get_analysis_settings(self)
        return self.tunerDlg.get_tuner_settings()

    # called by Control to update cpu load
    def update_cpu_load(self, load):
        BaseInterface.update_cpu_load(self, load)
        self.cpu_load_val.set_text(str(load) + "%")

    # Methods for interaction with Control
    # Specific Gui methods

    # called by Control to update data in video plots
    def update_video_plots_data(self, data):
        self.plot_page.on_incoming_data(data)

    # called by Control to update drawing mode for renderers
    def update_rendering_mode(self, draw, stream_id):
        self.cur_results_page.rend.set_draw_mode_for_renderers(draw, stream_id)

    # called by Control to mute all programs
    def mute_all_renderers(self):
        self.cur_results_page.mute_all_renderers()

    # called by Control to update remote clients number
    def update_remote_clients_num(self, clients_num):
        self.remote_clients_num_val.set_text(str(clients_num))

    # Control asks to return current xids for video rendering
    def get_renderers_xids(self):
        return self.cur_results_page.rend.get_renderers_xid()

    # Control asks to return info about currently existing plots
    def get_plot_info(self):
        plot_info = []
        for plot in self.plot_page.plots:
            colors = []
            for color in plot.colors:
                colors.append([color.red, color.green,
                               color.blue, color.alpha])
            plot_info.append([list(plot.plot_type), plot.plot_progs, colors])
        return plot_info

    # User actions handling

    # on reveal table button (in header bar) clicked
    def reveal_child(self, button, revealer):
        revealer.set_reveal_child(not revealer.get_reveal_child())
        self.emit(CustomMessages.PROG_TABLE_REVEALER,
                  not revealer.get_reveal_child())

    # tooltip callback for reveal table button (in header bar)
    def tooltip_callback(self, widget, x, y, keyboad_mode, tooltip):
        if widget.get_active() == False:
            tooltip.set_text("Скрыть таблицу результатов")
        else:
            tooltip.set_text("Показать таблицу результатов")
        return True

    # called when a stackswitcher switches a page.
    # Hides a table revealer button
    def page_switched(self, stack, gparam):
        self.manage_table_revealer_button_visibility()

    # called to hide header bar button if table is invisible
    def manage_table_revealer_button_visibility(self):
        if self.myStack.get_visible_child_name() != "cur_results":
            self.showTableBtn.set_visible(False)
        else:
            self.showTableBtn.set_visible(
                self.cur_results_page.get_prog_table_visible())

    # dark theme switch button was activated
    def on_dark_theme_check(self, widget, gparam):
        Gtk.Settings.get_default().set_property(
                              "gtk-application-prefer-dark-theme",
                              widget.get_active())
        self.emit(CustomMessages.COLOR_THEME, widget.get_active())

    # Functions called when user clicks one of the buttons from toolbar

    # start button was clicked
    def on_start_clicked(self, widget):
        # send stop message if button label is stop and vice versa
        if widget.get_label() == "Стоп":
            self.emit(CustomMessages.ACTION_STOP_ANALYSIS)
        else:
            self.emit(CustomMessages.ACTION_START_ANALYSIS)

    # prog select button was clicked
    def on_prog_select_clicked(self, widget):
        responce = self.progDlg.run()
        if responce == Gtk.ResponseType.APPLY:
            self.emit(CustomMessages.NEW_SETTINS_PROG_LIST)
        self.progDlg.hide()

    # rf settings button was clicked
    def on_rf_set_clicked(self, widget):
        responce = self.tunerDlg.run()
        if responce == Gtk.ResponseType.APPLY:
            self.emit(CustomMessages.TUNER_SETTINGS_CHANGED)
        self.tunerDlg.hide()

    # analysis settings button was clicked
    def on_analysis_set_clicked(self, widget):
        responce = self.analysisSetDlg.run()
        if responce == Gtk.ResponseType.APPLY:
            self.emit(CustomMessages.ANALYSIS_SETTINGS_CHANGED)
        self.analysisSetDlg.hide()

    # dump button was clicked
    def on_dump_clicked(self, widget):
        responce = self.dumpSetDlg.run()
        if responce == Gtk.ResponseType.APPLY:
            pass
        self.dumpSetDlg.hide()

    # about button was clicked
    def on_about_clicked(self, widget):
        aboutDlg = AboutDialog(self.window)
        aboutDlg.run()
        aboutDlg.destroy()

