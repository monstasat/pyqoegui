from gi.repository import Gtk

from Control.DVBTunerConstants import DVBC, DVBT, DVBT2


# tree view that displays tuner status
class TunerStatusTreeView(Gtk.TreeView):
    def __init__(self, parent):
        Gtk.TreeView.__init__(self, hexpand=True, vexpand=True,
                              halign=Gtk.Align.FILL, valign=Gtk.Align.FILL,
                              show_expanders=True, enable_tree_lines=True)

        self.set_grid_lines(Gtk.TreeViewGridLines.BOTH)
        self.get_selection().set_mode(Gtk.SelectionMode.NONE)

        self.store = Gtk.ListStore(str, str, int)

        self.device = 0xff

        self.unknown = "неизвестно"

        # append values
        self.store.append(["Стандарт сигнала", self.unknown, 0xff])
        self.store.append(["Модуляция", self.unknown, 0xff])
        self.store.append(["Символьная скорость", self.unknown, DVBC])
        self.store.append(["Число поднесущих канала", self.unknown, DVBT])
        self.store.append(["Защитный интервал", self.unknown, DVBT])
        self.store.append(["Режим иерархии", self.unknown, DVBT])
        self.store.append(["Спектр", self.unknown, DVBT])
        self.store.append(["Скорость кода LP", self.unknown, DVBT])
        self.store.append(["Скорость кода HP", self.unknown, DVBT])
        self.store.append(["Ширина канала", self.unknown, DVBT])
        self.store.append(["PLP ID", self.unknown, DVBT2])
        self.store.append(["Ширина канала", self.unknown, DVBT2])

        # creating store filter
        self.store_filter = self.store.filter_new()
        # setting the filter function
        self.store_filter.set_visible_func(self.param_filter_func)
        self.set_model(self.store_filter)

        # the cellrenderer for the first column - text
        self.parameter_name = Gtk.CellRendererText()
        # the cellrenderer for the second column - text
        self.parameter_value = Gtk.CellRendererText()

        # create first column
        self.column_name = Gtk.TreeViewColumn("Параметр")
        self.column_name.set_alignment(0.5)
        self.column_name.set_expand(True)
        self.column_name.pack_start(self.parameter_name, True)
        self.column_name.add_attribute(self.parameter_name, "text", 0)
        # append first column
        self.append_column(self.column_name)

        # create second column
        self.column_value = Gtk.TreeViewColumn("Значение")
        self.column_value.set_alignment(0.5)
        self.column_value.set_expand(True)
        self.column_value.pack_start(self.parameter_value, True)
        self.column_value.add_attribute(self.parameter_value, "text", 1)
        # append second column
        self.append_column(self.column_value)

    def param_filter_func(self, model, iter_, data):
        return (model[iter_][2] == 0xff) or \
               (model[iter_][2] == self.device)

    def set_signal_params(self, modulation, params):

        # DVB-C
        if 3 <= modulation <= 3:
            # set device
            self.device = DVBC
            iter_ = self.store.get_iter_from_string('0')
            self.store[iter_][1] = "DVB-C"

            # set modulation
            iter_ = self.store.get_iter_from_string('1')
            if modulation == 3:
                self.store[iter_][1] = "64-QAM"
            elif modulation == 4:
                self.store[iter_][1] = "128-QAM"
            elif modulation == 5:
                self.store[iter_][1] = "256-QAM"

            # set symbol rate
            iter_ = self.store.get_iter_from_string('2')
            self.store[iter_][1] = str(params)

        # DVB-T
        elif 4 <= modulation <= 8:
            # set device
            self.device = DVBT
            iter_ = self.store.get_iter_from_string('0')
            self.store[iter_][1] = "DVB-T"

            # set modulation
            iter_ = self.store.get_iter_from_string('1')
            if modulation == 6:
                self.store[iter_][1] = "QPSK"
            elif modulation == 7:
                self.store[iter_][1] = "16-QAM"
            elif modulation == 8:
                self.store[iter_][1] = "64-QAM"

            # set fft
            fft = (params & 0xC000) >> 14
            iter_ = self.store.get_iter_from_string('3')
            if fft == 0:
                self.store[iter_][1] = "2K"
            elif fft == 1:
                self.store[iter_][1] = "8K"
            else:
                self.store[iter_][1] = self.unknown

            # set gi
            gi = (params & 0x3000) >> 12
            iter_ = self.store.get_iter_from_string('4')
            if gi == 0:
                self.store[iter_][1] = "1/32"
            elif gi == 1:
                self.store[iter_][1] = "1/16"
            elif gi == 2:
                self.store[iter_][1] = "1/8"
            elif gi == 3:
                self.store[iter_][1] = "1/4"
            else:
                self.store[iter_][1] = self.unknown

            # set hierarchy
            hierarchy = (params & 0xC00) >> 10
            iter_ = self.store.get_iter_from_string('5')
            if hierarchy == 0:
                self.store[iter_][1] = "без иерархии"
            elif hierarchy == 1:
                self.store[iter_][1] = "a = 1"
            elif hierarchy == 2:
                self.store[iter_][1] = "a = 2"
            elif hierarchy == 3:
                self.store[iter_][1] = "a = 4"
            else:
                self.store[iter_][1] = self.unknown

            # set spectrum
            spectrum = (params & 0x200) >> 9
            iter_ = self.store.get_iter_from_string('6')
            if spectrum == 0:
                self.store[iter_][1] = "прямой"
            elif spectrum == 1:
                self.store[iter_][1] = "инверсный"
            else:
                self.store[iter_][1] = self.unknown

            # set fec lp
            fec_lp = (params & 0x1C0) >> 6
            iter_ = self.store.get_iter_from_string('7')
            if fec_lp == 0:
                self.store[iter_][1] = "1/2"
            elif fec_lp == 1:
                self.store[iter_][1] = "2/3"
            elif fec_lp == 2:
                self.store[iter_][1] = "3/4"
            elif fec_lp == 3:
                self.store[iter_][1] = "5/6"
            elif fec_lp == 4:
                self.store[iter_][1] = "7/8"
            else:
                self.store[iter_][1] = self.unknown

            # set fec hp
            fec_hp = (params & 0x38) >> 3
            iter_ = self.store.get_iter_from_string('8')
            if fec_hp == 0:
                self.store[iter_][1] = "1/2"
            elif fec_hp == 1:
                self.store[iter_][1] = "2/3"
            elif fec_hp == 2:
                self.store[iter_][1] = "3/4"
            elif fec_hp == 3:
                self.store[iter_][1] = "5/6"
            elif fec_hp == 4:
                self.store[iter_][1] = "7/8"
            else:
                self.store[iter_][1] = self.unknown

            # set bw
            bw = (params & 0x6) >> 1
            iter_ = self.store.get_iter_from_string('9')
            if bw == 0:
                self.store[iter_][1] = "6 МГц"
            elif bw == 1:
                self.store[iter_][1] = "7 МГц"
            elif bw == 2:
                self.store[iter_][1] = "8 МГц"
            else:
                self.store[iter_][1] = self.unknown

        # DVB-T2
        elif modulation == 9:
            # set device
            self.device = DVBT2
            iter_ = self.store.get_iter_from_string('0')
            self.store[iter_][1] = "DVB-T2"

            # set modulation
            qam_id = (params & 0x0f00) >> 8
            iter_ = self.store.get_iter_from_string('1')
            if qam_id == 0:
                self.store[iter_][1] = "QPSK"
            elif qam_id == 1:
                self.store[iter_][1] = "16-QAM"
            elif qam_id == 2:
                self.store[iter_][1] = "64-QAM"
            elif qam_id == 3:
                self.store[iter_][1] = "256-QAM"
            else:
                self.store[iter_][1] = self.unknown

            # set plp id
            plp_id = params & 0x00ff
            iter_ = self.store.get_iter_from_string('10')
            self.store[iter_][1] = str(plp_id)

            # set bandwidth
            bw = (params & 0xc000) >> 14
            iter_ = self.store.get_iter_from_string('11')
            if bw == 0:
                self.store[iter_][1] = "6 МГц"
            elif bw == 1:
                self.store[iter_][1] = "7 МГц"
            elif bw == 2:
                self.store[iter_][1] = "8 МГц"
            else:
                self.store[iter_][1] = self.unknown

        # unknown
        else:
            # set device
            self.device = 0xff
            self.store[self.store.get_iter_from_string('0')][1] = self.unknown
            # set modulation
            self.store[self.store.get_iter_from_string('1')][1] = self.unknown

            self.store_filter.refilter()

