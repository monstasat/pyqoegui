from gi.repository import Gtk

from Gui.BaseDialog import SettingEntry
from Gui.BaseDialog import ComboBox
from Gui.TunerSettingsDialog.TerrestrialFrequencyModel import \
                             TerrestrialFrequencyModel
from Gui.TunerSettingsDialog.CableFrequencyModel import CableFrequencyModel
from Gui import Spacing


# box with widgets for tuner settings management
class TunerSettingsBox(Gtk.Box):

    def __init__(self, standard):
        Gtk.Box.__init__(self)

        # modify box view
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_spacing(Spacing.ROW_SPACING)
        self.set_border_width(Spacing.BORDER)

        # save tv standard
        self.standard = standard

        # bandwidth model: text, number
        bw_model = Gtk.ListStore(str, int)
        bw_model.append(["6 МГц", 0])
        bw_model.append(["7 МГц", 1])
        bw_model.append(["8 МГц", 2])

        # frequency model: dependent on tv standard
        if (standard == 'DVB-T2') or (standard == 'DVB-T'):
            self.freq_model = TerrestrialFrequencyModel()
        elif standard == 'DVB-C':
            self.freq_model = CableFrequencyModel()

        # create frequency combo box
        self.frequency_box = ComboBox("Частота ТВ канала",
                                      self.freq_model)
        # set size
        self.frequency_box.combobox.set_size_request(170, -1)

        # create bandwidth combo box
        self.bw_box = ComboBox("Ширина полосы", bw_model)
        # set size
        self.bw_box.combobox.set_size_request(170, -1)

        # create plp id spin box
        self.plp_box = SettingEntry(0, "PLP ID", 0, 255)
        self.plp_box.spinBtn.set_increments(1, 10)
        self.plp_box.spinBtn.set_digits(0)
        # set size
        self.plp_box.spinBtn.set_size_request(170, -1)

        # add widgets depending on standard
        self.add(self.frequency_box)
        if (standard == 'DVB-T2') or (standard == 'DVB-T'):
            self.add(self.bw_box)
        if standard == 'DVB-T2':
            self.add(self.plp_box)

        self.show_all()

    # frequency getter
    @property
    def frequency(self):
        freq = 0
        freq_idx = self.frequency_box.combobox.get_active()
        # if no active item,
        # choose 586 MHz by default
        if freq_idx == -1:
            freq = 586000000
        else:
            iter_ = self.freq_model.get_iter(str(freq_idx))
            freq = self.freq_model[iter_][2]
        return freq

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
        # if no active item,
        # choose 8 MHz by default
        if bw == -1:
            bw = tm.BW8
        return bw

    # bandwidth setter
    @bandwidth.setter
    def bandwidth(self, value):
        if value > 2:
            value = 2
        if value < 0:
            value = 0
        self.bw_box.combobox.set_active(value)

    # plp id getter
    @property
    def plp_id(self):
        return int(self.plp_box.spinBtn.get_value())

    # plp id setter
    @plp_id.setter
    def plp_id(self, value):
        self.plp_box.spinBtn.set_value(value)

