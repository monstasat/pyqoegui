from gi.repository import Gtk

from Gui.TunerSettingsDialog.TunerStatusTreeView import TunerStatusTreeView
from Gui.TunerSettingsDialog.TunerMeasuredDataTreeView import \
                             TunerMeasuredDataTreeView
from Gui import Spacing


# box with widgets for status displaying
class TunerStatusBox(Gtk.Box):
    def __init__(self, slot_id, settings):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL,
                         spacing=Spacing.ROW_SPACING,
                         border_width=Spacing.BORDER,
                         valign=Gtk.Align.START)

        self.slot_id = slot_id
        self.settings = settings.copy()
        # current tuner status
        self.host_connected = False
        self.slot_connected = False
        self.lock = False
        # status color bar
        self.status = Gtk.Label(label="Нет данных от тюнера",
                                hexpand=True,
                                halign=Gtk.Align.CENTER)
        self.status_box = Gtk.Box(hexpand=True,
                                  vexpand=True,
                                  halign=Gtk.Align.FILL)
        self.status_box.set_size_request(-1, 40)
        self.status_box.add(self.status)
        self.status_box.connect('draw', self.on_draw)
        # signal parameters
        self.signal_params_view = TunerStatusTreeView(self)
        # measured data
        self.measured_data_view = TunerMeasuredDataTreeView(slot_id, settings)

        self.add(Gtk.Label(label="Статус тюнера"))
        self.add(self.status_box)
        self.add(Gtk.HSeparator())
        self.add(Gtk.Label(label="Измеренные параметры"))
        self.add(self.measured_data_view)

    def set_tuner_status_text_and_color(self):

        if self.host_connected is False:
            self.status.set_text("Нет данных от тюнера")
        elif self.slot_connected is False:
            self.status.set_text("Нет данных от модуля")
        elif self.lock is False:
            self.status.set_text("Нет сигнала")
        else:
            self.status.set_text("Есть сигнал")

    def on_draw(self, widget, cr):
        rect = widget.get_allocation()
        cr.rectangle(0, 0, rect.width, rect.height)
        if self.host_connected is False or \
           self.slot_connected is False:
            cr.set_source_rgba(1.0, 0.4, 0.4, 0.6)
        elif self.lock is False:
            cr.set_source_rgba(1.0, 1.0, 0.4, 0.6)
        else:
            cr.set_source_rgba(0.4, 1.0, 0.4, 0.6)

        cr.fill()

    def on_new_tuner_settings(self, settings):
        self.settings.update(settings)
        self.measured_data_view.on_new_tuner_settings(self.settings)

    def on_new_devinfo(self, devinfo):
        if "connected" in devinfo:
            host_connected = devinfo["connected"]
            if self.host_connected != host_connected:
                self.host_connected = host_connected
                self.set_tuner_status_text_and_color()

        if "hw_cfg" in devinfo:
            hw_cfg = devinfo["hw_cfg"]
            slot_connected = (hw_cfg & (2**self.slot_id)) > 0
            if self.slot_connected != slot_connected:
                self.slot_connected = slot_connected
                self.set_tuner_status_text_and_color()

    def on_new_meas(self, meas):
        lock = meas.get("lock", False)
        if self.lock != lock:
            self.lock = lock
            self.set_tuner_status_text_and_color()

        self.measured_data_view.set_measured_params(meas)

    def on_new_params(self, params):
        pass
