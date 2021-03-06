import math
from functools import reduce
from collections import deque

from gi import require_version
require_version('PangoCairo', '1.0')
from gi.repository import Gtk, Gdk, cairo, Pango, PangoCairo, GObject

from Gui.PlotPage.Plot.PlotBottomBar import PlotBottomBar
from Gui.PlotPage.Plot import GraphTypes
from Gui import Spacing
from Gui.Icon import Icon
from Control import CustomMessages


class Interval():
    def __init__(self, height, type, color):
        self.height = height
        self.type = type
        self.color = color


class Plot(Gtk.Box):

    __gsignals__ = {
        CustomMessages.PLOT_PAGE_CHANGED: (GObject.SIGNAL_RUN_FIRST,
                                           None, ())}

    def __init__(self, plot_type, plot_progs, colors, data_predicate):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL,
                         spacing=Spacing.ROW_SPACING)

        # save incoming parameters
        self.plot_type = plot_type
        self.plot_progs = plot_progs
        self.data_predicate = data_predicate

        # add plot label at the top
        self.label = Gtk.Label(halign=Gtk.Align.END, hexpand=True,
                               vexpand=False, label="")

        self.close_button = Gtk.Button(image=Icon("window-close"),
                                       relief=Gtk.ReliefStyle.NONE)
        self.label_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,
                                 spacing=Spacing.COL_SPACING)
        self.label_box.add(self.label)
        self.label_box.add(self.close_button)

        # add drawing area in the middle
        self.da = Gtk.DrawingArea(hexpand=True, halign=Gtk.Align.FILL,
                                  vexpand=True, valign=Gtk.Align.FILL)
        self.da.connect('draw', self.graph_draw)
        self.da.connect('configure_event', self.graph_configure)
        self.da.connect('destroy', self.graph_destroy)
        self.da.connect('state-flags-changed', self.graph_state_changed)
        self.da.set_events(Gdk.EventMask.EXPOSURE_MASK)

        # add plot bottom bar at the bottom
        self.bottom_bar = PlotBottomBar(plot_progs, colors)
        self.bottom_bar.connect(CustomMessages.PLOT_PAGE_CHANGED,
                                self.on_plot_changed)

        # remember colors of bottom bar
        self.colors = self.bottom_bar.colors

        self.add(self.label_box)
        self.add(self.da)
        self.add(self.bottom_bar)

        # width of graph frame
        self.FRAME_WIDTH = 4

        # plot parameters
        # plot type
        # minor type - name of parameter
        self.minor_type = plot_type[0]
        # major type - video or audio
        self.major_type = plot_type[3]
        # measured data index
        self.data_index = plot_type[4]

        # progs displayed on graph. needed for mapping data
        # to corresponding plot line
        self.progs = []
        for prog in plot_progs:
            prog_info = []
            # stream id
            prog_info.append(prog[0])
            # prog id
            prog_info.append(prog[1])
            for pid in prog[5]:
                if pid[2].split('-')[0] == self.major_type:
                    # pid
                    prog_info.append(pid[0])
            # convert strings to int
            prog_info = list(map(int, prog_info))
            self.progs.append(prog_info)

        # buffers for storing input data before it is shown on graph
        self.buffer = []
        for i in range(len(self.progs)):
            self.buffer.append([])

        # drawing area parameters
        # draw area width
        self.draw_width = 0
        # draw area height
        self.draw_height = 0
        # number of horizontal bars
        self.num_bars = 1
        self.graph_dely = 0
        self.real_draw_height = 0.0
        self.graph_delx = 0
        self.graph_buffer_offset = 0
        # offset from left border
        self.indent = 24
        # graph font size
        self.fontsize = 8
        # offset from right border
        self.rmargin = 7 * self.fontsize
        # line width
        self.line_width = 1
        # background surface
        self.background = None
        # flag that permits graph drawing
        self.draw = True
        # graph range
        self.min = plot_type[2][0]
        self.max = plot_type[2][1]
        # y axis unit
        self.unit = ""
        # background intervals
        self.intervals = []

        self.total_seconds = 60
        # graph points number
        # graph refresh speed and other refresh parameters
        self.speed = 250
        self.NUM_POINTS = int((self.total_seconds * 1000 / self.speed)) + 2
        self.frames_per_unit = 10
        self.render_counter = self.frames_per_unit - 1
        # start refreshing loop
        self.timer_index = GObject.timeout_add(self.speed/self.frames_per_unit,
                                               self.graph_update,
                                               None)

        # number of displayed programs
        self.prog_num = len(self.progs)
        # data storage for analyzed programs
        self.data = []
        for i in range(self.prog_num):
            self.data.append(deque([-1] * self.NUM_POINTS, self.NUM_POINTS))

        self.prev_data = []
        for i in range(self.prog_num):
            self.prev_data.append(self.min)

    # set graph title
    def set_title(self, text):
        self.label.set_text(text)

    # add interval to plot
    def add_interval(self, height, type, clear_previous=False):
        if clear_previous is True:
            self.intervals.clear()

        # set color
        if type == GraphTypes.ERROR:
            color = (1.0, 0.7, 0.7)
        elif type == GraphTypes.WARNING:
            color = (1.0, 1.0, 0.7)
        else:
            color = (0.7, 1.0, 0.7)

        # append interval to list
        self.intervals.append(Interval(height=height, color=color, type=type))

    # set minimum and maximum values of plot y axis
    def set_min_max(self, min, max):
        self.min = min
        self.max = max
        self.clear_background()

    # set unit for plot y axis
    def set_y_axis_unit(self, unit):
        if unit == '%':
            self.unit = '%%'
        else:
            self.unit = unit
        self.clear_background()
        self.bottom_bar.set_unit(unit)

    # change plot refresh speed
    def change_speed(self, new_speed):
        self.speed = new_speed
        if selt.timer_index is not None:
            GObject.source_remove(self.timer_index)
            self.timer_index = GObject.timeout_add(
                self.speed / self.frames_per_unit. self.update, None)

        self.clear_background()

    # force graph redraw
    def graph_queue_draw(self):
        self.da.queue_draw()

    # invalidate graph background
    def clear_background(self):
        if self.background is not None:
            # self.background.destroy()
            self.background = None

    # start plotting
    def graph_start(self):
        # if timer is not already set
        if self.timer_index is None:
            self.graph_update()
            self.timer_index = GObject.timeout_add(
                self.speed / self.frames_per_unit, self.update, None)
        # enable drawing
        self.draw = True

    # stop plotting
    def graph_stop(self):
        # do not draw anymore, but continue to poll
        self.draw = False

    # when graph is to be destroyed
    def graph_destroy(self, data):
        if self.timer_index is not None:
            GObject.source_remove(self.timer_index)
        self.clear_background()

    # if graph state was changed
    def graph_state_changed(self, flags, data):
        self.clear_background()
        self.graph_queue_draw()

    # configure event was received
    def graph_configure(self, event, data):
        rect = self.da.get_allocation()
        self.draw_width = rect.width
        self.draw_height = rect.height

        self.clear_background()
        self.graph_queue_draw()

    # draw on graph
    def graph_draw(self, widget, cr):
        i = 0
        j = 0
        sample_width = 0.0
        x_offset = 0.0

        # number of pixels wide for one graph point
        sample_width = float(self.draw_width - self.rmargin - self.indent) / float(self.NUM_POINTS)
        # general offset
        x_offset = self.draw_width - self.rmargin
        # subframe offset
        x_offset += self.rmargin - (sample_width / self.frames_per_unit)*self.render_counter

        # draw the graph

        #if self.background is None:
        self.draw_background()

        cr.set_source_surface(self.background)
        cr.paint()

        cr.set_line_width(self.line_width)
        # 0 - butt, 1 - round, 2 - square
        cr.set_line_cap(1)
        cr.set_line_join(1)
        cr.rectangle(self.indent + self.FRAME_WIDTH + 1,
                     self.FRAME_WIDTH - 1,
                     self.draw_width - self.rmargin - self.indent - 1,
                     self.real_draw_height + self.FRAME_WIDTH - 1)
        cr.clip()

        for i in range(self.prog_num):
            data = self.data[i]
            # set line color
            Gdk.cairo_set_source_rgba(cr, self.bottom_bar.colors[i])
            cr.move_to(x_offset,
                       (1.0 - data[-1]) * self.real_draw_height + 3.5)
            for i in range(self.NUM_POINTS-1):
                cr.curve_to(
                    x_offset - ((i - 0.5)*self.graph_delx),
                    (1.0 - data[-1 - i])*self.real_draw_height + 3.5,
                    x_offset - ((i - 0.5)*self.graph_delx),
                    (1.0 - data[-1 - i - 1])*self.real_draw_height + 3.5,
                    x_offset - (i * self.graph_delx),
                    (1.0 - data[-1 - i - 1])*self.real_draw_height + 3.5)
            cr.stroke()

    # draw plot background (background, grids and labels)
    def draw_background(self):
        # self.graph_configure()
        self.get_num_bars()
        self.graph_dely = (self.draw_height - 20) / self.num_bars
        self.real_draw_height = float(self.graph_dely) * float(self.num_bars)
        self.graph_delx = (self.draw_width - 2.0 - self.indent) / (self.NUM_POINTS - 3)
        self.graph_buffer_offset = int((1.5 * self.graph_delx) + self.FRAME_WIDTH)

        cr = self.da.get_window().cairo_create()

        styleContext = self.get_parent().get_style_context()

        fg = styleContext.get_color(Gtk.StateType.NORMAL)

        cr.paint_with_alpha(0.0)
        layout = PangoCairo.create_layout(cr)
        font_desc = styleContext.get_font(Gtk.StateType.NORMAL)
        font_desc.set_size(0.8 * self.fontsize * Pango.SCALE)
        layout.set_font_description(font_desc)

        # draw frame
        cr.translate(self.FRAME_WIDTH, self.FRAME_WIDTH)

        width = self.draw_width - self.rmargin - self.indent
        y = 0
        for interval in self.intervals:
            cr.set_source_rgba(interval.color[0], interval.color[1], interval.color[2], 1)
            interval_height = interval.height * self.real_draw_height
            cr.rectangle(self.indent, y, width, interval_height)
            y += interval_height
            cr.fill()

        if len(self.intervals) is 0:
            cr.set_source_rgba(1, 1, 1, 1)
            rect = self.da.get_allocation()
            cr.rectangle(self.indent, 0, width, self.real_draw_height)
            cr.fill()

        cr.set_line_width(1.0)
        cr.set_source_rgb(0.89, 0.89, 0.89)

        # draw horizontal bars
        for i in range(self.num_bars + 1):
            y = 0.0
            if i == 0:
                y = 0.5 + self.fontsize / 2.0
            elif i == self.num_bars:
                y = i * self.graph_dely + 0.5
            else:
                y = i * self.graph_dely + self.fontsize / 2.0

            string = '%d' + self.unit

            cr.set_source_rgba(fg.red, fg.green, fg.blue, fg.alpha)
            caption = string % (self.max - i * ((self.max - self.min) / self.num_bars))

            layout.set_alignment(Pango.Alignment.LEFT)
            layout.set_text(caption, -1)
            extents = layout.get_extents()
            cr.move_to(self.draw_width - self.indent - 23, y - 1.0 * extents[1].height / Pango.SCALE / 2)

            PangoCairo.show_layout(cr, layout)

            if i == 0 or i == self.num_bars:
                cr.set_source_rgb(0.70, 0.71, 0.70)
            else:
                cr.set_source_rgb(0.89, 0.89, 0.89)

            cr.move_to(self.indent, i * self.graph_dely + 0.5)
            cr.line_to(self.draw_width - self.rmargin + 0.5 + 4, i * self.graph_dely + 0.5)
            cr.stroke()

        for i in range(7):
            x = i * (self.draw_width - self.rmargin - self.indent) / 6
            if i == 0 or i == 6:
                cr.set_source_rgb(0.70, 0.71, 0.70)
            else:
                cr.set_source_rgb(0.89, 0.89, 0.89)

            cr.move_to((math.ceil(x) + 0.5) + self.indent, 0.5)
            cr.line_to((math.ceil(x) + 0.5) + self.indent, self.real_draw_height + 4.5)
            cr.stroke()

            seconds = self.total_seconds - i * self.total_seconds / 6

            if i == 0:
                format = "%u секунд"
            else:
                format = "%u"

            caption = format % seconds
            layout.set_text(caption, -1)
            extents = layout.get_extents()
            cr.move_to((math.ceil(x) + 0.5 + self.indent) - (1.0 * extents[1].width / Pango.SCALE / 2),
                       self.draw_height - 1.15 * extents[1].height / Pango.SCALE)

            cr.set_source_rgba(fg.red, fg.green, fg.blue, fg.alpha)
            PangoCairo.show_layout(cr, layout)

        cr.stroke()

        # remember surface
        self.background = cr.get_target()

    # update plot
    def graph_update(self, data):

        for i in range(self.prog_num):
            if self.render_counter == self.frames_per_unit - 1:
                data = self.get_data(i)
                if data is None:
                    data = self.prev_data[i]
                if data < self.min:
                    data = self.min
                elif data > self.max:
                    data = self.max
                self.data[i].rotate(self.NUM_POINTS-1)
                self.data[i][0] = (data - self.min) / abs(self.max - self.min)
                self.prev_data[i] = data
                self.bottom_bar.set_value(data, i)

        if self.draw is True:
            self.graph_queue_draw()

        self.render_counter += 1
        if self.render_counter >= self.frames_per_unit:
            self.render_counter = 0
        return True

    # decide number of horizontal bars
    def get_num_bars(self):
        k = int(self.draw_height / (self.fontsize + 14))

        def get_nearest_divider(max_):
            range_ = abs(self.max - self.min)
            possible_dividers = list(range(max_, 0, -1))
            for i in possible_dividers:
                if range_ % i is 0:
                    return i

        if k == 0 or k == 1:
            self.num_bars = 1
            self.line_width = 1
        elif k == 2 or k == 3:
            self.num_bars = get_nearest_divider(3)
            self.line_width = 2
        elif k == 4:
            self.num_bars = get_nearest_divider(4)
            self.line_width = 2
        elif k == 5 or k == 6:
            self.num_bars = get_nearest_divider(5)
            self.line_width = 2
        else:
            self.num_bars = get_nearest_divider(10)
            self.line_width = 2

    # new data was received
    def on_incoming_data(self, data):
        index = self.progs.index(data[0])
        self.buffer[index].extend(data[1])

    def get_data(self, index):
        if len(self.buffer[index]) is not 0:
            val = self.data_predicate(self.buffer[index])
        else:
            val = None
        self.buffer[index].clear()
        return val

    # when plot colors are changed
    def on_plot_changed(self, wnd):
        self.emit(CustomMessages.PLOT_PAGE_CHANGED)

