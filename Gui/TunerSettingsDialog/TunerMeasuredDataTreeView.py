from gi.repository import Gtk

from Control.DVBTunerConstants import DVBUNK, DVBT2, DVBT, DVBC


# tree view that displays tuner measured data
class TunerMeasuredDataTreeView(Gtk.TreeView):
    def __init__(self, slot_id, settings):
        Gtk.TreeView.__init__(self, hexpand=True, vexpand=False,
                              halign=Gtk.Align.FILL, valign=Gtk.Align.FILL,
                              show_expanders=True, enable_tree_lines=True)

        self.set_grid_lines(Gtk.TreeViewGridLines.BOTH)
        self.get_selection().set_mode(Gtk.SelectionMode.NONE)

        # current measured data
        self.measured_data = {}

        self.store = Gtk.ListStore(str, str)

        self.unknown = "неизвестно"

        self.slot_id = slot_id
        self.settings = settings.copy()

        # append values
        self.store.append(["Мощность, дБм", self.unknown])
        self.store.append(["MER, дБ", self.unknown])
        self.store.append(["BER", self.unknown])
        self.store.append(["Частота, Гц", self.unknown])
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

    def on_new_tuner_settings(self, settings):
        self.settings.update(settings)

    def set_measured_params(self, data):
        MAX_DWORD = 0xffffffff
        MAX_WORD = 0xffff
        MAX_BYTE = 0xff

        self.measured_data = data
        # set rf power
        iter_ = self.store.get_iter_from_string('0')
        rf_power = self.measured_data.get("rf_power", MAX_WORD)
        self.store[iter_][1] = self.unknown if rf_power == MAX_WORD \
                               else str(-rf_power / 10)
        # set mer
        iter_ = self.store.get_iter_from_string('1')
        mer = self.measured_data.get("mer", MAX_WORD)
        self.store[iter_][1] = self.unknown if mer == MAX_WORD \
                               else str(mer / 10.)
        # set ber
        iter_ = self.store.get_iter_from_string('2')
        ber = self.measured_data.get("ber", MAX_DWORD)
        self.store[iter_][1] = self.unknown if ber == MAX_DWORD \
                               else "%.3e" % (ber / (2**24))

        # set frequency
        iter_ = self.store.get_iter_from_string('3')
        freq = self.measured_data.get("freq", MAX_DWORD)
        self.store[iter_][1] = self.unknown if freq == MAX_DWORD \
                               else str(freq)

        # set frequency
        iter_ = self.store.get_iter_from_string('4')
        device = self.settings.get("device", DVBUNK)
        # print(self.slot_id, self.settings)
        if device in [DVBT2, DVBT, DVBC]:
            if device == DVBT2:
                frequency = self.settings.get("t2_freq", -1)
            elif device == DVBT:
                frequency = self.settings.get("t_freq", -1)
            elif device == DVBC:
                frequency = self.settings.get("c_freq", -1)
            else:
                frequency = MAX_DWORD

            if frequency != MAX_DWORD:
                self.store[iter_][1] = self.unknown if freq == MAX_DWORD \
                                       else str(frequency - freq)
        # set bitrate
        iter_ = self.store.get_iter_from_string('5')
        br = self.measured_data.get("bitrate", MAX_DWORD)
        self.store[iter_][1] = self.unknown if br == MAX_DWORD \
                               else str(br / 1000000.)

