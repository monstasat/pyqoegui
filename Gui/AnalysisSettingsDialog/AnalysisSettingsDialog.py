from gi.repository import Gtk

from Gui.BaseDialog import BaseDialog
from Gui.AnalysisSettingsDialog.AnalysisSettingsPage import \
                                AnalysisSettingsPage
from Gui.Icon import Icon
from Gui import Spacing


class AnalysisSettingsDialog(BaseDialog):
    def __init__(self, parent):
        BaseDialog.__init__(self, "Настройки анализа", parent)

        mainBox = self.get_content_area()

        # fill page list with created pages
        self.pages = []
        self.pages.append((
            AnalysisSettingsPage(parent.errorSettingsStore, [0]),
            "video_loss",
            "Пропадание видео"))
        self.pages.append((
            AnalysisSettingsPage(parent.errorSettingsStore, [1]),
            "audio_loss",
            "Пропадание аудио"))
        self.pages.append((
            AnalysisSettingsPage(parent.errorSettingsStore, [2, 3, 4, 5]),
            "black_frame",
            "Чёрный кадр"))
        self.pages.append((
            AnalysisSettingsPage(parent.errorSettingsStore, [6, 7, 8, 9]),
            "freeze",
            '"Заморозка" видео"'))
        self.pages.append((
            AnalysisSettingsPage(parent.errorSettingsStore, [10, 11]),
            "blockiness",
            "Блочность"))
        self.pages.append((
            AnalysisSettingsPage(parent.errorSettingsStore, [12, 13]),
            "overload",
            '"Перегрузка" звука'))
        self.pages.append((
            AnalysisSettingsPage(parent.errorSettingsStore, [14, 15]),
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

