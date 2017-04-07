from gi.repository import Gtk, Gdk

from Control.DVBTunerConstants import *
from Gui.BaseDialog import BaseDialog
from Gui.BaseDialog import ComboBox
from Gui.Placeholder import Placeholder
from Gui.TunerSettingsDialog.TunerPage import TunerPage
from Gui.TunerSettingsDialog.TunerStatusBox import TunerStatusBox
from Gui.TunerSettingsDialog.TunerSettingsBox import TunerSettingsBox
from Gui.Icon import Icon
from Gui import Spacing


# dialog for managing tuner settings
class TunerSettingsDialog(BaseDialog):
    def __init__(self, parent, tuner_settings):
        BaseDialog.__init__(self, "Настройки ТВ тюнера", parent.window)

        css = """
        .TunerNotebook stack {
        background-color: transparent;
        }
        .TunerNotebook stack:active {
        background-color: transparent;
        }
        """

        self.tuner_idxs = set([])
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
        cssprovider = Gtk.CssProvider()
        cssprovider.load_from_data(bytes(css.encode()))
        screen = Gdk.Screen.get_default()
        stylecontext = Gtk.StyleContext()
        stylecontext.add_provider_for_screen(screen, cssprovider,
                                             Gtk.STYLE_PROVIDER_PRIORITY_USER)
        context = self.slot_selector.get_style_context()
        context.add_class("TunerNotebook")


        self.slots = {}

        overlay = Gtk.Overlay(valign=Gtk.Align.FILL,
                              hexpand=True,
                              vexpand=True)
        overlay.add(self.slot_selector)
        self.holder = Placeholder("network-wireless-no-route-symbolic",
                                  'Тюнер не обнаружен',
                                  72)
        overlay.add_overlay(self.holder)

        # pack items to main container
        mainBox = self.get_content_area()
        mainBox.set_halign(Gtk.Align.FILL)
        mainBox.set_valign(Gtk.Align.FILL)
        mainBox.set_hexpand(True)
        mainBox.set_vexpand(True)
        mainBox.pack_start(overlay, True, True, 0)

        self.connect('show', self.on_shown)

        self.update_values(self.tuner_settings)

    def on_shown(self, widget):
        BaseDialog.on_shown(self, widget)
        if self.slot_selector.get_n_pages() == 0:
            self.slot_selector.hide()
            self.holder.show_all()
        else:
            self.holder.hide()
            self.slot_selector.show_all()

    def add_slot(self, index):
        settings = self.tuner_settings.get(index, {})
        slot = TunerPage(index, settings, self.standard_model)
        slot.set_property("margin_top", 5)
        if index in self.slots:
            self.slots[index].destroy()

        self.slots.update(dict([(index, slot), ]))
        self.slot_selector.append_page(
            slot,
            Gtk.Label("Модуль " + str(index + 1)))

    def remove_slot(self, index):
        if index in self.slots:
            slot = self.slots.pop(index)
            slot.destroy()

        self.show_all()

    def update_slots(self, new_indexes):
        """
        Handles case when modules number changes

        new indexes - indexes of modules which are currently available
        """

        to_remove = self.tuner_idxs.difference(set(new_indexes))
        to_add = set(new_indexes).difference(self.tuner_idxs)
        for i in to_remove:
            self.remove_slot(i)
        for i in to_add:
            self.add_slot(i)

        for i,slot in self.slots.items():
            self.slot_selector.reorder_child(slot,i)

        if self.slot_selector.get_n_pages() == 0:
            self.slot_selector.hide()
            self.holder.show_all()
        else:
            self.holder.hide()
            self.slot_selector.show_all()

        self.tuner_idxs = set(new_indexes)

    def show_tuner_info(self, widget):
        """
        Shows modal dialog with some tuner info inside, like
        serial number and different versions
        """

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

    def get_tuner_settings(self):
        """Return tuner settings (for all modules) to caller"""

        tuner_settings = {}
        for i,slot in self.slots.items():
            slot_dic = dict([('device', slot.standard_combo.combobox.get_active()),
                             ('t2_freq', slot.dvbt2_box.frequency),
                             ('t2_bw', slot.dvbt2_box.bandwidth),
                             ('t2_plp_id', slot.dvbt2_box.plp_id),
                             ('t_freq', slot.dvbt_box.frequency),
                             ('t_bw', slot.dvbt_box.bandwidth),
                             ('c_freq', slot.dvbc_box.frequency),
                             ('c_bw', slot.dvbc_box.bandwidth)])
            tuner_settings.update({int(slot.slot_id): slot_dic})
            
        return tuner_settings

    def update_values(self, tuner_settings):
        """Updates tuner settings in widgets"""

        self.tuner_settings = tuner_settings.copy()

        for k,v in self.tuner_settings.items():
            try:
                slot = self.slots[int(k)]
            except:
                pass
            else:
                slot.on_new_tuner_settings(v)

    def on_new_devinfo(self, devinfo):
        self.tuner_status = devinfo

        if "hw_cfg" in devinfo:
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

    def on_new_plp_list(self, plp_list):
        id = plp_list.get("id", None)
        if id is not None:
            if id in self.slots:
                self.slots[id].on_new_plp_list(plp_list)


