from gi.repository import GObject

from BaseInterface import BaseInterface
from Usb.UsbExchange import UsbExchange


class Usb(BaseInterface):

    def __init__(self,
                 analyzed_progs_list,
                 analysis_settings_list,
                 tuner_settings_list):

        BaseInterface.__init__(self,
                               analyzed_progs_list,
                               analysis_settings_list,
                               tuner_settings_list)

        #GObject.timeout_add(1000, self.send_messages)

        self.exchange = UsbExchange()

        self.interface_name = 'Usb'

    def send_messages(self):
        print("sending message")

        self.exchange.send_init()
        self.exchange.send_status()
        self.exchange.send_errors()

        return True

    # Methods for interaction with Control
    # Common methods for Gui and Usb

    # called by Control to update stream prog list
    def update_stream_prog_list(self, prog_list):
        BaseInterface.update_stream_prog_list(self, prog_list)

        # increment settings version
        self.exchange.settings_version += 1

    # called by Control to update analyzed prog list
    def update_analyzed_prog_list(self, prog_list):
        BaseInterface.update_analyzed_prog_list(self, prog_list)

        # increment settings version
        self.exchange.settings_version += 1

    # called by Control to update analysis settings
    def update_analysis_settings(self, analysis_settings):
        BaseInterface.update_analysis_settings(self, analysis_settings)

        # increment settings version
        self.exchange.settings_version += 1

    # called by Control to update tuner settings
    def update_tuner_settings(self, tuner_settings):
        BaseInterface.update_tuner_settings(self, tuner_settings)

        # increment tuner settings version
        self.exchange.dvb_cont_ver += 1

    # called by Control to update tuner parameters
    def update_tuner_params(self, status, modulation, params):
        BaseInterface.update_tuner_params(self, status, modulation, params)

        # increment tuner status version
        self.exchange.dvb_stat_ver += 1

    # called by Control to update tuner measured data
    def update_tuner_measured_data(self, measured_data):
        BaseInterface.update_tuner_measured_data(self, measured_data)

    # called by Error Detector to update video status
    def update_video_status(self, results):
        BaseInterface.update_video_status(self, results)

    # called by Error Detector to update audio status
    def update_audio_status(self, results):
        BaseInterface.update_audio_status(self, results)

    # Control asks to return analyzed prog list
    def get_analyzed_prog_list(self):
        BaseInterface.get_analyzed_prog_list(self)
        return self.analyzed_prog_list

    # Control asks to return analysis settings
    def get_analysis_settings(self):
        return BaseInterface.get_analysis_settings(self)

    # Control asks to return tuner settings
    def get_tuner_settings(self):
        return BaseInterface.get_tuner_settings(self)

