import cairo
import math

from gi import require_version
require_version('GdkX11', '3.0')
from gi.repository import Gtk, Gdk, GdkX11, GObject

from Gui import Spacing


# one instance of video renderer
# (includes renderer window, prog name label, volume button)
class Renderer(Gtk.Grid):

    def __init__(self, guiProgInfo):
        Gtk.Grid.__init__(self)

        # is renderer enlarged by user?
        self.is_enlarged = False

        self.stream_id = guiProgInfo[0]
        # program id from PMT
        self.progID = guiProgInfo[1]
        # program name from SDT
        self.progName = guiProgInfo[2]

        # should be horizontally expandable and fill all available space
        self.set_hexpand_set(True)
        self.set_hexpand(True)
        self.set_halign(Gtk.Align.FILL)
        self.set_valign(Gtk.Align.FILL)

        # creating renderer window - drawing area
        self.drawarea = Gtk.DrawingArea(hexpand=True, vexpand=True)
        self.drawarea.set_events(Gdk.EventMask.EXPOSURE_MASK)
        self.drawarea.set_app_paintable(False)
        # set default renderer size (4:3)
        self.drawarea.set_size_request(100, 75)
        # this is to remove flickering
        self.drawarea.set_double_buffered(False)
        # connect 'draw' event with callback
        self.drawarea.connect("draw", self.on_drawingarea_draw)
        # do we need to draw black background?
        self.draw = False

        screen = self.drawarea.get_screen()
        visual = screen.get_system_visual()
        if visual is not None:
            self.drawarea.set_visual(visual)

        # creating volume button at the right edge of a renderer instance
        volbtn = Gtk.VolumeButton(halign=Gtk.Align.END,
                                  hexpand=False,
                                  vexpand=False)

        volbtn.connect('value-changed', self.volume_changed)

        # creating a program label
        progname = Gtk.Label(label=self.progName,
                             halign=Gtk.Align.END,
                             hexpand=False,
                             vexpand=False)

        # attach elements to grid
        self.attach(self.drawarea, 0, 0, 2, 1)
        self.attach(progname, 0, 1, 1, 1)
        self.attach(volbtn, 1, 1, 1, 1)

    def volume_changed(self, widget, value):
        pass

    # return xid for the drawing area
    def get_drawing_area_xid(self):
        return self.drawarea.get_window().get_xid()

    def on_drawingarea_draw(self, widget, cr):
        # if it is the first time we are drawing
        if self.draw is True:
            cr.set_source_rgb(0, 0, 0)
            w = self.drawarea.get_allocated_width()
            h = self.drawarea.get_allocated_height()
            cr.rectangle(0, 0, w, h)
            cr.fill()


# a grid of video renderers
class RendererGrid(Gtk.FlowBox):
    def __init__(self):
        Gtk.FlowBox.__init__(self)

        self.rend_arr = []

        # should be horizontally expandable and fill all available space
        self.set_hexpand(True)
        self.set_vexpand(True)
        self.set_halign(Gtk.Align.FILL)
        self.set_valign(Gtk.Align.FILL)

        # set selection mode to None
        self.set_selection_mode(Gtk.SelectionMode.NONE)

        # set rows and cols homogeneous
        self.set_homogeneous(True)

        # flow box should have horizontal orientation
        self.set_orientation(Gtk.Orientation.HORIZONTAL)

        # set some space between renderers
        self.set_column_spacing(Spacing.COL_SPACING)
        self.set_row_spacing(Spacing.ROW_SPACING)

        self.set_activate_on_single_click(False)

        # connect to draw signal
        self.connect('draw', self.on_draw)
        # connect to child activated signal
        self.connect('child-activated', self.on_child_activated)

    # draw necessary number of renderers
    def draw_renderers(self, progNum, guiProgInfo):

        # first of all delete all previous renderers
        self.remove_renderers()
        self.rend_arr.clear()

        # add number of renderers
        for i in range(progNum):
            self.rend_arr.append(Renderer(guiProgInfo[i]))
            af = Gtk.AspectFrame(hexpand=True, vexpand=True)
            af.set(0.5, 0.5, 4.0/3.0, False)
            af.add(self.rend_arr[i])
            # insert renderer to flow box
            self.insert(af, -1)

        # show all renderers
        self.show_all()

    # delete all renderers
    def remove_renderers(self):
        children = self.get_children()
        for child in children:
            child.destroy()
        self.rend_arr.clear()

    # returns array of drawing area xids
    def get_renderers_xid(self):
        xids = []
        for i in range(len(self.get_children())):
            rend = self.rend_arr[i]
            rend.drawarea.realize()
            xids.append([rend.stream_id,
                         rend.progID,
                         rend.drawarea.get_window().get_xid()]
                        )
        return xids

    # setting if renderers should draw black bakground
    def set_draw_mode_for_renderers(self, draw, stream_id):
        for i in range(len(self.get_children())):
            if self.rend_arr[i].stream_id == stream_id:
                self.rend_arr[i].draw = draw

    # when flowbox needs redrawing
    def on_draw(self, widget, cr):
        # decide on number of renderers per one line
        self.on_resize()

    # filtering function for flow box when one renderer is enlarged
    def filter_func(self, child, user_data):
        index = child.get_index()
        # if renderer is enlarged - show it
        return self.rend_arr[index].is_enlarged

    # if user double-clicks renderer
    def on_child_activated(self, widget, child):
        index = child.get_index()
        # if renderer is enlarged -
        # set it to normal state and show other renderers
        if self.rend_arr[index].is_enlarged is True:
            self.rend_arr[index].is_enlarged = False
            self.set_filter_func((lambda x, y: True), None)
            for rend in self.rend_arr:
                rend.hide()
            # show all renderers after 50 ms (for more smooth redrawing)
            GObject.timeout_add(50, self.show_renderers, None)
        # if renderer is not enlarged - enlarge it and hide other renderers
        else:
            self.rend_arr[index].is_enlarged = True
            self.set_filter_func(self.filter_func, None)

    # show all renderers in flowbox
    def show_renderers(self, data):
        for rend in self.rend_arr:
            rend.show_all()
        return False

    # decide on number of renderers per one line
    def on_resize(self):
        rect = self.get_allocation()
        if rect.width is 0:
            aspect_fb = 0
        else:
            aspect_fb = rect.height / rect.width

        # see if any of renderers is enlarged
        is_enlarged = False
        for child in self.rend_arr:
            if child.is_enlarged is True:
                is_enlarged = True
        children = self.get_children()

        # if one of renderers is enlarged - set 1 child per row
        if is_enlarged is True:
            cols = 1
        # in other way (if all renderers are shown)
        # decide on optimal number of renderers per line
        else:
            renderer_aspect = 0
            if len(children) is not 0:
                # get renderer ratio (height/width)
                rect = self.rend_arr[0].get_allocation()
                if rect.width is 0:
                    ratio = 0
                else:
                    ratio = rect.height / rect.width
                #ratio = rect.height/rect.width
            else:
                ratio = 0
            cols = self.get_max_renderers_per_row(aspect_fb,
                                                  ratio,
                                                  len(children))
        # set max renderers per line
        self.set_max_children_per_line(cols)

    # algorithm for computing optimal arranging of renderers (by F. Maximenkov)
    def get_max_renderers_per_row(self, flow_box_div, rend_div, rend_num):
        W = 1.0
        H = W * flow_box_div

        aspect_list = []

        for rows in range(1, rend_num + 1):
            columns = math.ceil(rend_num / float(rows))
            S_1 = 0.0

            if (W / columns * rend_div * rows) <= H:
                S_1 = W / columns * (W / columns * rend_div)
            else:
                S_1 = H / rows * (H / rows / rend_div)

            S_useful = S_1 * rend_num
            S_rects = S_1 * rows * columns
            space_rate = S_useful / S_rects

            aspect_list.append([rows, columns, S_useful, S_rects, space_rate])

        # sort by s_useful and space rate
        sorted_al = sorted(aspect_list, key=lambda x: (x[2], x[4]))

        if len(sorted_al) > 0:
            return sorted_al[-1][1]
        else:
            return 1

