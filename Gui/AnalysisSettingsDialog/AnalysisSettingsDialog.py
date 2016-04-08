from gi.repository import Gtk

from Gui.BaseDialog import BaseDialog
from Gui.AnalysisSettingsDialog.AnalysisSettingsPage import \
                                AnalysisSettingsPage
from Gui.Icon import Icon
from Gui import Spacing


class AnalysisSettingsDialog(BaseDialog):
    def __init__(self, parent, analysis_settings):
        BaseDialog.__init__(self, "Настройки анализа", parent.window)

        mainBox = self.get_content_area()

        self.analysis_settings = analysis_settings

        # fill page list with created pages
        self.pages = []
        self.pages.append(
            (AnalysisSettingsPage(self, 'vloss'), "vloss", "Пропадание видео"))
        self.pages.append((
            AnalysisSettingsPage(self, 'aloss'), "aloss", "Пропадание аудио"))
        self.pages.append((
            AnalysisSettingsPage(self, 'black'), "black", "Чёрный кадр"))
        self.pages.append((
            AnalysisSettingsPage(self, 'freeze'), "freeze",
            '"Заморозка" видео"'))
        self.pages.append((
            AnalysisSettingsPage(self, 'blocky'), "blocky", "Блочность"))
        self.pages.append((
            AnalysisSettingsPage(self, 'silence'), "silence", 'Тишина'))
        self.pages.append((
            AnalysisSettingsPage(self, 'loudness'),"loudness",
            '"Перегрузка" звука'))

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

        # update values in controls
        self.update_values(analysis_settings)

        # expertBtn = Gtk.ToggleButton(image=Icon('emblem-system-symbolic'))
        # self.header.pack_end(expertBtn)

    # return analysis settings
    def get_analysis_settings(self):
        # update analysis settings list
        list(map(lambda x: self.analysis_settings.update(x[0].get_settings()),
                 self.pages))

        return self.analysis_settings

    # update values in spin buttons
    def update_values(self, analysis_settings):
        self.analysis_settings = analysis_settings

        list(map(lambda x: x[0].set_settings(self.analysis_settings),
                 self.pages))

