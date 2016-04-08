from gi.repository import Gtk

from Gui.BaseDialog import SettingEntry
from Gui import Spacing


class AnalysisSettingsPage(Gtk.Box):
    def __init__(self, main_dlg, page_type, settings):
        Gtk.Box.__init__(self, spacing=Spacing.ROW_SPACING,
                         border_width=Spacing.BORDER,
                         orientation=Gtk.Orientation.VERTICAL,
                         vexpand=True, valign=Gtk.Align.FILL)

        self.page_type = page_type

        self.spin_btns = []
        self.switches = []

        if self.page_type == 'vloss' or self.page_type == 'aloss':
            return

        # possible parameters
        if self.page_type == 'black':
            names = ('Доля чёрных пикселей находится выше',
                     'Уровень средней яркости находится ниже')
            keys = (self.page_type + '_', 'luma_')
            units = ('%', '')
            digits = (1, 0)
            ranges = ((0, 100), (16, 235))
        elif self.page_type == 'freeze':
            names = ('Доля идентичных пикселей находится выше',
                     'Уровень средней разности находится ниже')
            keys = (self.page_type + '_', 'diff_')
            units = ('%', '')
            digits = (1, 0)
            ranges = ((0, 100), (0, 219))
        elif self.page_type == 'blocky':
            names = ('Уровень блочности находится выше',)
            keys = (self.page_type + '_',)
            units = ('',)
            digits = (1,)
            ranges = ((0, 10),)
        elif self.page_type == 'silence':
            names = ('Уровень громкости находится ниже',)
            keys = (self.page_type + '_',)
            units = ('LUFS',)
            digits = (1,)
            ranges = ((-59, -5),)
        elif self.page_type =='loudness':
            names = ('Уровень громкости находится выше',)
            keys = (self.page_type + '_',)
            units = ('LUFS',)
            digits = (1,)
            ranges = ((-59, -5),)

        row_cnt = 0

        grid = Gtk.Grid(column_spacing=Spacing.COL_SPACING,
                        row_spacing=Spacing.ROW_SPACING,
                        halign=Gtk.Align.FILL, hexpand=False)

        grid.attach(Gtk.Label("Определять ошибку немедленно, если",
                              halign=Gtk.Align.START), 0, row_cnt, 1, 1)
        row_cnt += 1

        for name, range_, unit, digit, key \
                            in zip(names, ranges, units, digits, keys):
            # create grid elements
            spin = Gtk.SpinButton(digits=digit)
            spin.set_range(range_[0], range_[1])
            spin.set_increments(0.1 if digit !=0 else 1, 2)
            switch = Gtk.Switch()

            self.spin_btns.append((spin, key + 'peak'))
            self.switches.append((switch, key + 'peak_en'))

            # attach elements to grid
            grid.attach(Gtk.Label(name, halign=Gtk.Align.START),
                        0, row_cnt, 1, 1)
            grid.attach(spin, 1, row_cnt, 1, 1)
            grid.attach(Gtk.Label(unit, Gtk.Align.START), 2, row_cnt, 1, 1)
            grid.attach(Gtk.VSeparator(), 3, row_cnt, 1, 1)
            grid.attach(switch, 4, row_cnt, 1, 1)
            row_cnt += 1

        grid.attach(Gtk.HSeparator(), 0, row_cnt, 5, 15)
        row_cnt += 15

        grid.attach(Gtk.Label("Определять ошибку, если в течение",
                              halign=Gtk.Align.START),
                    0, row_cnt, 1, 1)
        spin = Gtk.SpinButton(digits=0)
        spin.set_range(1, 3200)
        spin.set_increments(1, 2)
        self.spin_btns.append((spin, self.page_type + '_time'))

        grid.attach(spin, 1, row_cnt, 1, 1)
        grid.attach(Gtk.Label("секунд", halign=Gtk.Align.START),
                    2, row_cnt, 1, 1)
        row_cnt += 1

        for name, range_, unit, digit, key \
                            in zip(names, ranges, units, digits, keys):

            # create grid elements
            spin = Gtk.SpinButton(digits=digit)
            spin.set_range(range_[0], range_[1])
            spin.set_increments(0.1 if digit !=0 else 1, 2)
            switch = Gtk.Switch()

            self.spin_btns.append((spin, key + 'cont'))
            self.switches.append((switch, key + 'cont_en'))

            # attach elements to grid
            grid.attach(Gtk.Label(name, halign=Gtk.Align.START),
                        0, row_cnt, 1, 1)

            grid.attach(spin, 1, row_cnt, 1, 1)
            grid.attach(Gtk.Label(unit, Gtk.Align.START), 2, row_cnt, 1, 1)
            grid.attach(Gtk.VSeparator(), 3, row_cnt, 1, 1)
            grid.attach(switch, 4, row_cnt, 1, 1)
            row_cnt += 1

        self.add(grid)

        self.set_settings(settings)

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

