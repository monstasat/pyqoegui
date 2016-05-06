from gi.repository import Gtk

from Gui.BaseDialog import SettingEntry
from Gui import Spacing


class AnalysisSettingsPage(Gtk.Box):
    def __init__(self, main_dlg, page_type, settings):
        Gtk.Box.__init__(self, spacing=Spacing.ROW_SPACING,
                         border_width=Spacing.BORDER,
                         orientation=Gtk.Orientation.VERTICAL,
                         vexpand=True, valign=Gtk.Align.FILL,
                         hexpand=True, halign=Gtk.Align.FILL)

        self.page_type = page_type

        self.spin_btns = []
        self.switches = []

        # grid row counter
        row_cnt = 0

        # create main grid
        grid = Gtk.Grid(column_spacing=Spacing.COL_SPACING,
                        row_spacing=Spacing.ROW_SPACING,
                        halign=Gtk.Align.FILL, hexpand=True)

        # if this is video or audio loss page
        if self.page_type == 'vloss' or self.page_type == 'aloss':
            text = 'Определять ошибку немедленно, если'
            grid.attach(Gtk.Label(text, halign=Gtk.Align.START),
                        0, 0, 1, 1)

            text = 'Данные на выходе декодера ' + \
                   ('видео' if 'v' in self.page_type else 'аудио') + \
                   ' отсутствуют в течение'
            spin = Gtk.SpinButton(digits=0)
            spin.set_range(1, 3200)
            spin.set_increments(1, 2)
            self.spin_btns.append((spin, self.page_type))

            grid.attach(Gtk.Label(text, halign=Gtk.Align.START),
                        0, 1, 1, 1)
            grid.attach(spin, 1, 1, 1, 1)
            grid.attach(Gtk.Label("секунд"), 2, 1, 1, 1)
            self.add(grid)
            return

        # other possible parameters
        if self.page_type == 'black':
            names = ('Доля чёрных пикселей в кадре',
                     'Средняя яркость кадра')
            keys = (self.page_type + '_', 'luma_')
            signs = ('≥', '≤')
            units = ('%', '')
            digits = (1, 0)
            ranges = ((0, 100), (16, 235))
        elif self.page_type == 'freeze':
            names = ('Доля идентичных пикселей в соседних кадрах',
                     'Средняя разность между пикселами соседних кадров')
            keys = (self.page_type + '_', 'diff_')
            signs = ('≥', '≤')
            units = ('%', '')
            digits = (1, 2)
            ranges = ((0, 100), (0, 219))
        elif self.page_type == 'blocky':
            names = ('Уровень блочности в кадре',)
            keys = (self.page_type + '_',)
            signs = ('≥')
            units = ('',)
            digits = (1,)
            ranges = ((0, 10),)
        elif self.page_type == 'silence':
            names = ('Уровень громкости в программе',)
            keys = (self.page_type + '_',)
            signs = ('≤',)
            units = ('LUFS',)
            digits = (1,)
            ranges = ((-59, -5),)
        elif self.page_type =='loudness':
            names = ('Уровень громкости в программе',)
            keys = (self.page_type + '_',)
            signs = ('≥',)
            units = ('LUFS',)
            digits = (1,)
            ranges = ((-59, -5),)

        # add group header
        grid.attach(
            Gtk.Label("Триггеры пиковых ошибок",
                      halign=Gtk.Align.END,
                      valign=Gtk.Align.END),
            0, row_cnt, 6, 1)
        row_cnt += 1
        grid.attach(Gtk.HSeparator(valign=Gtk.Align.START), 0, row_cnt, 6, 4)
        row_cnt += 4

        # add peak group header
        grid.attach(Gtk.Label("Определять ошибку немедленно, если",
                              halign=Gtk.Align.START, hexpand=True),
                    0, row_cnt, 1, 1)
        row_cnt += 1

        # add peak parameters group
        row_cnt = self.add_parameters_group('peak', grid, row_cnt, names,
                                            ranges, units, digits, keys, signs)

        # add group header
        grid.attach(
            Gtk.Label("Триггеры длительных ошибок",
                      halign=Gtk.Align.END,
                      valign=Gtk.Align.END),
            0, row_cnt, 6, 10)
        row_cnt += 10
        grid.attach(Gtk.HSeparator(valign=Gtk.Align.START), 0, row_cnt, 6, 4)
        row_cnt += 4

        # add cont group header
        grid.attach(Gtk.Label("Определять ошибку, если в течение",
                              halign=Gtk.Align.START), 0, row_cnt, 1, 1)
        spin = Gtk.SpinButton(digits=2, hexpand=False, climb_rate=1)
        spin.set_range(0.1, 3200)
        spin.set_increments(0.1, 1)
        self.spin_btns.append((spin, self.page_type + '_time'))
        grid.attach(spin, 2, row_cnt, 1, 1)
        grid.attach(Gtk.Label("секунд"), 3, row_cnt, 1, 1)
        row_cnt += 1

        # add cont parameters group
        row_cnt = self.add_parameters_group('cont', grid, row_cnt, names,
                                            ranges, units, digits, keys, signs)

        # add aditional parameters to page if necessary
        if self.page_type == 'black':
            txt = "Принимать пиксель за чёрный, если его яркость "
            range_ = (16, 235)
            type_ = 'black_pixel'
        elif self.page_type == 'freeze':
            txt = "Считать пиксели идентичными, если разность их яркостей "
            range_ = (0, 219)
            type_ = 'pixel_diff'

        if self.page_type == 'black' or self.page_type == 'freeze':
            # add group header
            grid.attach(
                Gtk.Label("Дополнительные параметры",
                          halign=Gtk.Align.END,
                          valign=Gtk.Align.END),
                0, row_cnt, 6, 10)
            row_cnt += 10
            grid.attach(Gtk.HSeparator(valign=Gtk.Align.START), 0, row_cnt, 6, 4)
            row_cnt += 4

            grid.attach(Gtk.Label(txt, halign=Gtk.Align.START),
                        0, row_cnt, 1, 1)
            spin = Gtk.SpinButton(digits=0, hexpand=False)
            spin.set_range(range_[0], range_[1])
            spin.set_increments(1, 2)
            self.spin_btns.append((spin, type_))
            grid.attach(Gtk.Label('≤'), 1, row_cnt, 1, 1)
            grid.attach(spin, 2, row_cnt, 1, 1)

        # add grid to page
        self.add(grid)

        # fill values into controls
        self.set_settings(settings)

    def add_parameters_group(self, group_type, grid, row_cnt, names, ranges,
                             units, digits, keys, signs):

            for name, range_, unit, digit, key, sign \
                in zip(names, ranges, units, digits, keys, signs):

                # create grid elements
                spin = Gtk.SpinButton(digits=digit, hexpand=False)
                spin.set_range(range_[0], range_[1])
                spin.set_increments(0.1 if digit !=0 else 1, 2)
                switch = Gtk.Switch()

                self.spin_btns.append((spin, key + group_type))
                self.switches.append((switch, key + group_type + '_en'))

                # attach elements to grid
                grid.attach(Gtk.Label(name, halign=Gtk.Align.START),
                            0, row_cnt, 1, 1)
                grid.attach(Gtk.Label(sign, hexpand=False), 1, row_cnt, 1, 1)
                grid.attach(spin, 2, row_cnt, 1, 1)
                grid.attach(Gtk.Label(unit, Gtk.Align.START), 3, row_cnt, 1, 1)
                grid.attach(Gtk.VSeparator(), 4, row_cnt, 1, 1)
                grid.attach(switch, 5, row_cnt, 1, 1)
                row_cnt += 1

            return row_cnt

    def set_settings(self, settings):
        for spin in self.spin_btns:
            spin[0].set_value(settings[spin[1]])

        for switch in self.switches:
            switch[0].set_active(settings[switch[1]])

    def get_settings(self):
        settings = {}
        for spin in self.spin_btns:
            settings.update({spin[1]: spin[0].get_value()})

        for switch in self.switches:
            settings.update({switch[1]: switch[0].get_active()})

        return settings

