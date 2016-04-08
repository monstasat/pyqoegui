import struct
from collections import deque

from Usb import UsbMessageTypes as usb_msgs
from Control import TunerSettingsIndexes as ti


# converts 2 words to float
def words_to_float(loword, hiword):
    bytes_ = ((hiword << 16) | loword).to_bytes(4, byteorder='little')
    float_val = struct.unpack('f', bytes_)[0]
    return float_val


class UsbMessageParser():

    def __init__(self):
        # create parser buffer
        self.buffer = deque()
        # create message buffer
        self.message_buffer = []
        # create queue state
        self.queue_state = 0

        # received prog list
        self.prog_list_msg_data = []

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
        # msg code, msg data
        return [buf[1], buf[2:]]

    def parse_analyzed_prog_list(self, data):

        def decode_string(data, i):
            bytes = struct.pack(13*"H", *data[i:(i + 13)])
            return str(bytes.decode('cp1251', 'replace')).rstrip(' \t\r\n\0')

        prog_info = []

        client_id = data[0]
        length = data[1]
        request_id = data[2]
        # stream info
        # 3, 4 - wparam
        stream_num = data[5]
        prog_num = data[6]
        # if number of progs in received list is not null
        if prog_num > 0:
            # prog info
            prog_idx = data[7]
            # if this is a first message in a group,
            # clear prog list from previous programs
            if prog_idx == 0:
                self.prog_list_msg_data.clear()
            # 8 - hiword of wparam
            stream_id = data[9]
            prog_name = decode_string(data, 10)
            prov_name = decode_string(data, 23)
            prog_id = str(data[36])
            pids_num = str(data[37])

            # pids info
            pid_info = []
            # 38, 39 - wparam
            for i in range(int(pids_num)):
                pid = str(data[38 + 2 + i*28])
                codec_int = str(data[38 + 4 + i*28])
                codec_name = str(decode_string(data, 38 + 5 + i*28))

                # fill prog info
                pid_info.append([pid, codec_int, codec_name])

            # fill prog info
            prog_info = [prog_id, prog_name, prov_name, pids_num, pid_info]

            if len(self.prog_list_msg_data) != 0:
                for stream in self.prog_list_msg_data:
                    if stream[0] == stream_id:
                        stream[1].append(prog_info)
                        break
                else:
                    self.prog_list_msg_data.append([stream_id, [prog_info]])
            else:
                self.prog_list_msg_data = [[stream_id, [prog_info]]]

            # if this is a last message in a group
            # TODO: add additional check to be sure that the message
            # is consistent: eg message counter, etc
            if prog_idx == prog_num - 1:
                return self.prog_list_msg_data
            # in other case return none
            else:
                return None

        else:
            return []

    # TODO: add message length check to this group of functions
    def parse_video_analysis_settings(self, data, analysis_settings):
        settings = analysis_settings

        client_id = data[0]
        length = data[1]
        request_id = data[2]

        # TODO: fill settings

        return settings

    def parse_audio_analysis_settings(self, data, analysis_settings):
        settings = analysis_settings

        client_id = data[0]
        length = data[1]
        request_id = data[2]

        # TODO: fill settings

        return settings

    def parse_tuner_settings(self, data, tuner_settings):
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

