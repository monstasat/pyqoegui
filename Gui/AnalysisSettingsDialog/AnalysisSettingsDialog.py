from gi.repository import Gtk

from Gui.BaseDialog import BaseDialog
from Gui.AnalysisSettingsDialog.AnalysisSettingsPage import \
                                AnalysisSettingsPage
from Gui.Icon import Icon
from Gui import Spacing
from Control import AnalysisSettingsIndexes as ai


class AnalysisSettingsDialog(BaseDialog):
    def __init__(self, parent, analysis_settings):
        BaseDialog.__init__(self, "Настройки анализа", parent.window)

        mainBox = self.get_content_area()

        self.analysis_settings = analysis_settings

        # fill page list with created pages
        self.pages = []
        self.pages.append((
            AnalysisSettingsPage(self, [ai.VIDEO_LOSS]),
            "video_loss",
            "Пропадание видео"))
        self.pages.append((
            AnalysisSettingsPage(self, [ai.AUDIO_LOSS]),
            "audio_loss",
            "Пропадание аудио"))
        self.pages.append((
            AnalysisSettingsPage(self, [ai.BLACK_ERR,
                                        ai.BLACK_WARN,
                                        ai.LUMA_WARN,
                                        ai.BLACK_PIXEL]),
            "black_frame",
            "Чёрный кадр"))
        self.pages.append((
            AnalysisSettingsPage(self, [ai.FREEZE_ERR,
                                        ai.FREEZE_WARN,
                                        ai.DIFF_WARN,
                                        ai.PIXEL_DIFF]),
            "freeze",
            '"Заморозка" видео"'))
        self.pages.append((
            AnalysisSettingsPage(self, [ai.BLOCK_ERR, ai.BLOCK_WARN]),
            "blockiness",
            "Блочность"))
        self.pages.append((
            AnalysisSettingsPage(self, [ai.OVERLOAD_ERR, ai.OVERLOAD_WARN]),
            "overload",
            '"Перегрузка" звука'))
        self.pages.append((
            AnalysisSettingsPage(self, [ai.SILENCE_ERR, ai.SILENCE_WARN]),
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

        # update values in controls
        self.update_values(analysis_settings)

        # expertBtn = Gtk.ToggleButton(image=Icon('emblem-system-symbolic'))
        # self.header.pack_end(expertBtn)

    # return analysis settings
    def get_analysis_settings(self):
        # update analysis settings list
        analysis_settings = self.analysis_settings
        for page in self.pages:
            for entry in page[0].get_children():
                value = entry.spinBtn.get_value()
                i = entry.index
                analysis_settings[i][2] = value

        return analysis_settings

    # update values in spin buttons
    def update_values(self, analysis_settings):
        self.analysis_settings = analysis_settings
        for page in self.pages:
            for entry in page[0].get_children():
                i = entry.index
                entry.spinBtn.set_value(analysis_settings[i][2])

