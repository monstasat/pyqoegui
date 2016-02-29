from gi.repository import Gtk

from Gui.BaseDialog import BaseDialog
from Gui.Icon import Icon
from Gui import Spacing


class SettingEntry(Gtk.Box):
    def __init__(self, index, label, min_, max_):
        Gtk.Box.__init__(self)

        self.index = index

        self.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.set_hexpand(True)
        self.set_vexpand(False)
        self.set_spacing(Spacing.COL_SPACING)

        # value entry
        self.spinBtn = Gtk.SpinButton()
        self.spinBtn.set_numeric(True)
        self.spinBtn.set_range(min_, max_)
        self.spinBtn.set_digits(2)
        self.spinBtn.set_increments(0.1, 1)
        self.spinBtn.set_hexpand(True)
        self.spinBtn.set_vexpand(False)
        self.spinBtn.set_halign(Gtk.Align.END)
        self.spinBtn.set_valign(Gtk.Align.CENTER)
        self.spinBtn.set_size_request(150, -1)
        self.spinBtn.set_property('climb-rate', 2)

        # setting name
        self.label = Gtk.Label(label=label)
        self.label.set_hexpand(True)
        self.label.set_vexpand(False)
        self.label.set_halign(Gtk.Align.START)
        self.label.set_valign(Gtk.Align.CENTER)

        self.add(self.label)
        self.add(self.spinBtn)

        self.show_all()

    def set_label(self, text):
        self.label.set_text(text)

    def set_value(self, value):
        self.spinBtn.set_value(value)


class BaseSettingsPage(Gtk.Box):
    def __init__(self, store, indexes):
        Gtk.Box.__init__(self)

        # box must be with vertical orientation
        self.set_orientation(Gtk.Orientation.VERTICAL)

        # set border width and child spacing
        self.set_spacing(Spacing.ROW_SPACING)
        self.set_border_width(Spacing.BORDER)

        # remember store
        self.store = store

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
                entry.spinBtn.set_digits(1)
            self.add(entry)


class AnalysisSettingsDialog(BaseDialog):
    def __init__(self, parent):
        BaseDialog.__init__(self, "Настройки анализа", parent)

        mainBox = self.get_content_area()

        # fill page list with created pages
        self.pages = []
        self.pages.append((
            BaseSettingsPage(parent.errorSettingsStore, [0]),
            "video_loss",
            "Пропадание видео"))
        self.pages.append((
            BaseSettingsPage(parent.errorSettingsStore, [1]),
            "audio_loss",
            "Пропадание аудио"))
        self.pages.append((
            BaseSettingsPage(parent.errorSettingsStore, [2, 3, 4, 5]),
            "black_frame",
            "Чёрный кадр"))
        self.pages.append((
            BaseSettingsPage(parent.errorSettingsStore, [6, 7, 8, 9]),
            "freeze",
            '"Заморозка" видео"'))
        self.pages.append((
            BaseSettingsPage(parent.errorSettingsStore, [10, 11]),
            "blockiness",
            "Блочность"))
        self.pages.append((
            BaseSettingsPage(parent.errorSettingsStore, [12, 13]),
            "overload",
            '"Перегрузка" звука'))
        self.pages.append((
            BaseSettingsPage(parent.errorSettingsStore, [14, 15]),
            "silence",
            "Тишина"))

        # create stack
        self.stack = Gtk.Stack(halign=Gtk.Align.FILL, hexpand=True)

        # set stack transition type
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_UP_DOWN)

        # add pages to stack
        for page in self.pages:
            self.stack.add_titled(page[0], page[1], page[2])

        # create stack sidebar
        self.stackSidebar = Gtk.StackSidebar(
            vexpand=True,
            hexpand=False,
            halign=Gtk.Align.START)
        self.stackSidebar.set_stack(self.stack)
        self.stackSidebar.show()

        # configure main container orientation
        mainBox.set_orientation(Gtk.Orientation.HORIZONTAL)
        # pack items to main container
        mainBox.pack_start(self.stackSidebar, False, False, 0)
        separator = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        mainBox.pack_start(separator, False, False, 0)
        mainBox.pack_start(self.stack, True, True, 0)

        # expertBtn = Gtk.ToggleButton(image=Icon('emblem-system-symbolic'))
        # self.header.pack_end(expertBtn)

        self.show_all()

    # apply values from spin buttons to model
    def apply_settings(self):
        for page in self.pages:
            for entry in page[0].get_children():
                value = entry.spinBtn.get_value()
                i = entry.index
                iter_ = page[0].store.get_iter(str(i))
                page[0].store[iter_][2] = value

    # update values in spin buttons
    def update_values(self):
        for page in self.pages:
            for entry in page[0].get_children():
                i = entry.index
                iter_ = page[0].store.get_iter(str(i))
                value = page[0].store[iter_][2]
                entry.spinBtn.set_value(value)

