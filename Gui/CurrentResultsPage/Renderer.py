from gi import require_version
require_version('GdkX11', '3.0')
from gi.repository import Gtk, Gdk, GdkX11, GObject, GdkPixbuf

from Gui.Icon import Icon
from Control import CustomMessages


# one instance of video renderer
# (includes renderer window, prog name label, volume button)
class Renderer(Gtk.Grid):

    __gsignals__ = {
        CustomMessages.VOLUME_CHANGED: (GObject.SIGNAL_RUN_FIRST,
                                        None, (int, int, int, int,))}

    def __init__(self,
                 stream_id,
                 prog_id,
                 prog_name,
                 prog_type,
                 video_pid,
                 audio_pid):

        Gtk.Grid.__init__(self)

        # is renderer enlarged by user?
        self.is_enlarged = False

        self.stream_id = stream_id
        # program id from PMT
        self.prog_id = prog_id
        # program name from SDT
        self.progName = prog_name
        # prog type
        self.prog_type = prog_type
        # video pid
        self.video_pid = video_pid
        # audio pid
        self.audio_pid = audio_pid

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
        self.volbtn = Gtk.VolumeButton(halign=Gtk.Align.END,
                                       hexpand=False,
                                       vexpand=False)

        self.volbtn.connect('value-changed', self.volume_changed)
        # if program to this renderer do no contain audio,
        # disable volume button
        # FIXME: chnage 2 and 3
        if (self.prog_type != 2) and (self.prog_type != 3):
            self.volbtn.set_sensitive(False)

        # creating a program label
        progname = Gtk.Label(label=self.progName,
                             halign=Gtk.Align.END,
                             hexpand=False,
                             vexpand=False)

        # attach elements to grid
        self.attach(self.drawarea, 0, 0, 2, 1)
        self.attach(progname, 0, 1, 1, 1)
        self.attach(self.volbtn, 1, 1, 1, 1)

    def volume_changed(self, widget, value):
        self.emit(CustomMessages.VOLUME_CHANGED,
                  int(self.stream_id),
                  int(self.prog_id),
                  int(self.audio_pid),
                  int(value * 100))
        # TODO: change 1 to VIDEO
        # redraw if renderer corresponds to radio program
        if (self.prog_type & 1) == 0:
            self.drawarea.queue_draw()

    # return xid for the drawing area
    def get_drawing_area_xid(self):
        return self.drawarea.get_window().get_xid()

    def on_drawingarea_draw(self, widget, cr):

        # TODO: change 1 to VIDEO
        # if renderer corresponds to radio program
        if (self.prog_type & 1) == 0:

            # get volume button icons
            icons = self.volbtn.get_property("icons")

            # choose icon to draw
            volume = self.volbtn.get_value()
            if volume == 0.0:
                icon = icons[0]
            elif volume == 1.0:
                icon = icons[1]
            elif 0 < volume < 0.5:
                icon = icons[2]
            else:
                icon = icons[3]

            # get dimensions of drawing area
            w = self.drawarea.get_allocated_width()
            h = self.drawarea.get_allocated_height()

            # create pixbuf from icon with size height/2
            icon_theme = Gtk.IconTheme.get_default()
            pixbuf = icon_theme.load_icon(icon,
                                          h/2,
                                          0)

            # fill renderer background
            cr.set_source_rgb(0.0, 0.0, 0.0)
            cr.rectangle(0, 0, w, h)
            cr.fill()

            Gdk.cairo_set_source_pixbuf(cr,
                                        pixbuf,
                                        (w - pixbuf.get_width())/2,
                                        (h - pixbuf.get_height())/2)
            cr.paint()

        # if draw flag was set
        elif self.draw is True:
            cr.set_source_rgb(0, 0, 0)
            w = self.drawarea.get_allocated_width()
            h = self.drawarea.get_allocated_height()
            cr.rectangle(0, 0, w, h)
            cr.fill()

    def set_volume(self, value):
        self.volbtn.set_value(value)

