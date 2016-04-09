from gi.repository import Gtk

from Gui.BaseDialog import BaseDialog
from Gui.BaseDialog import ComboBox
from Gui.TunerSettingsDialog.TunerStatusBox import TunerStatusBox
from Gui.TunerSettingsDialog.TunerSettingsBox import TunerSettingsBox
from Gui import Spacing


# dialog for managing tuner settings
class TunerSettingsDialog(BaseDialog):
    def __init__(self, parent, tuner_settings):
        BaseDialog.__init__(self, "Настройки ТВ тюнера", parent.window)

        mainBox = self.get_content_area()

        self.tuner_settings = tuner_settings

        self.standard_model = Gtk.ListStore(str, int)
        self.standard_model.append(["DVB-T2", 3])
        self.standard_model.append(["DVB-T", 6])
        self.standard_model.append(["DVB-C", 9])

        # standard selection page
        self.standard_box = Gtk.Box(spacing=Spacing.ROW_SPACING,
                                    border_width=Spacing.BORDER,
                                    orientation=Gtk.Orientation.VERTICAL)
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
        self.pages.append((self.standard_box, "standard", "Выбор стандарта"))
        self.pages.append((self.dvbt2_box, "dvbt2", "Настройки DVB-T2"))
        self.pages.append((self.dvbt_box, "dvbt", "Настройки DVB-T"))
        self.pages.append((self.dvbc_box, "dvbc", "Настройки DVB-C"))
        self.pages.append((self.status_box, "status", "Статус сигнала"))

        # create stack
        self.stack = Gtk.Stack(halign=Gtk.Align.FILL, hexpand=True)
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_UP_DOWN)
        list(map(lambda x: self.stack.add_titled(x[0], x[1], x[2]),
                 self.pages))

        # create stack sidebar
        self.stackSidebar = Gtk.StackSidebar(vexpand=True, hexpand=False,
                                             halign=Gtk.Align.START,
                                             stack=self.stack)
        # create separator
        separator = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)

        # configure main container orientation
        mainBox.set_orientation(Gtk.Orientation.HORIZONTAL)
        # pack items to main container
        mainBox.pack_start(self.stackSidebar, False, False, 0)
        mainBox.pack_start(separator, False, False, 0)
        mainBox.pack_start(self.stack, True, True, 0)

        self.update_values(self.tuner_settings)

    # return tuner settings
    def get_tuner_settings(self):
        device_box = self.standard_box.get_children()[0]
        device = device_box.combobox.get_active()

        self.tuner_settings['device'] = device
        self.tuner_settings['t2_freq'] = self.dvbt2_box.frequency
        self.tuner_settings['t2_bw'] = self.dvbt2_box.bandwidth
        self.tuner_settings['t2_plp_id'] = self.dvbt2_box.plp_id
        self.tuner_settings['t_freq'] = self.dvbt_box.frequency
        self.tuner_settings['t_bw'] = self.dvbt_box.bandwidth
        self.tuner_settings['c_freq'] = self.dvbc_box.frequency

        return self.tuner_settings

    # update values in controls buttons
    def update_values(self, tuner_settings):
        # update tuner settings list
        self.tuner_settings = tuner_settings

        self.standard_combo.combobox.set_active(tuner_settings['device'])
        self.dvbt2_box.frequency = tuner_settings['t2_freq']
        self.dvbt2_box.bandwidth = tuner_settings['t2_bw']
        self.dvbt2_box.plp_id = tuner_settings['t2_plp_id']
        self.dvbt_box.frequency = tuner_settings['t_freq']
        self.dvbt_box.bandwidth = tuner_settings['t_bw']
        self.dvbc_box.frequency = tuner_settings['c_freq']

    def set_new_tuner_params(self, status, modulation, params):
        self.status_box.signal_params_view.set_signal_params(modulation,
                                                             params)
        self.status_box.measured_data_view.device = \
                                self.status_box.signal_params_view.device
        self.status_box.set_tuner_status_text_and_color(status)
        if status == 0x8000:
            self.status_box.measured_data_view.store_filter.refilter()
            self.status_box.signal_params_view.store_filter.refilter()

    def set_new_measured_data(self, measured_data):
        self.status_box.measured_data_view.set_measured_params(measured_data)

