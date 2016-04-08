from gi.repository import Gtk

from Gui.BaseDialog import SettingEntry
from Gui import Spacing


class AnalysisSettingsPage(Gtk.Box):
    def __init__(self, main_dlg, page_type, settings):
        Gtk.Box.__init__(self, spacing=Spacing.ROW_SPACING,
                         border_width=Spacing.BORDER,
                         orientation=Gtk.Orientation.VERTICAL)

        self.page_type = page_type

        if self.page_type == 'vloss' or self.page_type == 'aloss':
            return

        # possible parameters
        if self.page_type == 'black':
            peak_names = ('как только доля чёрных пикселей превысит',
                          'Если уровень средней яркости ниже')
            cont_names = ('Если доля чёрных пикселей находится выше',
                          'Если уровень средней яркости находится ниже')
            keys = (self.page_type + '_', 'luma_')
            ranges = ((0, 100), (16, 235))
            incremets = (0.1, 1)
        elif self.page_type == 'freeze':
            peak_names = ('Если доля идентичных пикселей выше',
                          'Если уровень средней разности ниже')
            cont_names = ('Если доля идентичных пикселей находится выше',
                          'Если уровень средней разности находится ниже')
            keys = (self.page_type + '_', 'diff_')
            ranges = ((0, 100), (0, 219))
            incremets = (0.1, 1)
        elif self.page_type == 'blocky':
            peak_names = ('Если уровень блочности выше',)
            cont_names = ('Если уровень блочности находится выше',)
            keys = (self.page_type + '_')
            ranges = ((0, 10),)
            incremets = (0.1,)
        elif self.page_type == 'silence':
            peak_names = ('Если уровень громкости ниже',)
            cont_names = ('Если уровень громкости находится ниже',)
            keys = (self.page_type + '_')
            ranges = ((-59, -5),)
            incremets = (0.1,)
        elif self.page_type =='loudness':
            peak_names = ('Если уровень громкости выше',)
            cont_names = ('Если уровень громкости находится выше',)
            keys = (self.page_type + '_')
            ranges = ((-59, -5),)
            incremets = (0.1,)


        # create peak box
        peak_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,
                           hexpand=True, vexpand=True,
                           halign=Gtk.Align.FILL, valign=Gtk.Align.FILL,
                           spacing=Spacing.ROW_SPACING)

        peak_box.add(Gtk.Label('Определять ошибку,',
                     halign = Gtk.Align.START))

        for name, range_ in zip(peak_names, ranges):
            entry = SettingEntry(0, name, range_[0], range_[1], True)
            peak_box.add(entry)

        # create cont box
        cont_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,
                           hexpand=True, vexpand=True,
                           halign=Gtk.Align.FILL, valign=Gtk.Align.FILL,
                           spacing=Spacing.ROW_SPACING)

        cont_box.add(Gtk.Label('Определять ошибку,',
                     halign = Gtk.Align.START))

        for name, range_ in zip(cont_names, ranges):
            entry = SettingEntry(0, name, range_[0], range_[1], True)
            cont_box.add(entry)
        cont_box.add(SettingEntry(0, 'В течение ', 1, 3200, False))

        self.add(peak_box)
        self.add(Gtk.HSeparator())
        self.add(cont_box)

    def set_settings(self, analysis_settings):
        pass

    def get_settings(self):
        pass
