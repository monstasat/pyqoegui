from gi.repository import Gtk, GObject

from Gui.Placeholder import Placeholder
from Gui.Icon import Icon
from Gui.PlotPage.Plot.Plot import Plot
from Gui.PlotPage.Plot import GraphTypes
from Gui.PlotPage.PlotTypeSelectDialog import PlotTypeSelectDialog
from Gui.PlotPage import PlotTypes
from Gui import Spacing
from Control import CustomMessages


class PlotPage(Gtk.Box):

    def __init__(self, mainWnd):
        Gtk.Box.__init__(self, hexpand=True, vexpand=True,
                         halign=Gtk.Align.FILL, valign=Gtk.Align.CENTER,
                         spacing=Spacing.ROW_SPACING,
                         orientation=Gtk.Orientation.VERTICAL)

        # max plots on page
        self.MAX_PLOTS = 4

        # main window
        self.mainWnd = mainWnd

        # child array
        self.plots = []

        # create add plot button
        self.addBtn = Gtk.Button(label="Добавить график",
                                 halign=Gtk.Align.CENTER)
        self.addBtn.get_style_context().add_class(
            Gtk.STYLE_CLASS_SUGGESTED_ACTION)
        self.addBtn.connect('clicked', self.on_plot_add_dialog)

        self.placeholder = Placeholder(
            "list-add-symbolic",
            "Для добавления нового графика нажмите кнопку", 72)
        self.placeholder.set_valign(Gtk.Align.CENTER)

        # placeholder box (with add button)
        self.placeholder_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,
                                       spacing=Spacing.ROW_SPACING)
        self.placeholder_box.add(self.placeholder)
        self.placeholder_box.add(self.addBtn)

        # initially add only placeholder
        self.add(self.placeholder_box)

    # if add plot button was pressed
    def on_plot_add_dialog(self, widget):

        # show plot selection dialog
        plotTypeDlg = PlotTypeSelectDialog(self.mainWnd)
        responce = plotTypeDlg.run()

        # if user selected a dialog
        if responce == Gtk.ResponseType.APPLY:

            # get selected plot parameters
            selected_type = plotTypeDlg.get_selected_plot_type()
            selected_progs = plotTypeDlg.get_selected_programs()
            plot_index = selected_type.get_index()
            plot_info = PlotTypes.PLOT_TYPES[plot_index]

            # add plot to plot page
            self.add_plot(plot_info, selected_progs, [])
            self.mainWnd.emit(CustomMessages.PLOT_PAGE_CHANGED)

        # hide plot selection dialog
        plotTypeDlg.hide()

    def add_plot(self, plot_info, plot_progs, colors):

        # get information about selected prog type
        plot_title = plot_info[0]
        plot_unit = plot_info[1]
        plot_range = plot_info[2]

        # if plot param is freeze, black or blockiness, plot max value
        if PlotTypes.PLOT_TYPES.index(tuple(plot_info)) == 0 or \
           PlotTypes.PLOT_TYPES.index(tuple(plot_info)) == 1 or \
           PlotTypes.PLOT_TYPES.index(tuple(plot_info)) == 2:
            data_predicate = lambda x: max(x)
        # else, plot average value
        else:
            data_predicate = lambda x: sum(x)/len(x)

        # create new plot with selected parameters
        plot = Plot(plot_info, plot_progs, colors, data_predicate)
        # connect delete plot event to plot close button
        plot.close_button.connect('clicked', self.on_plot_delete)

        # append plot unit (if any) to plot title
        if plot_unit is not '':
            plot_title += ", " + plot_unit
        plot.set_title(plot_title)

        self.add_plot_intervals(plot, self.mainWnd.analysis_settings)

        plot.set_min_max(plot_range[0], plot_range[1])
        plot.set_y_axis_unit(plot_unit)
        # connect plot to changed signal
        plot.connect(CustomMessages.PLOT_PAGE_CHANGED, self.on_plot_changed)
        # show plot
        plot.show_all()

        # add plot to plot page
        self.add(plot)

        # append plot to plot list
        self.plots.append(plot)

        # unselect all programs in model
        self.mainWnd.analyzed_progs_model.unselect_all()

        # hide placeholder and move add button to right edge of the page
        self.placeholder.hide()
        self.addBtn.set_halign(Gtk.Align.END)

        # align plot page to fill all available space
        self.set_valign(Gtk.Align.FILL)

        # if maximum plot number reached, disable add button
        if len(self.plots) >= self.MAX_PLOTS:
            self.addBtn.set_sensitive(False)

    # if user deletes the plot from page
    def on_plot_delete(self, widget):
        # get corresponding plot
        plot = widget.get_parent().get_parent()
        # remove plot from list and from page
        self.plots.remove(plot)
        self.remove(plot)
        plot.destroy()

        # if number of plots on page is 0,
        # show placeholder and move button to center of the page
        if len(self.plots) is 0:
            self.set_valign(Gtk.Align.CENTER)
            self.placeholder.show_all()
            self.addBtn.set_halign(Gtk.Align.CENTER)

        # if number of plots on page is less that max, activate add button
        if len(self.plots) < self.MAX_PLOTS:
                self.addBtn.set_sensitive(True)

        # emit message about plot num change to control
        self.mainWnd.emit(CustomMessages.PLOT_PAGE_CHANGED)

    # add intervals to plot
    def add_plot_intervals(self, plot, analysis_settings):
        # get current plot y axis range
        plot_range = plot.plot_type[2]

        # get index of plot
        index = PlotTypes.PLOT_TYPES.index(tuple(plot.plot_type))

        # get plot full range
        full_range = abs(plot_range[1] - plot_range[0])


        # FIXME: add dependency on enable/disable cont or peak
        # apply intervals
        # freeze frame
        if index is 0:
            err = analysis_settings['freeze_cont']
            plot.add_interval((plot_range[1] - err)/full_range,
                              GraphTypes.ERROR,
                              clear_previous=True)
            plot.add_interval((err - plot_range[0])/full_range,
                              GraphTypes.NORMAL)
        # black frame
        elif index is 1:
            err = analysis_settings['black_cont']
            plot.add_interval((plot_range[1] - err)/full_range,
                              GraphTypes.ERROR,
                              clear_previous=True)
            plot.add_interval((err - plot_range[0])/full_range,
                              GraphTypes.NORMAL)
        # blockiness
        elif index is 2:
            err = analysis_settings['blocky_cont']
            plot.add_interval((plot_range[1] - err)/full_range,
                              GraphTypes.ERROR,
                              clear_previous=True)
            plot.add_interval((err - plot_range[0])/full_range,
                              GraphTypes.NORMAL)
        # average frame luma
        elif index is 3:
            err = analysis_settings['luma_cont']
            plot.add_interval((plot_range[1] - err)/full_range,
                              GraphTypes.NORMAL,
                              clear_previous=True)
            plot.add_interval((err - plot_range[0])/full_range,
                              GraphTypes.ERROR)
        # average frame difference
        elif index is 4:
            err = analysis_settings['diff_cont']
            plot.add_interval((plot_range[1] - err)/full_range,
                              GraphTypes.NORMAL,
                              clear_previous=True)
            plot.add_interval((err - plot_range[0])/full_range,
                              GraphTypes.ERROR)
        elif (index is 5) or (index is 6):
            high_err = analysis_settings['loudness_cont']
            low_err = analysis_settings['silence_cont']
            plot.add_interval(abs(plot_range[1] - high_err)/full_range,
                              GraphTypes.ERROR,
                              clear_previous=True)
            plot.add_interval(abs(high_err - low_err)/full_range,
                              GraphTypes.NORMAL)
            plot.add_interval(abs(low_err - plot_range[0])/full_range,
                              GraphTypes.ERROR)

    def on_plot_changed(self, wnd):
        self.mainWnd.emit(CustomMessages.PLOT_PAGE_CHANGED)

    # filtering function that passes measured data to plots if they need it
    def on_incoming_data(self, data):
        for plot in self.plots:
            # if plot requires data for this stream/prog/pid
            if data[0] in plot.progs:
                plot.on_incoming_data([data[0], data[1][plot.data_index]])

