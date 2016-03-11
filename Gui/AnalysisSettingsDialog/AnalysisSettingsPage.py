from gi.repository import Gtk

from Gui.BaseDialog import SettingEntry
from Gui import Spacing


class AnalysisSettingsPage(Gtk.Box):
    def __init__(self, main_dlg, indexes):
        Gtk.Box.__init__(self)

        # box must be with vertical orientation
        self.set_orientation(Gtk.Orientation.VERTICAL)

        # set border width and child spacing
        self.set_spacing(Spacing.ROW_SPACING)
        self.set_border_width(Spacing.BORDER)

        # remember indexes
        self.indexes = indexes

        settings = main_dlg.analysis_settings

        for i in indexes:
            name = settings[i][0]
            if settings[i][1] == 'error':
                name += " (ошибка)"
            elif settings[i][1] == 'warning':
                name += " (предупреждение)"
            min_ = settings[i][3]
            max_ = settings[i][4]
            entry = SettingEntry(i, name, min_, max_)
            entry.set_value(settings[i][2])

            # if parameter has attribute 'parameter'
            if settings[i][1] == 'parameter':
                entry.spinBtn.set_digits(0)
                entry.spinBtn.set_increments(1, 10)

            # if parameter is video loss or audio loss
            if i == 0 or i == 1:
                entry.spinBtn.set_increments(1, 10)
                entry.spinBtn.set_digits(0)
            self.add(entry)

