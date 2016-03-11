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

        # remember store
        self.store = main_dlg.store

        # remember indexes
        self.indexes = indexes

        for i in indexes:
            iter_ = self.store.get_iter(str(i))
            name = self.store[iter_][0]
            if self.store[iter_][1] == 'error':
                name += " (ошибка)"
            elif self.store[iter_][1] == 'warning':
                name += " (предупреждение)"
            min_ = self.store[iter_][3]
            max_ = self.store[iter_][4]
            entry = SettingEntry(i, name, min_, max_)
            entry.set_value(self.store[iter_][2])

            # if parameter has attribute 'parameter'
            if self.store[iter_][1] == 'parameter':
                entry.spinBtn.set_digits(0)
                entry.spinBtn.set_increments(1, 10)

            # if parameter is video loss or audio loss
            if i == 0 or i == 1:
                entry.spinBtn.set_increments(1, 10)
                entry.spinBtn.set_digits(0)
            self.add(entry)

