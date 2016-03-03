#!/usr/bin/python3
from gi.repository import Gtk, Gdk, GLib, GObject

from Gui.ButtonToolbar import ButtonToolbar
from Gui.CurrentResultsPage.CurrentResultsPage import CurrentResultsPage
from Gui.PlotPage.PlotPage import PlotPage
from Gui.AllResultsPage.AllResultsPage import AllResultsPage
from Gui.ProgramSelectDialog import ProgramSelectDialog
from Gui.AnalysisSettingsDialog import AnalysisSettingsDialog
from Gui.TunerSettingsDialog import TunerSettingsDialog
from Gui.AboutDialog import AboutDialog
from Gui.Icon import Icon
from Gui import Spacing
from Control import CustomMessages


class MainWindow(Gtk.Window):

    __gsignals__ = {
        CustomMessages.NEW_SETTINS_PROG_LIST: (GObject.SIGNAL_RUN_FIRST,
                                               None, ()),
        CustomMessages.ACTION_START_ANALYSIS: (GObject.SIGNAL_RUN_FIRST,
                                               None, ()),
        CustomMessages.ACTION_STOP_ANALYSIS: (GObject.SIGNAL_RUN_FIRST,
                                              None, ()),
        CustomMessages.VOLUME_CHANGED: (GObject.SIGNAL_RUN_FIRST,
                                        None, (int, int, int, int)),
        CustomMessages.COLOR_THEME: (GObject.SIGNAL_RUN_FIRST,
                                        None, (int,)),
        CustomMessages.PROG_TABLE_REVEALER: (GObject.SIGNAL_RUN_FIRST,
                                        None, (int,)),
        CustomMessages.PLOT_PAGE_CHANGED: (GObject.SIGNAL_RUN_FIRST,
                                               None, ()),
        CustomMessages.ANALYSIS_SETTINGS_CHANGED: (GObject.SIGNAL_RUN_FIRST,
                                               None, ())}

    def __init__(self,
                 app,
                 stream_progs_model,
                 analyzed_progs_model,
                 error_model,
                 color_theme,
                 table_revealed,
                 plot_info):

        Gtk.Window.__init__(self, application=app)

        # applied programs info
        self.guiProgInfo = []

        # main window border width
        self.set_border_width(Spacing.BORDER)
        #self.maximize()
        # self.set_resizable(False)
        # can't resize window by double click on header bar
        settings = Gtk.Settings.get_default()
        # settings.set_property("gtk-titlebar-double-click", 'none')

        # get models from control
        # remember model for storing streaming programs lists
        # and corresponding parameters
        self.store = stream_progs_model
        # remember model for storing analyzed programs lists
        # and corresponding parameters
        self.analyzedStore = analyzed_progs_model
        # remember model for storing analysis settings
        self.errorSettingsStore = error_model

        # create prog selection dialog
        self.progDlg = ProgramSelectDialog(self)
        self.progDlg.hide()

        # add header bar to the window
        hb = Gtk.HeaderBar()

        # add menu button to header bar
        menuBtn = Gtk.MenuButton(name="menu",
                                 always_show_image=True,
                                 has_tooltip=True,
                                 tooltip_text="Меню",
                                 image=Icon("open-menu-symbolic"))

        popover = Gtk.Popover(border_width=Spacing.BORDER)
        popBox = Gtk.HBox(spacing=Spacing.COL_SPACING)
        darkThemeCheck = Gtk.Switch()
        darkThemeCheck.connect('state-set', self.on_dark_theme_check)
        popBox.add(darkThemeCheck)
        popBox.add(Gtk.Label(label='Использовать тёмное оформление'))
        popBox.show_all()
        popover.add(popBox)
        menuBtn.set_popover(popover)
        hb.pack_end(menuBtn)

        # create stack pages
        self.cur_results_page = CurrentResultsPage(self)
        self.plot_page = PlotPage(self)
        self.all_results_page = AllResultsPage()
        pages = []
        pages.append((self.cur_results_page,
                      "cur_results",
                      "Текущие результаты"))
        pages.append((self.plot_page,
                      "plots",
                      "Графики"))
        pages.append((self.all_results_page,
                      "all_results",
                      "Общие результаты"))

        # create stack
        self.myStack = Gtk.Stack()
        self.myStack.set_transition_duration(200)
        self.myStack.set_transition_type(Gtk.StackTransitionType.NONE)
        # add callback when page is switched
        self.myStack.connect("notify::visible-child", self.page_switched)
        # add pages to stack
        for page in pages:
            self.myStack.add_titled(page[0], page[1], page[2])

        # create stack switcher
        switch = Gtk.StackSwitcher(stack=self.myStack)
        # add stack switcher to the header bar
        hb.set_custom_title(switch)

        # creating left side bar with buttons
        self.toolbar = ButtonToolbar()

        # main window grid
        mainGrid = Gtk.Grid(row_spacing=Spacing.ROW_SPACING,
                            column_spacing=Spacing.COL_SPACING,
                            halign=Gtk.Align.FILL,
                            valign=Gtk.Align.FILL
                            )
        mainGrid.attach(self.toolbar, 0, 0, 1, 1)
        mainGrid.attach(self.myStack, 1, 0, 1, 1)

        # top window can have only one widget - this is Gtk.Stack in our case
        self.add(mainGrid)

        # add prgtbl button to header bar
        self.showTableBtn = Gtk.ToggleButton(always_show_image=True,
                                             name="table_btn",
                                             active=False,
                                             has_tooltip=True,
                                             image=Icon("pan-down-symbolic"))
        # connect to the callback function of the tooltip
        self.showTableBtn.connect("query-tooltip", self.tooltip_callback)
        self.showTableBtn.connect("clicked",
                                  self.reveal_child,
                                  self.cur_results_page.get_table_revealer()
                                  )
        hb.pack_end(self.showTableBtn)

        self.set_titlebar(hb)

        self.show_all()

        # set initial gui view
        if color_theme is True:
            darkThemeCheck.set_active(True)
        if table_revealed is True:
            self.showTableBtn.set_active(table_revealed)
        for plot in plot_info:
            colors = []
            for color in plot[2]:
                colors.append(Gdk.RGBA(color[0], color[1], color[2], color[3]))
            self.plot_page.add_plot(plot[0], plot[1], colors)

        # code to set some elements initially visible/invisible
        self.cur_results_page.hide_renderer_and_table()
        # if table is invisible, hide the button
        self.manage_table_revealer_button_visibility()

        # connect buttons to events
        # get start button
        btnCallbacks = [self.on_start_clicked, self.on_prog_select_clicked,
                        self.on_rf_set_clicked, self.on_analysis_set_clicked,
                        self.on_dump_clicked, self.on_about_clicked]
        btns = self.toolbar.get_children()
        for i, func in enumerate(btnCallbacks):
            btns[i].connect('clicked', func)

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
        if(self.myStack.get_visible_child_name() != "cur_results"):
            self.showTableBtn.set_visible(False)
        else:
            if self.cur_results_page.get_prog_table_visible():
                self.showTableBtn.set_visible(True)
            else:
                self.showTableBtn.set_visible(False)

    # dark theme switch button was activated
    def on_dark_theme_check(self, widget, gparam):
        settings = Gtk.Settings.get_default()
        settings.set_property("gtk-application-prefer-dark-theme",
                              widget.get_active())
        self.emit(CustomMessages.COLOR_THEME, widget.get_active())

    # get renderers xids from cur result page
    def get_renderers_xids(self):
        return self.cur_results_page.get_renderers_xid()

    # set gui for new program list
    def set_new_programs(self, guiProgInfo):
        self.guiProgInfo = guiProgInfo
        # add new programs to gui
        self.cur_results_page.on_prog_list_changed(guiProgInfo)
        # determine wether table revealer button should be visible
        self.manage_table_revealer_button_visibility()

    def on_video_measured_data(self, data):
        self.plot_page.on_incoming_data(data)

    def set_draw_mode_for_renderers(self, draw, stream_id):
        self.cur_results_page.rend.set_draw_mode_for_renderers(draw, stream_id)

    # get plot page parameters
    def get_plot_info(self):
        plot_info = []
        for plot in self.plot_page.plots:
            colors = []
            for color in plot.colors:
                colors.append([color.red, color.green, color.blue, color.alpha])
            plot_info.append([list(plot.plot_type), plot.plot_progs, colors])
        return plot_info

    def mute_all_renderers(self):
        self.cur_results_page.mute_all_renderers()

    # start button was clicked
    def on_start_clicked(self, widget):
        # send stop message if button label is stop and vice versa
        if widget.get_label() == "Стоп":
            self.emit(CustomMessages.ACTION_STOP_ANALYSIS)
        else:
            self.emit(CustomMessages.ACTION_START_ANALYSIS)

    # prog select button was clicked
    def on_prog_select_clicked(self, widget):
        # run the dialog
        responce = self.progDlg.run()

        # if new program list was chosen
        if responce == Gtk.ResponseType.APPLY:
            # emit signal from gui to control about new programs
            self.emit(CustomMessages.NEW_SETTINS_PROG_LIST)

        self.progDlg.hide()

    # rf settings button was clicked
    def on_rf_set_clicked(self, widget):
        # create the dialog
        tunerSetDlg = TunerSettingsDialog(self)
        responce = tunerSetDlg.run()

        # if new settings applied
        if responce == Gtk.ResponseType.APPLY:
            # apply settings
            pass
            # emit signal from gui to control about new tuner params
            pass

        tunerSetDlg.destroy()

    # analysis settings button was clicked
    def on_analysis_set_clicked(self, widget):
        # create the dialog
        analysisSetDlg = AnalysisSettingsDialog(self)
        responce = analysisSetDlg.run()

        # if new settings applied
        if responce == Gtk.ResponseType.APPLY:
            # apply settings
            analysisSetDlg.apply_settings()
            # apply changes to plots
            for plot in self.plot_page.plots:
                self.plot_page.add_plot_intervals(plot)
            # emit signal from gui to control about new analysis params
            self.emit(CustomMessages.ANALYSIS_SETTINGS_CHANGED)

        analysisSetDlg.destroy()

    # dump button was clicked
    def on_dump_clicked(self, widget):
        pass

    # about button was clicked
    def on_about_clicked(self, widget):
        aboutDlg = AboutDialog(self)
        responce = aboutDlg.run()
        if responce == Gtk.ResponseType.DELETE_EVENT or \
           responce == Gtk.ResponseType.CANCEL:
            aboutDlg.destroy()

