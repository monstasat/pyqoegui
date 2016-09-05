from gi.repository import Gtk

from Gui.BaseDialog import BaseDialog
from Gui.BaseDialog import ComboBox
from Gui.TunerSettingsDialog.TunerPage import TunerPage
from Gui.TunerSettingsDialog.TunerStatusBox import TunerStatusBox
from Gui.TunerSettingsDialog.TunerSettingsBox import TunerSettingsBox
from Gui import Spacing


# dialog for managing tuner settings
class TunerSettingsDialog(BaseDialog):
    def __init__(self, parent, tuner_settings):
        BaseDialog.__init__(self, "Настройки ТВ тюнера", parent.window)

        mainBox = self.get_content_area()
        mainBox.set_halign(Gtk.Align.FILL)
        mainBox.set_valign(Gtk.Align.FILL)
        mainBox.set_hexpand(True)
        mainBox.set_vexpand(True)

        self.tuner_settings = tuner_settings

        self.standard_model = Gtk.ListStore(str, int)
        self.standard_model.append(["DVB-T2", 3])
        self.standard_model.append(["DVB-T", 6])
        self.standard_model.append(["DVB-C", 9])

        # tuner slot selector
        self.slot_selector = Gtk.Notebook()
        self.slot_selector.set_scrollable(False)
        self.slot_selector.set_show_border(False)

        self.slots = []

        for slot_id in range(4):
            self.slots.append(TunerPage(slot_id, tuner_settings, self.standard_model))
            self.slot_selector.append_page(self.slots[slot_id], Gtk.Label(label="Модуль " + str(slot_id + 1)))

        # pack items to main container
        mainBox.pack_start(self.slot_selector, True, True, 0)

        self.update_values(self.tuner_settings)

    # return tuner settings
    def get_tuner_settings(self):

        tuner_settings = {}
        for slot in self.slots:
            slot_dic = dict([('device', slot.standard_combo.combobox.get_active()),
                             ('t2_freq', slot.dvbt2_box.frequency),
                             ('t2_bw', slot.dvbt2_box.bandwidth),
                             ('t2_plp_id', slot.dvbt2_box.plp_id),
                             ('t_freq', slot.dvbt_box.frequency),
                             ('t_bw', slot.dvbt_box.bandwidth),
                             ('c_freq', slot.dvbc_box.frequency)])
            tuner_settings.update({slot.slot_id: slot_dic})

        return self.tuner_settings

    # update values in controls buttons
    def update_values(self, tuner_settings):
        # update tuner settings list
        self.tuner_settings = tuner_settings

        for k,v in self.tuner_settings.items():
            try:
                slot = self.slots[int(k)]
            except (IndexError, ValueError):
                slot = None
            if slot is not None:
                slot.standard_combo.combobox.set_active(v['device'])
                slot.dvbt2_box.frequency = v['t2_freq']
                slot.dvbt2_box.bandwidth = v['t2_bw']
                slot.dvbt2_box.plp_id = v['t2_plp_id']
                slot.dvbt_box.frequency = v['t_freq']
                slot.dvbt_box.bandwidth = v['t_bw']
                slot.dvbc_box.frequency = v['c_freq']

    def set_new_tuner_params(self, status, modulation, params):
        pass
        # self.status_box.signal_params_view.set_signal_params(modulation,
        #                                                      params)
        # self.status_box.measured_data_view.device = \
        #                         self.status_box.signal_params_view.device
        # self.status_box.set_tuner_status_text_and_color(status)
        # if status == 0x8000:
        #     self.status_box.measured_data_view.store_filter.refilter()
        #     self.status_box.signal_params_view.store_filter.refilter()

    def set_new_measured_data(self, measured_data):
        pass
       # self.status_box.measured_data_view.set_measured_params(measured_data)

