import struct

from gi.repository import GObject

from BaseInterface import BaseInterface
from Usb.UsbExchange import UsbExchange
from Usb.UsbMessageParser import UsbMessageParser
from Usb import UsbMessageTypes as usb_msgs
from Control import CustomMessages

class Usb(BaseInterface):

    def __init__(self,
                 analyzed_progs,
                 analysis_settings,
                 tuner_settings):

        BaseInterface.__init__(self,
                               analyzed_progs,
                               analysis_settings,
                               tuner_settings)

        self.interface_name = 'Usb'

        self.exchange = UsbExchange()
        self.msg_parser = UsbMessageParser()

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

        self.msg_parser.extend(buf)
        messages = self.msg_parser.parse_queue()

        client_id = 0
        request_id = 0

        for msg in messages:
            msg_type = msg[0]
            msg_data = msg[1]

            if msg_type == usb_msgs.GET_BOARD_INFO:
                self.init_done = False

            elif msg_type == usb_msgs.SET_BOARD_MODE:
                print("usb set board mode")
                self.init_done = True

            elif msg_type == usb_msgs.OPEN_CLIENT:
                print("usb open client")

            elif msg_type == usb_msgs.CLOSE_CLIENT:
                print("usb close client")

            # remote client sent extended board mode (not used)
            elif msg_type == usb_msgs.SET_BOARD_MODE_EXT:
                pass

            # remote client sent ip settings (not used)
            elif msg_type == usb_msgs.SET_IP:
                pass

            # remote client sent video analysis settings
            elif msg_type == usb_msgs.SET_VIDEO_ANALYSIS_SETTINGS:
                pass

            # remote client sent audio analysis settings
            elif msg_type == usb_msgs.SET_AUDIO_ANALYSIS_SETTINGS:
                pass

            # remote client sent analyzed prog list
            elif msg_type == usb_msgs.SET_ANALYZED_PROG_LIST:
                pass

            # remote client sent tuner settings
            elif msg_type == usb_msgs.SET_TUNER_SETTINGS:
                pass

            # remote client asks to return ip settings (not used)
            elif msg_type == usb_msgs.GET_IP:
                pass

            # remote client asks to return video analysis settings
            elif msg_type == usb_msgs.GET_VIDEO_ANALYSIS_SETTINGS:
                client_id = msg_data[0]
                request_id = msg_data[2]
                self.exchange.send_video_analysis_settings(
                        self.analysis_settings,
                        client_id,
                        request_id)

            # remote client asks to return audio analysis settings
            elif msg_type == usb_msgs.GET_AUDIO_ANALYSIS_SETTINGS:
                client_id = msg_data[0]
                request_id = msg_data[2]
                self.exchange.send_audio_analysis_settings(
                        self.analysis_settings,
                        client_id,
                        request_id)

            # remote client asks to return analyzed prog list
            elif msg_type == usb_msgs.GET_ANALYZED_PROG_LIST:
                client_id = msg_data[0]
                request_id = msg_data[2]
                self.exchange.send_analyzed_prog_list(
                        self.analyzed_prog_list,
                        client_id,
                        request_id)

            # remote client asks to reset the device
            elif msg_type == usb_msgs.RESET:
                self.emit(CustomMessages.ACTION_STOP_ANALYSIS)
                self.emit(CustomMessages.ACTION_START_ANALYSIS)

            # remote client asks to return tuner settings
            elif msg_type == usb_msgs.GET_TUNER_SETTINGS:
                client_id = msg_data[0]
                request_id = msg_data[2]
                self.exchange.send_tuner_settings(
                        self.tuner_settings,
                        client_id,
                        request_id)

            elif msg_type == usb_msgs.GET_TUNER_STATUS:
                pass

            # remote client asks to poweroff the device (not used)
            elif msg_type == usb_msgs.POWEROFF:
                pass

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

