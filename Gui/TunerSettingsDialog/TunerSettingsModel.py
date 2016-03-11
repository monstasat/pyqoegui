from gi.repository import Gtk

from Control import TunerSettingsIndexes as ti

class TunerSettingsModel(Gtk.ListStore):
    def __init__(self, tuner_settings = []):
        # error name, type, failure, min, max, frames till error
        Gtk.ListStore.__init__(self, int)

        self.set_settings(tuner_settings)

    def is_index_valid(self, index):
        num = self.iter_n_children(None)
        if index > num or index < 0:
            return False
        else:
            return True

    def set_value_by_index(self, value, index):
        if self.is_index_valid(index) is True:
            iter = self.get_iter_from_string(str(index))
            self[iter][0] = value

    def get_value_by_index(self, index):
        if self.is_index_valid(index) is True:
            iter = self.get_iter(str(index))
            return self[iter][0]

    # return settings in the list format
    def get_settings_list(self):
        settings_list = []
        # iterating over model rows (settings)
        for row in self:
            settings_list.append([row[0]])

        return settings_list

    def set_settings(self, tuner_settings):
        # check if input parameter is consistent
        if len(tuner_settings) > 0:
            self.clear()
            # fill the model
            for value in tuner_settings:
                self.append(value)

