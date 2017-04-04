from gi.repository import Gtk

from Control.DVBTunerConstants import *
from Gui.BaseDialog import BaseDialog
from Gui.BaseDialog import ComboBox
from Gui.TunerSettingsDialog.TunerPage import TunerPage
from Gui.TunerSettingsDialog.TunerStatusBox import TunerStatusBox
from Gui.TunerSettingsDialog.TunerSettingsBox import TunerSettingsBox
from Gui.Icon import Icon
from Gui import Spacing


# dialog for managing tuner settings
class TunerSettingsDialog(BaseDialog):
    def __init__(self, parent, tuner_settings):
        BaseDialog.__init__(self, "Настройки ТВ тюнера", parent.window)

        self.tuner_idxs = set([])

        mainBox = self.get_content_area()
        mainBox.set_halign(Gtk.Align.FILL)
        mainBox.set_valign(Gtk.Align.FILL)
        mainBox.set_hexpand(True)
        mainBox.set_vexpand(True)

        self.tuner_settings = tuner_settings.copy()

        self.standard_model = Gtk.ListStore(str, int)
        self.standard_model.append(["DVB-T2", DVBT2])
        self.standard_model.append(["DVB-T", DVBT])
        self.standard_model.append(["DVB-C", DVBC])

        # tuner info box
        self.tuner_status = {}
        tuner_info_btn = Gtk.Button(image=Icon("dialog-information"))
        tuner_info_btn.connect("clicked", self.show_tuner_info)
        self.header.pack_end(tuner_info_btn)

        # tuner slot selector
        self.slot_selector = Gtk.Notebook()
        self.slot_selector.set_scrollable(False)
        self.slot_selector.set_show_border(False)

        self.slots = {}

        for slot_id in range(4):
            slot = TunerPage(slot_id, tuner_settings, self.standard_model)
            # slot.set_sensitive(False)
            self.slots.update(dict([(slot_id, slot), ]))
            self.slot_selector.append_page(
                self.slots[slot_id],
                Gtk.Label(label="Модуль " + str(slot_id + 1)))

        # pack items to main container
        mainBox.pack_start(self.slot_selector, True, True, 0)
        self.update_values(self.tuner_settings)

    def show_tuner_info(self, widget):

        serial = self.tuner_status.get("serial", -1)
        serial = "-" if (serial == -1) else hex(serial)
        hw_ver = self.tuner_status.get("hw_ver", -1)
        hw_ver = "-" if (hw_ver == -1) else hex(hw_ver)
        fpga_ver = self.tuner_status.get("fpga_ver", -1)
        fpga_ver = "-" if (fpga_ver == -1) else hex(fpga_ver)
        soft_ver = self.tuner_status.get("soft_ver", -1)
        soft_ver = "-" if (soft_ver == -1) else hex(soft_ver)

        aboutDlg = Gtk.MessageDialog(self,
                                     Gtk.DialogFlags.MODAL,
                                     Gtk.MessageType.INFO,
                                     Gtk.ButtonsType.OK,
                                     "О тюнере DVB-T/T2/C")
        s = "Серийный номер: %s\n" \
            "Аппаратная версия: %s\n" \
            "Версия FPGA: %s\n" \
            "Программная версия: %s" % \
            (serial, hw_ver, fpga_ver, soft_ver)
        aboutDlg.format_secondary_text(s)
        aboutDlg.run()
        aboutDlg.destroy()

    def update_slots(self, new_indexes):
        self.tuner_idxs = set(new_indexes)
        # for k,slot in self.slots.items():
        #     slot.set_sensitive(k in self.tuner_idxs)

    # return tuner settings
    def get_tuner_settings(self):

        tuner_settings = {}
        for i,slot in self.slots.items():
            slot_dic = dict([('device', slot.standard_combo.combobox.get_active()),
                             ('t2_freq', slot.dvbt2_box.frequency),
                             ('t2_bw', slot.dvbt2_box.bandwidth),
                             ('t2_plp_id', slot.dvbt2_box.plp_id),
                             ('t_freq', slot.dvbt_box.frequency),
                             ('t_bw', slot.dvbt_box.bandwidth),
                             ('c_freq', slot.dvbc_box.frequency)])
            tuner_settings.update({int(slot.slot_id): slot_dic})
            
        return tuner_settings

    # update values in controls buttons
    def update_values(self, tuner_settings):
        # update tuner settings list
        self.tuner_settings = tuner_settings

        for k,v in self.tuner_settings.items():
            try:
                slot = self.slots[int(k)]
            except (IndexError, ValueError):
                pass
            else:
                slot.on_new_tuner_settings(v)

    def on_new_devinfo(self, devinfo):
        self.tuner_status = devinfo
        if "connected" in devinfo:
            connected = devinfo["connected"]
            if connected is False:
                self.update_slots(set([]))

        if "hw_cfg" in devinfo and connected:
            hw_cfg = devinfo["hw_cfg"]
            indexes = []
            for idx in range(4):
                if (hw_cfg & (2**idx)) > 0:
                    indexes.append(idx)

            if len(self.tuner_idxs.symmetric_difference(indexes)) > 0:
                self.update_slots(indexes)

        for i,slot in self.slots.items():
            slot.on_new_devinfo(devinfo)

    def on_new_meas(self, meas):
        id = meas.get("id", None)
        if id is not None:
            if id in self.slots:
                self.slots[id].on_new_meas(meas)

    def on_new_params(self, params):
        id = params.get("id", None)
        if id is not None:
            if id in self.slots:
                self.slots[id].on_new_params(params)
        # self.status_box.signal_params_view.set_signal_params(modulation,
        #                                                      params)
        # self.status_box.measured_data_view.device = \
        #                         self.status_box.signal_params_view.device
        # self.status_box.set_tuner_status_text_and_color(status)
        # if status == 0x8000:
        #     self.status_box.measured_data_view.store_filter.refilter()
        #     self.status_box.signal_params_view.store_filter.refilter()


