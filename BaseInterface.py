import os
import re
from operator import itemgetter

from gi.repository import GObject

from Control import CustomMessages
from Config.Config import ANALYSIS_DEFAULT
from Config.Config import TUNER_DEFAULT


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
                                              None, ()),
        CustomMessages.AUDIO_SOURCE_CHANGED: (GObject.SIGNAL_RUN_FIRST,
                                              None, ())}

    def __init__(self,
                 app,
                 analyzed_prog_list=[],
                 analysis_settings_list=ANALYSIS_DEFAULT,
                 tuner_settings_list=TUNER_DEFAULT):

        GObject.GObject.__init__(self)

        # available audio outputs
        self.audio_outputs = []
        index = 0
        buf = os.popen("pacmd list-cards").readlines()
        for line in buf:
            res = re.search("index: \w*", line)
            if res is not None:
                index = int(res.group().split(':')[1])
                continue

            res = re.search("output:[a-z]*-stereo:", line)
            if res is not None:
                self.audio_outputs.append([index, res.group()[:-1]])

        # sort outputs by alphabetical order
        self.audio_outputs = sorted(self.audio_outputs, key=itemgetter(1))

        self.app = app
        # create stream prog list
        self.stream_prog_list = []
        # create analyzed prog list
        self.analyzed_prog_list = analyzed_prog_list
        # create analysis settings list
        self.analysis_settings = analysis_settings_list
        # create tuner settings list
        self.tuner_settings = tuner_settings_list

        self.tuner_devinfo = {}
        self.tuner_meas = {}
        self.tuner_params = {}
        self.tuner_plp_list = {}

        self.app.hold()

    def __destroy__(self):
        self.app.release()
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
    def update_tuner_status(self, devinfo):
        self.tuner_devinfo = devinfo.copy()

    # called by Control to update tuner parameters
    def update_tuner_params(self, params):
        index = params.get('id', None)
        if index is not None:
            self.tuner_params[index] = params.copy()

    # called by Control to update tuner measured data
    def update_tuner_measured_data(self, meas):
        index = meas.get('id', None)
        if index is not None:
            self.tuner_meas[index] = meas.copy()

    def update_tuner_plp_list(self, plp_list):
        index = plp_list.get('id', None)
        if index is not None:
            self.tuner_plp_list[index] = plp_list.copy()

    # called by Error Detector to update analysis results
    def update_analysis_results(self, results):
        pass

    # called by Control to update lufs values in program table and plots
    def update_lufs(self, lufs):
        pass

    # called by Control to update cpu load
    def update_cpu_load(self, load):
        pass

    # called by Control to update audio source
    def update_audio_source(self, source):
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

    # Control asks to return audio source
    def get_audio_source(self):
        pass

