from gi.repository import Gtk

from Gui.TunerSettingsDialog.TunerStatusTreeView import TunerStatusTreeView
from Gui.TunerSettingsDialog.TunerMeasuredDataTreeView import \
                             TunerMeasuredDataTreeView
from Gui import Spacing


# box with widgets for status displaying
class TunerStatusBox(Gtk.Box):
    def __init__(self):
        Gtk.Box.__init__(self)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_spacing(Spacing.ROW_SPACING)
        self.set_border_width(Spacing.BORDER)

        # current tv standard
        self.device = 0xff

        # current tuner status
        self.no_device = True
        self.status_ok = False
        self.level_ok = False
        self.lock_ok = False

        # status color bar
        self.status_color_bar = Gtk.Label(label="Нет данных от тюнера")
        self.status_color_bar.set_size_request(-1, 40)
        self.status_color_bar.connect('draw', self.on_color_label_draw)

        # signal parameters
        self.signal_params_view = TunerStatusTreeView(self)

        # measured data
        self.measured_data_view = TunerMeasuredDataTreeView(self)

        self.add(Gtk.Label(label="Статус тюнера"))
        self.add(self.status_color_bar)
        self.add(Gtk.HSeparator())
        self.add(Gtk.Label(label="Параметры сигнала"))
        self.add(self.signal_params_view)
        self.add(Gtk.HSeparator())
        self.add(Gtk.Label(label="Измеренные параметры"))
        self.add(self.measured_data_view)

    def set_tuner_status_text_and_color(self, status):
        if status == 0x8000:
            self.no_device = True
        else:
            self.no_device = False
            self.status_ok = True
            # FIXME: change 0x1, 0x2 to constants
            self.level_ok = bool(status & 0x1)
            self.lock_ok = bool(status & 0x2)

        if self.no_device is True:
            self.status_color_bar.set_text("Нет данных от тюнера")
        elif self.level_ok is False:
            self.status_color_bar.set_text("Низкий уровень сигнала")
        elif self.lock_ok is False:
            self.status_color_bar.set_text("Сигнал не захвачен")
        else:
            self.status_color_bar.set_text("Есть сигнал")
        self.status_color_bar.queue_draw()

    def on_color_label_draw(self, widget, cr):
        rect = widget.get_allocation()
        cr.rectangle(0, 0, rect.width, rect.height)
        if self.no_device is True:
            cr.set_source_rgba(1.0, 0.4, 0.4, 0.6)
        elif self.status_ok is False:
            cr.set_source_rgba(1.0, 1.0, 0.4, 0.6)
        elif (self.level_ok is False) or (self.lock_ok is False):
            cr.set_source_rgba(1.0, 1.0, 0.4, 0.6)
        else:
            cr.set_source_rgba(0.4, 1.0, 0.4, 0.6)

        cr.fill()

