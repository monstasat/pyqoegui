import math

from gi.repository import Gtk, GObject

from Gui.CurrentResultsPage.Renderer import Renderer
from Gui import Spacing
from Control import CustomMessages


# a grid of video renderers
class RendererGrid(Gtk.FlowBox):

    __gsignals__ = {
        CustomMessages.VOLUME_CHANGED: (GObject.SIGNAL_RUN_FIRST,
                                               None, (int, int, int, int,))}

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
        for rend in self.rend_arr:
            rend.destroy
        self.rend_arr.clear()

        # add number of renderers
        for i in range(progNum):
            self.rend_arr.append(Renderer(guiProgInfo[i]))
            # connect renderer to volume changed signal
            self.rend_arr[i].connect(CustomMessages.VOLUME_CHANGED,
                                     self.on_volume_changed)
            af = Gtk.AspectFrame(hexpand=True, vexpand=True)
            af.set(0.5, 0.5, 4.0/3.0, False)
            af.add(self.rend_arr[i])
            # insert renderer to flow box
            self.insert(af, -1)

        # set filter function
        self.set_filter_func((lambda x, y: True), None)

        # show all renderers
        self.show_all()

    def on_volume_changed(self, wnd, stream_id, prog_id, pid, value):
        self.emit(CustomMessages.VOLUME_CHANGED,
                  stream_id,
                  prog_id,
                  pid,
                  value)

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

