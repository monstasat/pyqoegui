from gi.repository import GObject

from Control import CustomMessages
from Control import AnalysisSettingsIndexes as ai
from Control import TunerSettingsIndexes as ti


class BaseInterface(GObject.GObject):

    __gsignals__ = {
        CustomMessages.NEW_SETTINS_PROG_LIST: (GObject.SIGNAL_RUN_FIRST,
                                               None, ()),
        CustomMessages.ANALYSIS_SETTINGS_CHANGED: (GObject.SIGNAL_RUN_FIRST,
                                                   None, ()),
        CustomMessages.TUNER_SETTINGS_CHANGED: (GObject.SIGNAL_RUN_FIRST,
                                                None, ()),
        CustomMessages.ACTION_START_ANALYSIS: (GObject.SIGNAL_RUN_FIRST,
                                               None, ()),
        CustomMessages.ACTION_STOP_ANALYSIS: (GObject.SIGNAL_RUN_FIRST,
                                              None, ())}

    def __init__(self,
                 app,
                 analyzed_prog_list=[],
                 analysis_settings_list=ai.DEFAULT_VALUES,
                 tuner_settings_list=ti.DEFAULT_VALUES):

        GObject.GObject.__init__(self)

        self.app = app
        # create stream prog list
        self.stream_prog_list = []
        # create analyzed prog list
        self.analyzed_prog_list = analyzed_prog_list
        # create analysis settings list
        self.analysis_settings = analysis_settings_list
        # create tuner settings list
        self.tuner_settings = tuner_settings_list

        #self.app.hold()

    def __destroy__(self):
        #self.app.release()
        pass

    def factory(type_, app):
        if type_ == "Gui":
            from Gui.Gui import Gui
            return Gui(app)
        if type_ == "Usb":
            from Usb.Usb import Usb
            return Usb(app)
        assert 0, "Bad interface creation" + type_
    factory = staticmethod(factory)

    # Methods for interaction with Control
    # Common methods for Gui and Usb

    # called by Control to update stream prog list
    def update_stream_prog_list(self, prog_list):
        # save stream prog list
        self.stream_prog_list = prog_list

    # called by Control to update analyzed prog list
    def update_analyzed_prog_list(self, prog_list):
        # save analyzed prog list
        self.analyzed_prog_list = prog_list

    # called by Control to update analysis settings
    def update_analysis_settings(self, analysis_settings):
        # save settings
        self.analysis_settings = analysis_settings

    # called by Control to update tuner settings
    def update_tuner_settings(self, tuner_settings):
        # save settings
        self.tuner_settings = tuner_settings

    # called by Control to update tuner status
    def update_tuner_status(self, status, hw_errors, temperature):
        pass

    # called by Control to update tuner parameters
    def update_tuner_params(self, status, modulation, params):
        pass

    # called by Control to update tuner measured data
    def update_tuner_measured_data(self, measured_data):
        pass

    # called by Error Detector to update video status
    def update_video_status(self, results):
        pass

    # called by Error Detector to update audio status
    def update_audio_status(self, results):
        pass

    # called by Control to update lufs values in program table and plots
    def update_lufs(self, lufs):
        pass

    # called by Control to update cpu load
    def update_cpu_load(self, load):
        pass

    # Control asks to return analyzed prog list
    def get_analyzed_prog_list(self):
        return self.analyzed_prog_list

    # Control asks to return analysis settings
    def get_analysis_settings(self):
        return self.analysis_settings

    # Control asks to return tuner settings
    def get_tuner_settings(self):
        return self.tuner_settings

