from gi.repository import Gtk


class ErrorTypesModel(Gtk.ListStore):
    def __init__(self):
        # error name, type, failure, min, max, frames till error
        Gtk.ListStore.__init__(self, str, str, float, float, float, float)

        self.default_values = (
            ['Пропадание видео, секунд',
             'error',   2.0,   0,  3600, 2],
            ['Пропадание аудио, секунд',
             'error',   2.0,   0,  3600, 2],
            ['Количество чёрных пикселей, %',
             'error',   99.5,  0,  100,  75],
            ['Количество чёрных пикселей, %',
             'warning', 95.0,  0,  100,  75],
            ['Уровень средней яркости',
             'warning', 10.0,  0,  255,  75],
            ['Уровень чёрного пиксела',
             'parameter', 16,  0,  100,  0],
            ['Количество идентичных пикселей, %',
             'error',   99.5,  0,  100,  75],
            ['Количество идентичных пикселей, %',
             'warning', 95.0,  0,  100,  75],
            ['Уровень средней разности',
             'warning', 0.20,  0,  255,  75],
            ['Допустимая разность между пикселами',
             'parameter', 0,  0,  100,  0],
            ['Блочность',
             'error',   4.00,  0,  10,   5],
            ['Блочность',
             'warning', 3.00,  0,  10,   1],
            ['Уровень громкости, LUFS',
             'error',   -22.0, -59, -5,  1],
            ['Уровень громкости, LUFS',
             'warning', -22.5, -59, -5,  1],
            ['Уровень громкости, LUFS',
             'error',   -34.0, -59, -5,  1],
            ['Уровень громкости, LUFS',
             'warning', -33.0, -59, -5,  1]
            )

        # fill the model
        for value in self.default_values:
            self.append([value[0],
                         value[1],
                         value[2],
                         value[3],
                         value[4],
                         value[5]])

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
