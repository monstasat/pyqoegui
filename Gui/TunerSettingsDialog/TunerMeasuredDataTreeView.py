from gi.repository import Gtk

from Control.DVBTunerConstants import DVBC, DVBT, DVBT2


# tree view that displays tuner measured data
class TunerMeasuredDataTreeView(Gtk.TreeView):
    def __init__(self, parent):
        Gtk.TreeView.__init__(self, hexpand=True, vexpand=False,
                              halign=Gtk.Align.FILL, valign=Gtk.Align.FILL,
                              show_expanders=True, enable_tree_lines=True)

        self.set_grid_lines(Gtk.TreeViewGridLines.BOTH)
        self.get_selection().set_mode(Gtk.SelectionMode.NONE)

        # current measured data
        self.measured_data = {}

        self.device = 0xff

        self.store = Gtk.ListStore(str, str)

        self.unknown = "неизвестно"

        # append values
        self.store.append(["Мощность, дБм", self.unknown])
        self.store.append(["MER, дБ", self.unknown])
        self.store.append(["BER", self.unknown])
        self.store.append(["Отклонение частоты, Гц", self.unknown])
        self.store.append(["Битрейт, Мбит/с", self.unknown])

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
        # if self.device == 0xff:
        #     return False
        # elif (self.device) == DVBC and \
        #      (str(model.get_path(iter_)) == '3'):
        #     return False
        # else:
        return True

    def set_measured_params(self, data):

        self.measured_data.update(data)

        # set rf power
        iter_ = self.store.get_iter_from_string('0')
        try:
            rf_power = self.measured_data["rf_power"]
        except:
            pass
        else:
            if rf_power == 0xffff:
                self.store[iter_][1] = self.unknown
            else:
                self.store[iter_][1] = str(-rf_power / 10)

        # set mer
        iter_ = self.store.get_iter_from_string('1')
        try:
            mer = self.measured_data["mer"]
        except:
            pass
        else:
            if mer == 0xffff:
                self.store[iter_][1] = self.unknown
            else:
                self.store[iter_][1] = str(mer / 10.)

        # set ber
        iter_ = self.store.get_iter_from_string('2')
        try:
            ber = self.measured_data["ber"]
            br = self.measured_data["bitrate"]
        except:
            pass
        else:
            if ber == -1 or br == -1 or br == 0:
                self.store[iter_][1] = self.unknown
            else:
                self.store[iter_][1] = "%.3e" % (ber / br)

        # set frequency
        iter_ = self.store.get_iter_from_string('3')
        try:
            freq = self.measured_data["freq"]
        except:
            pass
        else:
            if freq == -1:
                self.store[iter_][1] = self.unknown
            else:
                self.store[iter_][1] = str(freq)

        # set bitrate
        iter_ = self.store.get_iter_from_string('4')
        try:
            br = self.measured_data["bitrate"]
        except:
            print("no bitrate key")
            pass
        else:
            if br == -1:
                self.store[iter_][1] = self.unknown
            else:
                self.store[iter_][1] = str(br / 1000000.)

        # # set ber
        # if self.device == DVBC:
        #     # set ber1
        #     iter_ = self.store.get_iter_from_string('1')
        #     self.store[iter_][0] = "BER до декодера Рида-Соломона"
        #     self.store[iter_][1] = "%e" % self.measured_data[2]

        #     # set ber2
        #     iter_ = self.store.get_iter_from_string('2')
        #     self.store[iter_][0] = "BER после декодера Рида-Соломона"
        #     self.store[iter_][1] = "%e" % self.measured_data[4]

        # elif self.device == DVBT:
        #     # set ber1
        #     iter_ = self.store.get_iter_from_string('1')
        #     self.store[iter_][0] = "BER до декодера Витерби"
        #     self.store[iter_][1] = "%e" % self.measured_data[2]

        #     # set ber2
        #     iter_ = self.store.get_iter_from_string('2')
        #     self.store[iter_][0] = "BER до декодера Рида-Соломона"
        #     self.store[iter_][1] = "%e" % self.measured_data[4]

        #     # set ber3
        #     iter_ = self.store.get_iter_from_string('3')
        #     self.store[iter_][0] = "BER после декодера Рида-Соломона"
        #     self.store[iter_][1] = "%e" % self.measured_data[6]

        # elif self.device == DVBT2:
        #     # set ber1
        #     iter_ = self.store.get_iter_from_string('1')
        #     self.store[iter_][0] = "BER до декодера LDPC"
        #     self.store[iter_][1] = "%e" % self.measured_data[2]

        #     # set ber2
        #     iter_ = self.store.get_iter_from_string('2')
        #     self.store[iter_][0] = "BER до декодера BCH"
        #     self.store[iter_][1] = "%e" % self.measured_data[4]

        #     # set ber3
        #     iter_ = self.store.get_iter_from_string('3')
        #     self.store[iter_][0] = "BER после декодера BCH"
        #     self.store[iter_][1] = "%e" % self.measured_data[6]

        # else:
        #     self.store_filter.refilter()

