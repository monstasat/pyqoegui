from gi.repository import Gtk

from Gui.BaseDialog import BaseDialog
from Gui.BaseDialog import ComboBox
from Gui.TunerSettingsDialog.TunerStatusBox import TunerStatusBox
from Gui.TunerSettingsDialog.TunerSettingsBox import TunerSettingsBox
from Gui import Spacing
from Control import TunerSettingsModel as tm


# dialog for managing tuner settings
class TunerSettingsDialog(BaseDialog):
    def __init__(self, parent):
        BaseDialog.__init__(self, "Настройки ТВ тюнера", parent)

        mainBox = self.get_content_area()

        self.store = parent.tunerSettingsStore

        self.standard_model = Gtk.ListStore(str, int)
        self.standard_model.append(["DVB-T2", 3])
        self.standard_model.append(["DVB-T", 6])
        self.standard_model.append(["DVB-C", 9])

        # standard selection page
        self.standard_box = Gtk.Box()
        self.standard_box.set_spacing(Spacing.ROW_SPACING)
        self.standard_box.set_border_width(Spacing.BORDER)
        self.standard_box.set_orientation(Gtk.Orientation.VERTICAL)
        self.standard_combo = ComboBox("Выбор стандарта ТВ сигнала",
                                       self.standard_model)
        self.standard_box.add(self.standard_combo)
        self.standard_box.show_all()

        # standard settings pages
        self.dvbt2_box = TunerSettingsBox('DVB-T2')
        self.dvbt_box = TunerSettingsBox('DVB-T')
        self.dvbc_box = TunerSettingsBox('DVB-C')
        self.status_box = TunerStatusBox()

        # fill page list with created pages
        self.pages = []
        self.pages.append((
            self.standard_box,
            "standard",
            "Выбор стандарта"))
        self.pages.append((
            self.dvbt2_box,
            "dvbt2",
            "Настройки DVB-T2"))
        self.pages.append((
            self.dvbt_box,
            "dvbt",
            "Настройки DVB-T"))
        self.pages.append((
            self.dvbc_box,
            "dvbc",
            "Настройки DVB-C"))
        self.pages.append((
            self.status_box,
            "status",
            "Статус сигнала"))

        # create stack
        self.stack = Gtk.Stack(halign=Gtk.Align.FILL, hexpand=True)

        # set stack transition type
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_UP_DOWN)

        # add pages to stack
        for page in self.pages:
            self.stack.add_titled(page[0], page[1], page[2])

        # create stack sidebar
        self.stackSidebar = Gtk.StackSidebar(
            vexpand=True,
            hexpand=False,
            halign=Gtk.Align.START)
        self.stackSidebar.set_stack(self.stack)
        self.stackSidebar.show()

        # configure main container orientation
        mainBox.set_orientation(Gtk.Orientation.HORIZONTAL)
        # pack items to main container
        mainBox.pack_start(self.stackSidebar, False, False, 0)
        separator = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        mainBox.pack_start(separator, False, False, 0)
        mainBox.pack_start(self.stack, True, True, 0)

        # connect to show signal
        self.connect('show', self.on_shown)

    # when the dialog is shown
    def on_shown(self, widget):
        BaseDialog.on_shown(self, widget)
        self.update_values()

    # apply values from spin buttons to model
    def apply_settings(self):
        device_box = self.standard_box.get_children()[0]
        device = device_box.combobox.get_active()

        settings = [[device],
                    [self.dvbt2_box.frequency],
                    [self.dvbt2_box.bandwidth],
                    [self.dvbt2_box.plp_id],
                    [self.dvbt_box.frequency],
                    [self.dvbt_box.bandwidth],
                    [self.dvbc_box.frequency]]

        self.store.set_settings(settings)

    # update values in controls buttons
    def update_values(self):
        self.standard_combo.combobox.set_active(
            self.store.get_value_by_index(self.store.device))
        self.dvbt2_box.frequency = self.store.get_value_by_index(
            self.store.dvbt2_freq)
        self.dvbt2_box.bandwidth = self.store.get_value_by_index(
            self.store.dvbt2_bw)
        self.dvbt2_box.plp_id = self.store.get_value_by_index(
            self.store.dvbt2_plpid)
        self.dvbt_box.frequency = self.store.get_value_by_index(
            self.store.dvbt_freq)
        self.dvbt_box.bandwidth = self.store.get_value_by_index(
            self.store.dvbt_bw)
        self.dvbc_box.frequency = self.store.get_value_by_index(
            self.store.dvbc_freq)

    def set_new_tuner_params(self, status, modulation, params):
        self.status_box.signal_params_view.set_signal_params(modulation,
                                                             params)
        self.status_box.set_tuner_status_text_and_color(status)
        if status == 0x8000:
            self.status_box.measured_data_view.store_filter.refilter()
            self.status_box.signal_params_view.store_filter.refilter()

    def set_new_measured_data(self, measured_data):
        self.status_box.measured_data_view.set_measured_params(measured_data)

