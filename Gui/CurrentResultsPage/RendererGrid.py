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
        Gtk.FlowBox.__init__(self, hexpand=True, vexpand=True,
                             halign=Gtk.Align.FILL, valign=Gtk.Align.FILL,
                             homogeneous=True,
                             orientation=Gtk.Orientation.HORIZONTAL,
                             column_spacing=Spacing.COL_SPACING,
                             row_spacing=Spacing.ROW_SPACING,
                             selection_mode=Gtk.SelectionMode.NONE,
                             activate_on_single_click=False)

        self.rend_arr = []

        self.connect('draw', self.on_draw)
        self.connect('child-activated', self.on_child_activated)

    # draw necessary number of renderers
    def draw_renderers(self, prog_list):

        # first of all delete all previous renderers
        self.remove_renderers()

        # add renderers to grid
        for stream in prog_list:
            stream_id = stream[0]
            for prog in stream[1]:
                prog_name = prog[1]
                prog_type = 0
                prog_id = int(prog[0])

                video_pid = None
                audio_pid = None
                for pid in prog[4]:
                    if pid[2].split('-')[0] == 'video':
                        video_pid = int(pid[0])
                        # FIXME: & VIDEO
                        prog_type = prog_type | 0x01
                    elif pid[2].split('-')[0] == 'audio':
                        audio_pid = int(pid[0])
                        # FIXME: & AUDIO
                        prog_type = prog_type | 0x02

                # create renderer
                renderer = Renderer(stream_id, prog_id, prog_name,
                                    prog_type, video_pid, audio_pid)

                self.rend_arr.append(renderer)

                # connect renderer to volume changed signal
                renderer.connect(CustomMessages.VOLUME_CHANGED,
                                 self.on_volume_changed)
                af = Gtk.AspectFrame(hexpand=True, vexpand=True)
                af.set(0.5, 0.5, 4.0/3.0, False)
                af.add(renderer)
                # insert renderer to flow box
                self.insert(af, -1)

        # set filter function
        self.set_filter_func((lambda x, y: True), None)

        # show all renderers
        self.show_all()

    def on_volume_changed(self, wnd, stream_id, prog_id, pid, value):
        self.emit(CustomMessages.VOLUME_CHANGED,
                  stream_id, prog_id, pid, value)

    # delete all renderers
    def remove_renderers(self):
        children = self.get_children()
        for rend in self.rend_arr:
            rend.destroy()
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
                         rend.prog_id,
                         rend.drawarea.get_window().get_xid()])
        return xids

    # setting if renderers should draw black bakground
    def set_draw_mode_for_renderers(self, draw, stream_id):
        for i in range(len(self.get_children())):
            dbuf = bool(draw)
            if self.rend_arr[i].stream_id == stream_id:
                # if this is a radio program, set double buffered by default
                if (self.rend_arr[i].prog_type & 1) == 0:
                    dbuf = True
                self.rend_arr[i].draw = dbuf
                self.rend_arr[i].drawarea.set_double_buffered(dbuf)

    # when flowbox needs redrawing
    def on_draw(self, widget, cr):
        # decide on number of renderers per one line
        self.on_resize()

    # filtering function for flow box when one renderer is enlarged
    def filter_func(self, child, user_data):
        # if renderer is enlarged - show it
        return self.rend_arr[child.get_index()].is_enlarged

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
        aspect_fb = 0 if (rect.width is 0) else (rect.height/rect.width)

        # if one of renderers is enlarged - set 1 child per row
        is_enlarged = False
        for child in self.rend_arr:
            if child.is_enlarged is True:
                cols = 1
                break
        # decide on optimal number of renderers per line
        else:
            if len(self.rend_arr) is not 0:
                # get renderer ratio (height/width)
                rect = self.rend_arr[0].get_allocation()
                ratio = 0 if (rect.width is 0) else (rect.height/rect.width)
            else:
                ratio = 0
            cols = self.get_max_renderers_per_row(aspect_fb,
                                                  ratio,
                                                  len(self.rend_arr))
        # set max renderers per line
        self.set_max_children_per_line(cols)

    # algorithm for computing optimal arranging of renderers (by F. Maximenkov)
    def get_max_renderers_per_row(self, flow_box_div, rend_div, rend_num):
        W = 1.0
        H = W * flow_box_div

        aspect_list = []

        for rows in range(1, rend_num + 1):
            columns = math.ceil(rend_num / float(rows))
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

