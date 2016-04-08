from gi.repository import Gtk

from Gui.BaseDialog import BaseDialog
from Gui.AnalysisSettingsDialog.AnalysisSettingsPage import \
                                AnalysisSettingsPage as Page
from Gui.Icon import Icon
from Gui import Spacing


class AnalysisSettingsDialog(BaseDialog):
    def __init__(self, parent, settings):
        BaseDialog.__init__(self, "Настройки анализа", parent.window)

        mainBox = self.get_content_area()

        self.settings = settings

        # fill page list with created pages
        self.pages = []
        def append_page(name, sname, keys):
            key_lst = []
            for key in keys:
                key_lst.extend([k for k, v in settings.items() if key in k])
            page = Page(self, sname, { k: settings[k] for k in key_lst})
            self.pages.append((page, sname, name))

        append_page('Пропадание видео', 'vloss', ('vloss',))
        append_page('Пропадание аудио', 'aloss', ('aloss',))
        append_page('Чёрный кадр', 'black', ('black', 'luma'))
        append_page('"Заморозка" видео', 'freeze', ('freeze', 'diff'))
        append_page('Блочность', 'blocky', ('blocky',))
        append_page('Тишина', 'silence', ('silence',))
        append_page('"Перегрузка" звука', 'loudness', ('loudness',))

        # create stack
        self.stack = Gtk.Stack(halign=Gtk.Align.FILL, hexpand=True)

        # set stack transition type
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_UP_DOWN)

        # add pages to stack
        for page in self.pages:
            self.stack.add_titled(page[0], page[1], page[2])

        # create stack sidebar
        self.stackSidebar = Gtk.StackSidebar(vexpand=True, hexpand=False,
                                             halign=Gtk.Align.START)
        self.stackSidebar.set_stack(self.stack)

        # configure main container orientation
        mainBox.set_orientation(Gtk.Orientation.HORIZONTAL)
        # pack items to main container
        mainBox.pack_start(self.stackSidebar, False, False, 0)
        mainBox.pack_start(Gtk.VSeparator(), False, False, 0)
        mainBox.pack_start(self.stack, True, True, 0)

        # update values in controls
        self.update_values(settings)

    # return analysis settings
    def get_analysis_settings(self):
        # update analysis settings list
        list(map(lambda x: self.settings.update(x[0].get_settings()),
                 self.pages))

        return self.settings

    # update values in spin buttons
    def update_values(self, settings):
        self.settings = settings

        list(map(lambda x: x[0].set_settings(self.settings),
                 self.pages))

