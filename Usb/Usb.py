from gi.repository import GObject

from BaseInterface import BaseInterface
from Usb.UsbExchange import UsbExchange
from Usb import UsbMessageParser as parser
from Usb import UsbMessageTypes as usb_msgs
from Control import CustomMessages

class Usb(BaseInterface):

    __gsignals__ = {
        CustomMessages.REMOTE_CLIENTS_NUM_CHANGED: (GObject.SIGNAL_RUN_FIRST,
                                               None, (int,))}

    def __init__(self,
                 analyzed_progs,
                 analysis_settings,
                 tuner_settings):

        BaseInterface.__init__(self,
                               analyzed_progs,
                               analysis_settings,
                               tuner_settings)

        self.interface_name = 'Usb'

        # create usb exchange
        self.exchange = UsbExchange()
        # create message parser
        self.msg_parser = parser.UsbMessageParser()

        # create tuner status
        self.tuner_status = []
        # create tuner params
        self.tuner_params = []
        # create tuner measured data
        self.tuner_measured_data = []

        # initialization done flag
        # True - handshake done with sopr board
        # False - handshake not done with sopr board
        self.init_done = False

        # launch read and write methods
        GObject.timeout_add(1000, self.send_messages)
        GObject.timeout_add(500, self.read_messages)

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
                self.init_done = True

            elif msg_type == usb_msgs.OPEN_CLIENT:
                client_num = int(msg_data[1])
                self.emit(CustomMessages.REMOTE_CLIENTS_NUM_CHANGED,
                          client_num)

            elif msg_type == usb_msgs.CLOSE_CLIENT:
                client_num = int(msg_data[1])
                self.emit(CustomMessages.REMOTE_CLIENTS_NUM_CHANGED,
                          client_num)

            # remote client sent video analysis settings
            elif msg_type == usb_msgs.SET_VIDEO_ANALYSIS_SETTINGS:
                result = self.msg_parser.parse_video_analysis_settings(
                                                    msg_data,
                                                    self.analysis_settings)
                self.analysis_settings = result

                # send message to Control
                self.emit(CustomMessages.ANALYSIS_SETTINGS_CHANGED)

            # remote client sent audio analysis settings
            elif msg_type == usb_msgs.SET_AUDIO_ANALYSIS_SETTINGS:
                result = self.msg_parser.parse_audio_analysis_settings(
                                                    msg_data,
                                                    self.analysis_settings)
                self.analysis_settings = result

                # send message to Control
                self.emit(CustomMessages.ANALYSIS_SETTINGS_CHANGED)

            # remote client sent analyzed prog list
            elif msg_type == usb_msgs.SET_ANALYZED_PROG_LIST:
                result = self.msg_parser.parse_analyzed_prog_list(
                                                    msg_data)

                # if parser returned analyzed prog list
                if result is not None:
                    # send message to Control
                    self.analyzed_prog_list = result
                    self.emit(CustomMessages.NEW_SETTINS_PROG_LIST)

            # remote client sent tuner settings
            elif msg_type == usb_msgs.SET_TUNER_SETTINGS:
                result = self.msg_parser.parse_tuner_settings(
                                                    msg_data,
                                                    self.tuner_settings)
                self.tuner_settings = result

                # send message to Control
                self.emit(CustomMessages.TUNER_SETTINGS_CHANGED)

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

            # remote client asks to return stream and analyzed prog list
            elif msg_type == usb_msgs.GET_ANALYZED_PROG_LIST:
                client_id = msg_data[0]
                request_id = msg_data[2]
                self.exchange.send_prog_list(
                        self.stream_prog_list,
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
                client_id = msg_data[0]
                request_id = msg_data[2]
                self.exchange.send_tuner_status(
                        self.tuner_status,
                        self.tuner_params,
                        self.tuner_measured_data,
                        self.tuner_settings,
                        client_id,
                        request_id)

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

    # called by Control to update tuner status
    def update_tuner_status(self, status, hw_errors, temperature):
        BaseInterface.update_tuner_status(self, status, hw_errors, temperature)
        self.tuner_status = [status, hw_errors, temperature]

    # called by Control to update tuner parameters
    def update_tuner_params(self, status, modulation, params):
        BaseInterface.update_tuner_params(self, status, modulation, params)
        self.tuner_params = [status, modulation, params]

        # increment tuner status version
        self.exchange.dvb_stat_ver += 1

    # called by Control to update tuner measured data
    def update_tuner_measured_data(self, measured_data):
        BaseInterface.update_tuner_measured_data(self, measured_data)
        self.tuner_measured_data = measured_data

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
        return BaseInterface.get_analyzed_prog_list(self)

    # Control asks to return analysis settings
    def get_analysis_settings(self):
        return BaseInterface.get_analysis_settings(self)

    # Control asks to return tuner settings
    def get_tuner_settings(self):
        return BaseInterface.get_tuner_settings(self)

