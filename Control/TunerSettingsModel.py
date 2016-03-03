from gi.repository import Gtk

# standard constants
DVBT2 = 0
DVBT = 1
DVBC = 2

# bw constants
BW6 = 0
BW7 = 1
BW8 = 2


class TunerSettingsModel(Gtk.ListStore):
    def __init__(self):
        # error name, type, failure, min, max, frames till error
        Gtk.ListStore.__init__(self, int)

        # indexes of store
        self.device = 0
        self.dvbt2_freq = 1
        self.dvbt2_bw = 2
        self.dvbt2_plpid = 3
        self.dvbt_freq = 4
        self.dvbt_bw = 5
        self.dvbc_freq = 6

        self.default_values = (
            [DVBT2],          # device
            [586000000],      # t2 frequency
            [BW8],            # t2 bandwidth
            [0],              # t2 plp id
            [586000000],      # t frequency
            [BW8],            # t bandwidth
            [586000000])      # c frequency

        # fill the model
        for value in self.default_values:
            self.append(value)

    def is_index_valid(self, index):
        num = self.iter_n_children(None)
        if index > num or index < 0:
            return False
        else:
            return True

    def set_value(self, value, index):
        if self.is_index_valid(index) is True:
            iter = self.get_iter_from_string(str(index))
            self[iter][0] = value

    def get_value(self, index):
        if self.is_index_valid(index) is True:
            iter = self.get_iter_from_string(str(index))
            return self[iter][0]

    # return settings in the list format
    def get_settings_list(self):
        settings_list = []
        # iterating over model rows (settings)
        for row in self:
            settings_list.append([row[0]])

        return settings_list

    def set_settings(self, tuner_settings):
        self.clear()

        # check if input parameter is consistent
        if len(tuner_settings) != len(self.default_values):
            tuner_settings = self.default_values

        # fill the model
        for value in tuner_settings:
            self.append(value)

