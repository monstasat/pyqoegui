from gi.repository import Gtk

from Gui.AnalysisSettingsDialog.BaseParamBox import BaseParamBox
from Gui import Spacing


class AnalysisSettingsPage(Gtk.Box):
    def __init__(self, main_dlg, page_type):
        Gtk.Box.__init__(self)

        # box must be with vertical orientation
        self.set_orientation(Gtk.Orientation.VERTICAL)

        # set border width and child spacing
        self.set_spacing(Spacing.ROW_SPACING)
        self.set_border_width(Spacing.BORDER)

        settings = main_dlg.analysis_settings

        self.add(BaseParamBox())

    def set_settings(self, analysis_settings):
        pass

    def get_settings(self):
        pass
