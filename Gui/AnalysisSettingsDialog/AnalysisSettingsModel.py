from gi.repository import Gtk


class AnalysisSettingsModel(Gtk.ListStore):
    def __init__(self, analysis_settings = []):
        # error name, type, failure, min, max, frames till error
        Gtk.ListStore.__init__(self, str, str, float, float, float, float)

        self.set_settings(analysis_settings)

    def is_index_valid(self, index):
        num = self.iter_n_children(None)
        if index > num or index < 0:
            return False
        else:
            return True

    def get_name(self, index):
        if self.is_index_valid(index) is True:
            iter = self.get_iter_from_string(str(index))
            return self[iter][0]

    def set_failure_value(self, value, index):
        if self.is_index_valid(index) is True:
            iter = self.get_iter_from_string(str(index))
            self[iter][2] = value

    def get_failure_value(self, index):
        if self.is_index_valid(index) is True:
            iter = self.get_iter_from_string(str(index))
            return self[iter][2]

    def set_frames_till_error(self, value, index):
        if self.is_index_valid(index) is True:
            iter = self.get_iter_from_string(str(index))
            self[iter][5] = value

    def get_min_max(self, index):
        if self.is_index_valid(index) is True:
            iter = self.get_iter_from_string(str(index))
            return [self[iter][3], self[iter][4]]

    def get_frames_till_error(self, index):
        if self.is_index_valid(index) is True:
            iter = self.get_iter_from_string(str(index))
            return self[iter][5]

    # return settings in the list format
    def get_settings_list(self):
        settings_list = []
        # iterating over model rows (settings)
        for row in self:
            param_list = []
            # iterating over row parameters
            for param in row:
                param_list.append(param)
            settings_list.append(param_list)

        return settings_list

    def set_settings(self, analysis_settings):
        if len(analysis_settings) > 0:
            self.clear()
            # fill the model
            for value in analysis_settings:
                self.append([value[0],
                             value[1],
                             value[2],
                             value[3],
                             value[4],
                             value[5]])

