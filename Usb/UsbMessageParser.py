import struct
from collections import deque

from Usb import UsbMessageTypes as usb_msgs


# converts 2 words to float
def words_to_float(loword, hiword):
    bytes_ = ((hiword << 16) | loword).to_bytes(4, byteorder='little')
    float_val = struct.unpack('f', bytes_)[0]
    return float_val

# converts 2 words to dword
def words_to_dword(loword, hiword):
    bytes_ = ((hiword << 16) | loword).to_bytes(4, byteorder='little')
    dword_val = struct.unpack('I', bytes_)[0]
    return dword_val


class UsbMessageParser():

    def __init__(self):
        # create parser buffer
        self.buffer = deque()

        # received prog list
        self.prog_list_msg_data = []

    def extend(self, data):
        '''
        Extends parser buffer by 'data' bytes, received from remote client
        '''
        self.buffer.extend(data)

    def get_msg_length(self, code):
        lenght = 0

        if code == usb_msgs.GET_BOARD_INFO:
            length = 2
        elif code == usb_msgs.SET_BOARD_MODE:
            length = 6
        elif (code == usb_msgs.OPEN_CLIENT) or \
             (code == usb_msgs.CLOSE_CLIENT):
            length = 4
        elif code in usb_msgs.VALID_COD_COMMANDS:
            length = -1
        else:
            length = None

        return length

    def parse_queue(self):
        '''
        Method for parsing input usb queue
        '''

        # parsed messages are stored here
        parsed = []
        counter = 0
        message = []
        queue_length = 0
        cod_command = None
        message_length = None

        # print_parsed = False
        # if len(self.buffer) > 0:
        #     print("new bytes:", list(self.buffer))
        #     print_parsed = True

        while len(self.buffer) > 0:

            word = self.buffer[0]

            # wait for prefix state
            if counter == 0:

                # save current queue length
                queue_length = len(self.buffer)

                # if received prefix
                if self.buffer[0] == usb_msgs.PREFIX:

                    # Try to get cod command
                    try:
                        cod_command = int(self.buffer[1])
                    except:
                        break

                    message_length = self.get_msg_length(cod_command)

                    # if length is contained in message
                    if message_length == -1:

                        # try to read length from message
                        try:
                            message_length = int(self.buffer[3]) + 4
                            counter += 1
                            # in case if message is not fully received yet
                        except:
                            break
                    # if received message with constant length
                    elif message_length is not None:
                        counter += 1
                    # if received message code is unsupported
                    else:
                        self.buffer.popleft()

                    # if message is not fully received yet
                    if counter > 0 and message_length > queue_length:
                        break

                # if not received prefix
                elif counter == 0:
                    self.buffer.popleft()

            # read message state
            elif counter > 0:
                message.append(self.buffer.popleft())
                if counter == message_length:
                    counter = 0
                    # message is treated as valid if next byte is PREFIX
                    # or if receiving buffer is empty
                    if len(self.buffer) == 0 or \
                       self.buffer[0] == usb_msgs.PREFIX:
                        parsed.append((message[1], message[2:]))
                    message = []
                else:
                    counter += 1

        # if print_parsed:
        #     print("parsed data: ", parsed)

        # return parsed messages
        return parsed

    def parse_analyzed_prog_list(self, data):

        def decode_string(data, i):
            bytes = struct.pack(13*"H", *data[i:(i + 13)])
            return str(bytes.decode('cp1251', 'replace')).rstrip(' \t\r\n\0')

        prog_info = []

        try:

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
        except:
            return None

    # TODO: add message length check to this group of functions
    def parse_video_analysis_settings(self, data, analysis_settings):
        settings = analysis_settings

        if len(data) >= 47:
            try:
                client_id = data[0]
                length = data[1]
                request_id = data[2]

                # fill settings
                settings['vloss'] = words_to_float(data[3], data[4])
                settings['black_cont'] = words_to_float(data[5], data[6])
                settings['black_peak'] = words_to_float(data[7], data[8])
                settings['black_cont_en'] = int(data[9] & 0x00ff)
                settings['black_peak_en'] = int(data[9] >> 8)
                settings['luma_cont'] = words_to_float(data[10], data[11])
                settings['luma_peak'] = words_to_float(data[12], data[13])
                settings['luma_cont_en'] = int(data[14] & 0x00ff)
                settings['luma_peak_en'] = int(data[14] >> 8)
                settings['black_time'] = words_to_float(data[15], data[16])
                settings['black_pixel'] = words_to_dword(data[17], data[18])
                # data[19], data[20] - reserved
                settings['freeze_cont'] = words_to_float(data[21], data[22])
                settings['freeze_peak'] = words_to_float(data[23], data[24])
                settings['freeze_cont_en'] = int(data[25] & 0x00ff)
                settings['freeze_peak_en'] = int(data[25] >> 8)
                settings['diff_cont'] = words_to_float(data[26], data[27])
                settings['diff_peak'] = words_to_float(data[28], data[29])
                settings['diff_cont_en'] = int(data[30] & 0x00ff)
                settings['diff_peak_en'] = int(data[30] >> 8)
                settings['freeze_time'] = words_to_float(data[31], data[32])
                settings['pixel_diff'] = data[33]
                # data[34], data[35] - reserved
                settings['blocky_cont'] = words_to_float(data[36], data[37])
                settings['blocky_peak'] = words_to_float(data[38], data[39])
                settings['blocky_cont_en'] = int(data[40] & 0x00ff)
                settings['blocky_peak_en'] = int(data[40] >> 8)
                settings['blocky_time'] = words_to_float(data[41], data[42])
                settings['block_size'] = words_to_dword(data[43], data[44])
                # data[45], data[46] - reserved
            except:
                return None
            else:
                return settings
        else:
            return None

    def parse_audio_analysis_settings(self, data, analysis_settings):
        settings = analysis_settings.copy()

        if len(data) >= 23:
            try:
                client_id = data[0]
                length = data[1]
                request_id = data[2]

                settings['aloss'] = words_to_float(data[3], data[4])
                settings['silence_cont'] = words_to_float(data[5], data[6])
                settings['silence_peak'] = words_to_float(data[7], data[8])
                settings['silence_cont_en'] = int(data[9] & 0x00ff)
                settings['silence_peak_en'] = int(data[9] >> 8)
                settings['silence_time'] = words_to_float(data[10], data[11])
                # data[12], data[13] - reserved
                settings['loudness_cont'] = words_to_float(data[14], data[15])
                settings['loudness_peak'] = words_to_float(data[16], data[17])
                settings['loudness_cont_en'] = int(data[18] & 0x00ff)
                settings['loudness_peak_en'] = int(data[18] >> 8)
                settings['loudness_time'] = words_to_float(data[19], data[20])
                # data[21], data[22] - reserved
            except:
                return None
            else:
                return settings
        else:
            return None

    def parse_tuner_settings(self, data, tuner_settings):

        new_tuner_settings = tuner_settings.copy()

        try:
            client_id = data[0]
            length = data[1]
            request_id = data[2]
        except:
            return None

        tuner_slot_length = 12 # in words

        try:
            for i in range(4):
                settings_block = data[8 + (tuner_slot_length*i):]
                settings = dict([('device',  int(settings_block[0] & 0x00ff)),
                                 ('c_freq', int(settings_block[2] | (settings_block[3] << 16))),
                                 ('t_freq', int(settings_block[4] | (settings_block[5] << 16))),
                                 ('t_bw', 2 - int(settings_block[6])),
                                 ('t2_freq', int(settings_block[8] | (settings_block[9] << 16))),
                                 ('t2_bw', 2 - int(settings_block[10])),
                                 ('t2_plp_id', int(settings_block[11] & 0x00ff))])
                new_tuner_settings.update({int(i): settings})
        except:
            return None
        else:
            return new_tuner_settings
