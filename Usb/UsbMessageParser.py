import struct
from collections import deque

from Usb import UsbMessageTypes as usb_msgs
from Control import AnalysisSettingsIndexes as ai
from Control import TunerSettingsIndexes as ti


class UsbMessageParser():

    def __init__(self):
        # create parser buffer
        self.buffer = deque()
        # create message buffer
        self.message_buffer = []
        # create queue state
        self.queue_state = 0

    def extend(self, data):
        '''
        Extends parser buffer by 'data' bytes, received from remote client
        '''
        self.buffer.extend(data)

    def parse_queue(self):
        '''
        Method for parsing input usb queue
        '''
        messages = []

        # if there is no data in parser queue and something left in
        # message queue, parse message queue
        if len(self.buffer) == 0 and len(self.message_buffer) != 0:
            res = self.parse_message(self.message_buffer)
            messages.append(res)

            # clear previous message
            self.message_buffer.clear()

        # get word from queue
        while len(self.buffer) != 0:

            word = self.buffer.popleft()

            if word == usb_msgs.PREFIX:
                # if message buffer is not empty, parse it
                if len(self.message_buffer) > 0:
                    res = self.parse_message(self.message_buffer)
                    messages.append(res)

                # clear previous message
                self.message_buffer.clear()

                # push new prefix to message buffer
                self.message_buffer.append(word)

            else:
                self.message_buffer.append(word)

        return messages

    def parse_message(self, buf):
        msg_code = buf[1]
        msg_data = buf[2:]

        return [msg_code, msg_data]


# converts 2 words to float
def words_to_float(loword, hiword):
    bytes_ = ((hiword << 16) | loword).to_bytes(4, byteorder='little')
    float_val =  struct.unpack('f', bytes_)[0]
    return float_val


# TODO: add message length check to this group of functions
def parse_video_analysis_settings(data, analysis_settings):
    settings = analysis_settings

    client_id = data[0]
    length = data[1]
    request_id = data[2]

    settings[ai.BLACK_WARN][2] = words_to_float(data[3], data[4])
    settings[ai.BLACK_ERR][2] = words_to_float(data[5], data[6])
    settings[ai.FREEZE_WARN][2] = words_to_float(data[7], data[8])
    settings[ai.FREEZE_ERR][2] = words_to_float(data[9], data[10])
    settings[ai.DIFF_WARN][2] = words_to_float(data[11], data[12])
    settings[ai.VIDEO_LOSS][2] = float(data[13] & 0x00ff)
    settings[ai.LUMA_WARN][2] = float(data[13] >> 8)
    settings[ai.BLACK_ERR][5] = int(data[14] & 0x00ff)
    settings[ai.BLACK_PIXEL][2] = int(data[14] >> 8)
    settings[ai.PIXEL_DIFF][2] = int(data[15] & 0x00ff)
    settings[ai.FREEZE_ERR][5] = int(data[15] >> 8)

    return settings


def parse_audio_analysis_settings(data, analysis_settings):
    settings = analysis_settings

    client_id = data[0]
    length = data[1]
    request_id = data[2]
    settings[ai.OVERLOAD_WARN][2] = words_to_float(data[3], data[4])
    settings[ai.OVERLOAD_ERR][2] = words_to_float(data[5], data[6])
    settings[ai.SILENCE_WARN][2] = words_to_float(data[7], data[8])
    settings[ai.SILENCE_ERR][2] = words_to_float(data[9], data[10])
    settings[ai.AUDIO_LOSS][2] = float(data[11] & 0x00ff)

    return settings


def parse_analyzed_prog_list(data):

    def decode_string(data, i):
        bytes = struct.pack(13*"H", *data[i:(i + 13)])
        string = bytes.decode('cp1251', 'replace')
        return string

    client_id = data[0]
    length = data[1]
    request_id = data[2]
    # stream info
    # 3, 4 - wparam
    stream_num = data[5]
    prog_num = data[6]
    # prog info
    prog_idx = data[7]
    # 8 - hiword of wparam
    stream_id = data[9]
    prog_name = decode_string(data, 10)
    prov_name = decode_string(data, 23)
    prog_type = data[36]
    pids_num = data[37]
    # pids info
    # 38, 39 - wparam
    for i in range(pids_num):
        pid = data[38 + 2 + i*28]
        codec_int = data[38 + 4 + i*28]
        codec_name = decode_string(data, 38 + 5 + i*28)

    return []


def parse_tuner_settings(data, tuner_settings):
    settings = tuner_settings

    client_id = data[0]
    length = data[1]
    request_id = data[2]

    settings[ti.DEVICE][0] = int(data[8] & 0x00ff)
    settings[ti.C_FREQ][0] = int(data[10] | (data[11] << 16))
    settings[ti.T_FREQ][0] = int(data[12] | (data[13] << 16))
    settings[ti.T_BW][0] = 2 - int(data[14])
    settings[ti.T2_FREQ][0] = int(data[16] | (data[17] << 16))
    settings[ti.T2_BW][0] = 2 - int(data[18])
    settings[ti.T2_PLP_ID][0] = int(data[19] & 0x00ff)

    return settings

