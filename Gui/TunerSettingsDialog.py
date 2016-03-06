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


# status settings box
class StatusBox(Gtk.Box):
    def __init__(self):
        Gtk.Box.__init__(self)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_spacing(Spacing.ROW_SPACING)
        self.set_border_width(Spacing.BORDER)

        # current tv standard
        self.device = 0xff

        # current tuner status
        self.status_ok = False
        self.level_ok = False
        self.lock_ok = False

        # current measured data
        self.measured_data = [0, False, 0, False, 0, False, 0, False]

        # status color bar
        self.status_color_bar = Gtk.Label(label="Нет данных от тюнера")
        self.status_color_bar.set_size_request(-1, 40)
        self.status_color_bar.connect('draw', self.on_color_label_draw)

        # signal parameters

        self.signal_params = Gtk.Label(label="Параметры сигнала:\n -")
        self.signal_params.set_halign(Gtk.Align.START)

        # measured data

        self.measured_data_label = Gtk.Label(label="Измеренные параметры:\n -")
        self.measured_data_label.set_halign(Gtk.Align.START)

        self.add(self.status_color_bar)
        self.add(Gtk.HSeparator())
        self.add(self.signal_params)
        self.add(Gtk.HSeparator())
        self.add(self.measured_data_label)

    def set_signal_params_text(self, modulation, params):
        print(modulation, params)

        # DVB-C
        if 3 <= modulation <= 3:
            self.device = TunerSettingsModel.DVBC
            if modulation == 3:
                mod_txt = "64-QAM"
            elif modulation == 4:
                mod_txt = "128-QAM"
            elif modulation == 5:
                mod_txt = "256-QAM"
            sr = str(params)
            text = "Параметры сигнала: \n" + \
                   "Стандарт сигнала: DVB-C\n" + \
                   "Модуляция: " + mod_txt + "\n" + \
                   "Символьная скорость канала: " + sr + \
                   "\n"
        # DVB-T
        elif 4 <= modulation <= 8:
            self.device = TunerSettingsModel.DVBT
            fft = (params & 0xC000) >> 14
            if fft == 0:
                fft_txt = "2K"
            elif fft == 1:
                fft_txt = "8K"
            else:
                fft_txt = "неизвестно"
            gi = (params & 0x3000) >> 12
            if gi == 0:
                gi_txt = "1/32"
            elif gi == 1:
                gi_txt = "1/16"
            elif gi == 2:
                gi_txt = "1/8"
            elif gi == 3:
                gi_txt = "1/4"
            else:
                gi_txt = "неизвестно"
            hierarchy = (params & 0xC00) >> 10
            if hierarchy == 0:
                hierarchy_txt = "без иерархии"
            elif hierarchy == 1:
                hierarchy_txt = "a = 1"
            elif hierarchy == 2:
                hierarchy_txt = "a = 2"
            elif hierarchy == 3:
                hierarchy_txt = "a = 4"
            spectrum = (params & 0x200) >> 9
            if spectrum == 0:
                spectrum_txt = "прямой"
            elif spectrum == 1:
                spectrum_txt = "инверсный"
            else:
                spectrum_txt = "неизвестно"
            fec_lp = (params & 0x1C0) >> 6
            if fec_lp == 0:
                fec_lp_txt = "1/2"
            elif fec_lp == 1:
                fec_lp_txt = "2/3"
            elif fec_lp == 2:
                fec_lp_txt = "3/4"
            elif fec_lp == 3:
                fec_lp_txt = "5/6"
            elif fec_lp == 4:
                fec_lp_txt = "7/8"
            else:
                fec_lp_txt = "неизвестно"
            fec_hp = (params & 0x38) >> 3
            if fec_hp == 0:
                fec_hp_txt = "1/2"
            elif fec_hp == 1:
                fec_hp_txt = "2/3"
            elif fec_hp == 2:
                fec_hp_txt = "3/4"
            elif fec_hp == 3:
                fec_hp_txt = "5/6"
            elif fec_hp == 4:
                fec_hp_txt = "7/8"
            else:
                fec_hp_txt = "неизвестно"
            bw = (params & 0x6) >> 1
            if bw ==  0:
                bw_txt = "6 МГц"
            elif bw == 1:
                bw_txt = "7 МГц"
            elif bw == 2:
                bw_txt = "8 МГц"
            else:
                bw_txt = "неизвестно"
            if modulation == 6:
                mod_txt = "QPSK"
            elif modulation == 7:
                mod_txt = "16-QAM"
            elif modulation == 8:
                mod_txt = "64-QAM"
            text = "Параметры сигнала: \n" + \
                   "Стандарт сигнала: DVB-T\n" + \
                   "Модуляция: " + mod_txt + "\n" + \
                   "Число поднесущих: " + fft_txt + "\n" + \
                   "Защитный интервал: " + gi_txt + "\n" + \
                   "Режим иерархии: " + hierarchy_txt + "\n" + \
                   "Спектр: " + spectrum_txt + "\n" + \
                   "Скорость кода LP: " + fec_lp_txt + "\n" + \
                   "Скорость кода HP: " + fec_hp_txt + "\n" + \
                   "Ширина канала: " + bw_txt + "\n" + \
                   "\n"
        # DVB-T2
        elif modulation == 9:
            self.device = TunerSettingsModel.DVBT2
            plp_id = params & 0x00ff
            qam_id = (params & 0x0f00) >> 8
            bw = (params & 0xc000) >> 14
            if qam_id == 0:
                mod_txt = "QPSK"
            elif qam_id == 1:
                mod_txt = "16-QAM"
            elif qam_id == 2:
                mod_txt = "64-QAM"
            elif qam_id == 3:
                mod_txt = "256-QAM"
            else:
                mod_txt = "неизвестно"

            if bw ==  0:
                bw_txt = "6 МГц"
            elif bw == 1:
                bw_txt = "7 МГц"
            elif bw == 2:
                bw_txt = "8 МГц"
            else:
                bw_txt = "неизвестно"

            text = "Параметры сигнала: \n" + \
                   "Стандарт сигнала: DVB-T2\n" + \
                   "Модуляция: " + mod_txt + "\n" + \
                   "PLP ID: " + str(plp_id) + "\n" + \
                   "Ширина канала: " + bw_txt + "\n"
        # unknown
        else:
            self.device = 0xff
            text = "Параметры сигнала: \n" + \
                    "Стандарт сигнала: неизвестно\n" \

        self.signal_params.set_text(text)

    def set_measured_params_text(self, data):

        # if mer was updated
        if data[1] is True:
            self.measured_data[0] = data[0]
        # if ber1 was updated
        if data[3] is True:
            self.measured_data[2] = data[2]
        # if ber2 was updated
        if data[5] is True:
            self.measured_data[4] = data[4]
        # if ber3 was updated
        if data[7] is True:
            self.measured_data[6] = data[6]

        mer_txt = "MER: " + str(self.measured_data[0])
        if self.device == TunerSettingsModel.DVBC:
            ber1_txt = "BER до декодера Рида-Соломона: " + \
                       ("%e" % self.measured_data[2])
            ber2_txt = "BER после декодера Рида-Соломона: " + \
                       ("%e" % self.measured_data[4])
            text = "Измеренные параметры: \n" + \
                   mer_txt + "\n" + ber1_txt + "\n" + ber2_txt + "\n"
        elif self.device == TunerSettingsModel.DVBT:
            ber1_txt = "BER до декодера Витерби: " + \
                       ("%e" % self.measured_data[2])
            ber2_txt = "BER до декодера Рида-Соломона: " + \
                       ("%e" % self.measured_data[4])
            ber3_txt = "BER после декодера Рида-Соломона: " + \
                       ("%e" % self.measured_data[6])
            text = "Измеренные параметры: \n" + \
                   mer_txt + \
                   "\n" + ber1_txt + \
                   "\n" + ber2_txt + \
                   "\n" + ber3_txt + "\n"
        elif self.device == TunerSettingsModel.DVBT2:
            ber1_txt = "BER до декодера LDPC: " + \
                       ("%e" % self.measured_data[2])
            ber2_txt = "BER до декодера BCH: " + \
                       ("%e" % self.measured_data[4])
            ber3_txt = "BER после декодера BCH: " + \
                       ("%e" % self.measured_data[6])
            text = "Измеренные параметры: \n" + \
                   mer_txt + \
                   "\n" + ber1_txt + \
                   "\n" + ber2_txt + \
                   "\n" + ber3_txt + "\n"
        else:
            text = "Измеренные параметры: \n" + \
                   " -" + "\n"

        self.measured_data_label.set_text(text)

    def set_tuner_status_text_and_color(self, status):
        self.status_ok = True
        self.level_ok = bool(status & 0x1)
        self.lock_ok = bool(status & 0x2)
        if self.level_ok is False:
            self.status_color_bar.set_text("Низкий уровень сигнала")
        elif self.lock_ok is False:
            self.status_color_bar.set_text("Сигнал не захвачен")
        else:
            self.status_color_bar.set_text("Настроено")
        self.status_color_bar.queue_draw()

    def on_color_label_draw(self, widget, cr):
        rect = widget.get_allocation()
        cr.rectangle(0, 0, rect.width, rect.height)
        if self.status_ok is False:
            cr.set_source_rgba(1.0, 0.4, 0.4, 0.6)
        elif (self.level_ok is False) or (self.lock_ok is False):
            cr.set_source_rgba(1.0, 1.0, 0.4, 0.6)
        else:
            cr.set_source_rgba(0.4, 1.0, 0.4, 0.6)
        cr.fill()


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
        self.status_box = StatusBox()

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
        self.status_box.set_signal_params_text(modulation, params)
        self.status_box.set_tuner_status_text_and_color(status)

    def set_new_measured_data(self, measured_data):
        self.status_box.set_measured_params_text(measured_data)

