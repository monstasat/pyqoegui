import struct

from gi.repository import GObject

from BaseInterface import BaseInterface
from Usb.UsbExchange import UsbExchange
from Usb import UsbMessageTypes as usb_msgs
from Control import CustomMessages

class Usb(BaseInterface):

    def __init__(self,
                 analyzed_progs_list,
                 analysis_settings_list,
                 tuner_settings_list):

        BaseInterface.__init__(self,
                               analyzed_progs_list,
                               analysis_settings_list,
                               tuner_settings_list)

        self.interface_name = 'Usb'

        self.exchange = UsbExchange()

        self.state = 0
        self.msg_count = 0
        self.init_done = False

        GObject.timeout_add(1000, self.send_messages)
        GObject.timeout_add(1000, self.read_messages)

    def send_messages(self):

        if self.init_done is False:
            self.exchange.send_init()
        else:
            self.exchange.send_status()
            self.exchange.status_version += 1
            self.exchange.send_errors()

        return True

    def read_messages(self):
        buf = self.exchange.read()

        buf = struct.unpack("H"*int(len(buf)/2), buf)

        client_id = 0
        request_id = 0

        for i, word in enumerate(buf):
            if word == self.exchange.PREFIX:
                self.state = self.exchange.PREFIX
                self.msg_count = 0
                continue

            if self.state == self.exchange.PREFIX:
                if word == usb_msgs.GET_BOARD_INFO:
                    self.init_done = False
                else:
                    self.state = word
                continue

            if self.state == usb_msgs.SET_BOARD_MODE:
                if self.msg_count == 0:
                    print("usb set board mode")
                    self.init_done = True

            elif self.state == usb_msgs.OPEN_CLIENT:
                if self.msg_count == 0:
                    print("usb open client")

            elif self.state == usb_msgs.CLOSE_CLIENT:
                if self.msg_count == 0:
                    print("usb close client")

            # remote client sent extended board mode (not used)
            elif self.state == usb_msgs.SET_BOARD_MODE_EXT:
                if self.msg_count == 0:
                    pass

            elif self.state == usb_msgs.SET_IP:
                if self.msg_count == 0:
                    print("usb set ip settings")

            elif self.state == usb_msgs.SET_VIDEO_ANALYSIS_SETTINGS:
                if self.msg_count == 0:
                    print("usb set video analysis settings")

            elif self.state == usb_msgs.SET_AUDIO_ANALYSIS_SETTINGS:
                if self.msg_count == 0:
                    print("usb set audio analysis settings")

            elif self.state == usb_msgs.SET_ANALYZED_PROG_LIST:
                if self.msg_count == 0:
                    print("usb set analyzed prog list")

            elif self.state == usb_msgs.SET_TUNER_SETTINGS:
                if self.msg_count == 0:
                    print("usb set tuner settings")

            elif self.state == usb_msgs.GET_IP:
                if self.msg_count == 0:
                    print("usb get ip settings")

            elif self.state == usb_msgs.GET_VIDEO_ANALYSIS_SETTINGS:
                if self.msg_count == 0:
                    client_id = word
                if self.msg_count == 2:
                    request_id = word
                    self.exchange.send_video_analysis_settings(
                        self.analysis_settings,
                        client_id,
                        request_id)

            elif self.state == usb_msgs.GET_AUDIO_ANALYSIS_SETTINGS:
                if self.msg_count == 0:
                    client_id = word
                if self.msg_count == 2:
                    request_id = word
                    self.exchange.send_audio_analysis_settings(
                        self.analysis_settings,
                        client_id,
                        request_id)

            elif self.state == usb_msgs.GET_ANALYZED_PROG_LIST:
                if self.msg_count == 0:
                    print("usb get analyzed prog list")

            # remote client asks to reset the device
            elif self.state == usb_msgs.RESET:
                if self.msg_count == 0:
                    self.emit(CustomMessages.ACTION_STOP_ANALYSIS)
                    self.emit(CustomMessages.ACTION_START_ANALYSIS)

            elif self.state == usb_msgs.GET_TUNER_SETTINGS:
                if self.msg_count == 0:
                    print("usb get tuner settings")

            elif self.state == usb_msgs.GET_TUNER_STATUS:
                if self.msg_count == 0:
                    #print("usb get tuner status")
                    pass

            # remote client asks to poweroff the device
            elif self.state == usb_msgs.POWEROFF:
                if self.msg_count == 0:
                    pass

            # increment word counter
            self.msg_count += 1

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

    # called by Control to update cpu load
    def update_cpu_load(self, load):
        BaseInterface.update_cpu_load(self, load)
        self.exchange.cpu_load = int(load)

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

