import re

from gi.repository import Gtk

from Control.DVBTunerConstants import *
from Gui.BaseDialog import SettingEntry, ComboBox
from Gui.TunerSettingsDialog.TerrestrialFrequencyModel import \
                             TerrestrialFrequencyModel
from Gui.TunerSettingsDialog.CableFrequencyModel import CableFrequencyModel
from Gui.Icon import Icon
from Gui import Spacing


# box with widgets for tuner settings management
class TunerSettingsBox(Gtk.Box):

    def __init__(self, standard):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL,
                         spacing=Spacing.ROW_SPACING,
                         border_width=Spacing.BORDER)

        # save tv standard
        self.standard = standard
        self.plp_list = []

        # bandwidth model: text, number
        bw_model = Gtk.ListStore(str, int)
        bw_model.append(["6 МГц", BW6])
        bw_model.append(["7 МГц", BW7])
        bw_model.append(["8 МГц", BW8])

        # frequency model: dependent on tv standard
        if (standard == DVBT2) or (standard == DVBT):
            self.freq_model = TerrestrialFrequencyModel()
        elif standard == DVBC:
            self.freq_model = CableFrequencyModel()

        # create frequency combo box
        self.frequency_box = ComboBox("Частота ТВ канала", self.freq_model)
        self.frequency_box.combobox.set_size_request(170, -1)

        # create bandwidth combo box
        self.bw_box = ComboBox("Ширина полосы", bw_model)
        self.bw_box.combobox.set_size_request(170, -1)

        # create plp id spin box
        self.plp_btn = Gtk.MenuButton(name='plp', always_show_image=True,
                                                                                                                                                                                                                               has_tooltip=True, tooltip_text="Список найденных PLP",
                                      image=Icon('view-list-symbolic'),
                                      hexpand=False)

        self.plp_box = SettingEntry(0, "PLP ID", 0, 255,
                                    aux_widget=self.plp_btn)
        self.plp_box.spinBtn.set_increments(1, 10)
        self.plp_box.spinBtn.set_digits(0)
        self.plp_box.spinBtn.set_size_request(136, -1)

        # add widgets depending on standard
        self.add(self.frequency_box)
        self.add(self.bw_box)
        if standard == DVBT2:
            self.add(self.plp_box)

        self.show_all()

    def on_new_plp_list(self, plp_list):
        if self.plp_list != plp_list:
            self.plp_list = plp_list

        plps = self.plp_list.get('plps', [])
        if len(plps) > 0:
            plp_menu = Gtk.Menu()
            for plp in plps:
                item = Gtk.MenuItem(label=str(plp))
                item.connect("activate", self.on_plp_active, plp)
                plp_menu.add(item)

            plp_menu.show_all()
            self.plp_btn.set_popup(plp_menu)
        else:
            self.plp_btn.set_popup(None)

    def on_plp_active(self, widget, plp):
        try:
            self.plp_id = plp
        except:
            pass

    # frequency getter
    @property
    def frequency(self):
        freq_idx = self.frequency_box.combobox.get_active()
        # if no active item,
        # choose 586 MHz by default
        if freq_idx == -1:
            return 586000000
        else:
            iter_ = self.freq_model.get_iter(str(freq_idx))
            return self.freq_model[iter_][2]

    # frequency setter
    @frequency.setter
    def frequency(self, value):
        for i, row in enumerate(self.freq_model):
            if row[2] == value:
                self.frequency_box.combobox.set_active(i)

    # bandwidth getter
    @property
    def bandwidth(self):
        bw = self.bw_box.combobox.get_active()
        # if no active item, choose 8 MHz by default
        return bw if (bw != -1) else BW8

    # bandwidth setter
    @bandwidth.setter
    def bandwidth(self, value):
        if not value in (BW6, BW7, BW8):
            value = BW8
        self.bw_box.combobox.set_active(value)

    # plp id getter
    @property
    def plp_id(self):
        return int(self.plp_box.spinBtn.get_value())

    # plp id setter
    @plp_id.setter
    def plp_id(self, value):
        self.plp_box.spinBtn.set_value(value)

