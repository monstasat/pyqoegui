from gi.repository import Gtk

from Gui.BaseDialog import BaseDialog
from Gui.BaseDialog import SettingEntry
from Gui.BaseDialog import ComboBox
from Gui import Spacing
from Control import TunerSettingsModel


# list store containing terrestrial frequencies
class TerrestrialFrequencyModel(Gtk.ListStore):
    def __init__(self):
        Gtk.ListStore.__init__(self, str, int, int)

        # fill the model with values
        self.fill_model()

    # fill model with frequency values
    def fill_model(self):

        # tv channel number
        ch = 0
        # tv channel frequency
        freq = 0

        for index in range(1, 57):
            if index == 0:
                ch = 0
                freq = 0
            elif index <= 7:
                ch = index + 5
                freq = (ch*8 + 130) * 1000000
            else:
                ch = index + 13
                freq = (ch*8 + 306) * 1000000
            ch_string = 'ТВК %d (%g МГц)' % (ch, freq / 1000000)
            self.append([ch_string, ch, freq])


# list store containing cable frequencies
class CableFrequencyModel(Gtk.ListStore):
    def __init__(self):
        Gtk.ListStore.__init__(self, str, int, int, bool)

        # fill the model with values
        self.fill_model()

    # fill model with frequency values
    def fill_model(self):

        # tv channel number
        ch = 0
        # tv channel frequency
        freq = 0
        # special channel flag
        spec = False

        for index in range(1, 100):
            if index == 0:
                ch = 0
                freq = 0
                spec = False
            elif index == 1:
                ch = index
                freq = 52500000
                spec = False
            elif index == 2:
                ch = index
                freq = (index*8 + 46) * 1000000
                spec = False
            elif (index >= 3) and (index <= 5):
                ch = index
                freq = (index*8 + 56) * 1000000
                special = False
            elif (index >= 6) and (index <= 13):
                ch = index - 5
                freq = (index*8 + 66) * 1000000
                spec = True
            elif (index >= 14) and (index <= 17):
                ch = index - 8
                freq = (index*8 + 66) * 1000000
                spec = False
            elif (index >= 18) and (index <= 20):
                ch = index - 8
                freq = (index*8 + 66) * 1000000
                spec = False
            elif (index >= 21) and (index <= 50):
                ch = index - 10
                freq = (index*8 + 66) * 1000000
                spec = True
            else:
                ch = index - 30
                freq = (index*8 + 66) * 1000000
                spec = False
            if spec is True:
                ch_string = 'СТВК %d (%g МГц)' % (ch, freq / 1000000)
            else:
                ch_string = 'ТВК %d (%g МГц)' % (ch, freq / 1000000)
            self.append([ch_string, ch, freq, spec])


# dialog page with setting boxes
class TvStandardSettingsBox(Gtk.Box):

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
            bw = TunerSettingsModel.BW8
        return bw

    # bandwidth setter
    @bandwidth.setter
    def bandwidth(self, value):
        self.bw_box.combobox.set_active(value)

    # plp id getter
    @property
    def plp_id(self):
        return int(self.plp_box.spinBtn.get_value())

    # plp id setter
    @plp_id.setter
    def plp_id(self, value):
        self.plp_box.spinBtn.set_value(value)


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
        self.dvbt2_box = TvStandardSettingsBox('DVB-T2')
        self.dvbt_box = TvStandardSettingsBox('DVB-T')
        self.dvbc_box = TvStandardSettingsBox('DVB-C')

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

