from gi.repository import Gtk

from Gui.BaseDialog import BaseDialog
from Gui.AnalysisSettingsDialog import SettingEntry
from Gui import Spacing


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


class ComboBox(Gtk.Box):
    def __init__(self, label, store):
        Gtk.Box.__init__(self)

        self.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.set_hexpand(True)
        self.set_vexpand(False)
        self.set_spacing(Spacing.COL_SPACING)

        # value entry
        self.combobox = Gtk.ComboBox.new_with_model(store)
        self.combobox.set_hexpand(True)
        self.combobox.set_vexpand(False)
        self.combobox.set_halign(Gtk.Align.END)
        self.combobox.set_valign(Gtk.Align.CENTER)
        self.combobox.set_size_request(150, -1)
        renderer_text = Gtk.CellRendererText()
        self.combobox.pack_start(renderer_text, True)
        self.combobox.add_attribute(renderer_text, "text", 0)
        self.combobox.set_active(0)
        #self.combobox.set_entry_text_column(0)

        # setting name
        self.label = Gtk.Label(label=label)
        self.label.set_hexpand(True)
        self.label.set_vexpand(False)
        self.label.set_halign(Gtk.Align.START)
        self.label.set_valign(Gtk.Align.CENTER)

        self.add(self.label)
        self.add(self.combobox)

        self.show_all()


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


class TunerSettingsDialog(BaseDialog):
    def __init__(self, parent):
        BaseDialog.__init__(self, "Настройки ТВ тюнера", parent)

        mainBox = self.get_content_area()

        self.standard_model = Gtk.ListStore(str, int)
        self.standard_model.append(["DVB-T2", 3])
        self.standard_model.append(["DVB-T", 6])
        self.standard_model.append(["DVB-C", 9])

        # standard selection page
        self.standard_box = Gtk.Box()
        self.standard_box.set_spacing(Spacing.ROW_SPACING)
        self.standard_box.set_border_width(Spacing.BORDER)
        self.standard_box.set_orientation(Gtk.Orientation.VERTICAL)
        self.standard_box.add(ComboBox("Выбор стандарта ТВ сигнала",
                                       self.standard_model))
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

        self.show_all()

