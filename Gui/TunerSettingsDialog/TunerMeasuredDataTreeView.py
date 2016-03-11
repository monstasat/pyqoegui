from gi.repository import Gtk

from Control import TunerSettingsIndexes as ti


# tree view that displays tuner measured data
class TunerMeasuredDataTreeView(Gtk.TreeView):
    def __init__(self, parent):
        Gtk.TreeView.__init__(self)

        self.set_hexpand(True)
        self.set_vexpand(False)
        self.set_halign(Gtk.Align.FILL)
        self.set_valign(Gtk.Align.FILL)
        self.set_grid_lines(Gtk.TreeViewGridLines.BOTH)
        self.set_show_expanders(True)
        self.set_enable_tree_lines(False)
        sel = self.get_selection()
        sel.set_mode(Gtk.SelectionMode.NONE)

        # current measured data
        self.measured_data = [0, False, 0, False, 0, False, 0, False]

        self.main_wnd = parent

        self.store = Gtk.ListStore(str, str)

        self.unknown = "неизвестно"

        # append values
        self.store.append(["MER",
                           self.unknown])
        self.store.append(["BER",
                           self.unknown])
        self.store.append(["BER",
                           self.unknown])
        self.store.append(["BER",
                           self.unknown])

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
        if self.main_wnd.device == 0xff:
            return False
        elif (self.main_wnd.device) == ti.DVBC and \
             (str(model.get_path(iter_)) == '3'):
            return False
        else:
            return True

    def set_measured_params(self, data):

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

        # set mer
        iter_ = self.store.get_iter_from_string('0')
        self.store[iter_][1] = str(self.measured_data[0])

        # set ber
        if self.main_wnd.device == ti.DVBC:
            # set ber1
            iter_ = self.store.get_iter_from_string('1')
            self.store[iter_][0] = "BER до декодера Рида-Соломона"
            self.store[iter_][1] = "%e" % self.measured_data[2]

            # set ber2
            iter_ = self.store.get_iter_from_string('2')
            self.store[iter_][0] = "BER после декодера Рида-Соломона"
            self.store[iter_][1] = "%e" % self.measured_data[4]

        elif self.main_wnd.device == ti.DVBT:
            # set ber1
            iter_ = self.store.get_iter_from_string('1')
            self.store[iter_][0] = "BER до декодера Витерби"
            self.store[iter_][1] = "%e" % self.measured_data[2]

            # set ber2
            iter_ = self.store.get_iter_from_string('2')
            self.store[iter_][0] = "BER до декодера Рида-Соломона"
            self.store[iter_][1] = "%e" % self.measured_data[4]

            # set ber3
            iter_ = self.store.get_iter_from_string('3')
            self.store[iter_][0] = "BER после декодера Рида-Соломона"
            self.store[iter_][1] = "%e" % self.measured_data[6]

        elif self.main_wnd.device == ti.DVBT2:
            # set ber1
            iter_ = self.store.get_iter_from_string('1')
            self.store[iter_][0] = "BER до декодера LDPC"
            self.store[iter_][1] = "%e" % self.measured_data[2]

            # set ber2
            iter_ = self.store.get_iter_from_string('2')
            self.store[iter_][0] = "BER до декодера BCH"
            self.store[iter_][1] = "%e" % self.measured_data[4]

            # set ber3
            iter_ = self.store.get_iter_from_string('3')
            self.store[iter_][0] = "BER после декодера BCH"
            self.store[iter_][1] = "%e" % self.measured_data[6]

        else:
            self.store_filter.refilter()

