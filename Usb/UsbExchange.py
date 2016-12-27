import cyusb
import struct
import math

from Usb import UsbMessageTypes as usb_msgs
from Control import ProgramListControl
from Control.ErrorDetector.StatusTypes import STYPES


class UsbExchange():
    """UsbExchange class"""
    VERSION = 0x3
    TYPE = 0x2
    EXIT_RECEIVE = 0x40
    START_MSG = 0x10
    STOP_MSG = 0x20
    SEND_PERS_BUF = 0x0901
    # TODO: change prog num
    MAX_PROG_NUM = 20
    # max data size in one pers buf message (in words)
    MAX_DATA_SIZE = 243
    # max string size
    MAX_STR_SIZE = 26
    # 2: prefix
    # 2: code command
    HEADER = "HH"
    # 4: HEADER
    MSG_11 = HEADER
    # 4: HEADER
    # 1: type
    # 1: version
    # 2: reserved
    MSG_12 = HEADER + "BBH"
    # 4: HEADER
    # 2: length
    # 2: ts index
    # 4: ts num
    # 2: reserved
    # 2: err num
    ERR_MSG = HEADER + "HHIHH"
    # 2: index
    # 2: count
    # 1: err code
    # 1: err ext
    # 2: pid
    # 4: packet
    # 4: param 1
    # 4: param 2
    ERR_INFO = "HHBBHIII"

    def __init__(self):

        self.status_version = 0
        self.settings_version = 0
        self.dvb_cont_ver = 0
        self.dvb_stat_ver = 0
        self.lufs = [0]*self.MAX_PROG_NUM
        self.errs = [0]*self.MAX_PROG_NUM
        self.status_flags = 0

        self.is_connected = False

        self.is_connected = cyusb.init()
        if self.is_connected is True:
            self.connection = cyusb.Connection()

        self.cpu_load = 0

    def __destroy__(self):
        if self.is_connected is True:
            cyusb.close()

    def read(self):
        if self.is_connected is False:
            return b''

        buf = self.connection.recv()
        return struct.unpack("H"*int(len(buf)/2) + "B"*(len(buf) & 0x01), buf)

    def write(self, msg):
        if self.is_connected is True:
            self.connection.send(msg)

    def send_init(self):
        msg_code = (0x0100 | self.START_MSG) | \
                   (self.STOP_MSG | self.EXIT_RECEIVE)

        msg = struct.pack("="+self.MSG_12,
                          usb_msgs.PREFIX,
                          msg_code,
                          self.TYPE,
                          self.VERSION,
                          0)
        self.write(msg)

    def set_status(self, prog_idx, results):
        status = 0
        if results['vloss'] is STYPES['err']:
            status = status | 0x01
        if results['black'] is STYPES['err']:
            status = status | 0x02
        if results['freeze'] is STYPES['err']:
            status = status | 0x03
        if results['blocky'] is STYPES['err']:
            status = status | 0x04
        if results['aloss'] is STYPES['err']:
            status = status | 0x10
        if results['loudness'] is STYPES['err']:
            status = status | 0x20
        if results['silence'] is STYPES['err']:
            status = status | 0x30

        self.errs[prog_idx] = status

    def send_status(self):

        STATUS_MSG = self.HEADER
        # reserved, ts count, reserved
        STATUS_MSG += "IHB"
        # flags, stat ver, sett ver, video load, aud load,
        # dvbt2 stat ver, dvbt2 cont ver
        STATUS_MSG += "BBBBBBB"
        # err flags
        ERROR_MSG = "%sB" % self.MAX_PROG_NUM
        # loudness levels
        LOUD_MSG = "%sB" % self.MAX_PROG_NUM
        VOID_MSG = "%sH" % 225

        tmp_zer = [0 for _ in range(225)]

        msg_code = (0x0300 | self.START_MSG) | \
                   (self.STOP_MSG | self.EXIT_RECEIVE)

        b = struct.pack("="+STATUS_MSG,
                        usb_msgs.PREFIX,
                        msg_code,
                        0, 1, 0,
                        self.status_flags,
                        self.status_version & 0xff,
                        self.settings_version & 0xff,
                        int(self.cpu_load/100*255 + 0.5), 0,
                        self.dvb_stat_ver & 0xff,
                        self.dvb_cont_ver & 0xff)

        err = struct.pack("=%sB" % self.MAX_PROG_NUM, *self.errs)
        loud = struct.pack("=%sB" % self.MAX_PROG_NUM, *self.lufs)
        rsrvd = struct.pack("=%sH" % 225, *tmp_zer)

        msg = b''.join([b, err, loud, rsrvd])
        self.write(msg)

        self.lufs = [0]*self.MAX_PROG_NUM
        self.errs = [0]*self.MAX_PROG_NUM
        self.status_version += 1

    def send_status_old(self):

        STATUS_MSG = self.HEADER
        # reserved
        STATUS_MSG += "B"
        # flags, stat ver, sett ver, video load, aud load,
        # dvbt2 stat ver, dvbt2 cont ver
        STATUS_MSG += "BBBBBBB"
        # err flags
        ERROR_MSG = "%sB" % 12
        # loudness levels
        LOUD_MSG = "%sB" % 12

        msg_code = (0x0300 | self.START_MSG) | \
                   (self.STOP_MSG | self.EXIT_RECEIVE)

        b = struct.pack("="+STATUS_MSG,
                        usb_msgs.PREFIX,
                        msg_code,
                        0,
                        self.status_flags,
                        self.status_version & 0xff,
                        self.settings_version & 0xff,
                        int(self.cpu_load/100*255 + 0.5), 0,
                        self.dvb_stat_ver & 0xff,
                        self.dvb_cont_ver & 0xff)

        err = struct.pack("=%sB" % 12, *([0]*12))
        loud = struct.pack("=%sB" % 12, *([22]*12))

        msg = b''.join([b, err, loud])
        self.write(msg)

        self.lufs = [0]*self.MAX_PROG_NUM
        self.errs = [0]*self.MAX_PROG_NUM
        self.status_version += 1

    def send_errors(self):
        # header, length, TS index, TS num, reserved, err num

        # index, count, err code, err ext, pid, packet, param1, params
        ERR_INFO = "HHBBHIII"
        msg = struct.pack("="+self.ERR_MSG, #+ERR_INFO,
                          usb_msgs.PREFIX,
                          0x0401 | self.STOP_MSG | self.EXIT_RECEIVE,
                          5, 0, 0, 0, 0)
                          #0, 1, 0x12, 0, 2011, 0, 0, 0)

        self.write(msg)

        self.send_exit_errors()

    def send_exit_errors(self):
        msg_code = (0xFD00 | self.START_MSG) | \
                   (self.STOP_MSG | self.EXIT_RECEIVE)

        msg = struct.pack("="+self.MSG_12,
                          usb_msgs.PREFIX,
                          msg_code,
                          1,
                          1,
                          1)
        self.write(msg)

    def send_video_analysis_settings(self,
                                     aset,
                                     client_id,
                                     request_id):

        # header, length data, client id, msg cod, req id, length msg
        VIDEO_ANALYSIS_MSG = self.HEADER + "HHHHH"
        # vloss, black_cont, black_peak, black_cont_en, black_peak_en
        # luma_cont, luma_peak, luma_cont_en, luma_peak_en, black_time,
        # black_pixel, reserved
        # freeze_cont, freeze_peak, freeze_cont_en, freeze_peak_en
        # diff_cont, diff_peak, diff_cont_en, diff_peak_en, freeze_time,
        # pixel_diff, reserved
        # blocky_cont, blocky_peak, blocky_cont_en, blocky_peak_en,
        # blocky_time, block_size, reserved
        LEVELS = "fffBB"\
                 "ffBBfII"\
                 "ffBB"\
                 "ffBBfHI"\
                 "ffBBfII"

        # pack and send message
        msg = struct.pack("="+VIDEO_ANALYSIS_MSG+LEVELS,
                          usb_msgs.PREFIX,
                          self.SEND_PERS_BUF | self.EXIT_RECEIVE,
                          48,
                          client_id,
                          0xc514,
                          request_id,
                          44,
                          aset['vloss'],
                          aset['black_cont'],
                          aset['black_peak'],
                          int(aset['black_cont_en']),
                          int(aset['black_peak_en']),
                          aset['luma_cont'],
                          aset['luma_peak'],
                          int(aset['luma_cont_en']),
                          int(aset['luma_peak_en']),
                          aset['black_time'],
                          int(aset['black_pixel']),
                          0,
                          aset['freeze_cont'],
                          aset['freeze_peak'],
                          int(aset['freeze_cont_en']),
                          int(aset['freeze_peak_en']),
                          aset['diff_cont'],
                          aset['diff_peak'],
                          int(aset['diff_cont_en']),
                          int(aset['diff_peak_en']),
                          aset['freeze_time'],
                          int(aset['pixel_diff']),
                          0,
                          aset['blocky_cont'],
                          aset['blocky_peak'],
                          int(aset['blocky_cont_en']),
                          int(aset['blocky_peak_en']),
                          aset['blocky_time'],
                          8,
                          0)

        self.write(msg)

    def send_audio_analysis_settings(self,
                                     aset,
                                     client_id,
                                     request_id):

        # header, length data, client id, msg cod, req id, length msg
        AUDIO_ANALYSIS_MSG = self.HEADER + "HHHHH"
        # aloss, silence_cont, silence_peak, silence_cont_en, silence_peak_en, silence_time, reserved
        # loudness_cont, loudness_peak, loudness_cont_en, loudness_peak_en, loudness_time, reserved
        LEVELS = "fffBBfI"\
                 "ffBBfI"

        # pack and send message
        msg = struct.pack("="+AUDIO_ANALYSIS_MSG+LEVELS,
                          usb_msgs.PREFIX,
                          self.SEND_PERS_BUF | self.EXIT_RECEIVE,
                          24,
                          client_id,
                          0xc515,
                          request_id,
                          20,
                          aset['aloss'],
                          aset['silence_cont'],
                          aset['silence_peak'],
                          aset['silence_cont_en'],
                          aset['silence_peak_en'],
                          aset['silence_time'],
                          0,
                          aset['loudness_cont'],
                          aset['loudness_peak'],
                          aset['loudness_cont_en'],
                          aset['loudness_peak_en'],
                          aset['loudness_time'],
                          0)
        self.write(msg)


    # send prog lists (stream and analyzed) to remote client
    def send_prog_list(self, stream_progs, analyzed_progs,
                       client_id, request_id):

        # basic funtions needed for packing
        def get_len(prog_list):
            length = 0
            for stream in prog_list:
                for prog in stream[1]:
                    # prog info header len
                    length += (10 + 2*self.MAX_STR_SIZE)
                    for pid in prog[4]:
                        # pid info len
                        length += (30 + self.MAX_STR_SIZE)

            return length

        def get_prog_num(prog_list):
            prog_num = 0
            for stream in prog_list:
                prog_num += len(stream[1])

            return prog_num

        def encode_string(ustr):
            astr = ustr.encode('cp1251', 'replace')
            char_list = memoryview(astr).tolist()
            # if string is shorter that MAX_STR_SIZE bytes
            if len(char_list) < self.MAX_STR_SIZE:
                char_list.extend([0]*(self.MAX_STR_SIZE - len(char_list)))
            # if string is more than MAX_STR_SIZE bytes (or equal)
            else:
                char_list = char_list[:self.MAX_STR_SIZE]
                char_list[self.MAX_STR_SIZE - 1] = 0

            return char_list

        def pack_prog_list(prog_list):
            # pack stream prog list
            # wparam, streams num, prog num
            strm_msg = struct.pack("=IHH",
                                   0,
                                   len(prog_list),
                                   get_prog_num(prog_list))

            for stream in prog_list:
                stream_id = stream[0]
                for prog in stream[1]:
                    prog_name = encode_string(prog[1])
                    prov_name = encode_string(prog[2])
                    prog_id = int(prog[0])
                    pids_num = len(prog[4])

                    # wparam, stream id
                    prg_hdr = struct.pack("=IH", 0, stream_id)
                    # prog name
                    prg_name = struct.pack("=" + self.MAX_STR_SIZE*"B",
                                           *prog_name)
                    # prov name
                    prv_name = struct.pack("=" + self.MAX_STR_SIZE*"B",
                                           *prov_name)
                    # prog type, pids num
                    prg_end = struct.pack("=HH", prog_id, pids_num)

                    prg_msg = b''.join([prg_hdr, prg_name, prv_name, prg_end])

                    for pid in prog[4]:
                        pid_type_str = pid[2].split('-')[0]

                        if (pid_type_str == 'audio') or \
                           (pid_type_str == 'video'):

                            codec_name = encode_string(pid[2])
                            codec_int = int(pid[1])

                            if pid_type_str == 'video':
                                pid_type = 2
                                # width, height, aspect x,
                                # aspect y, frame rate
                                pid_prms = struct.pack("=IIIIf",
                                                       0, 0, 0, 0, 0.0)
                            elif pid_type_str == 'audio':
                                pid_type = 1
                                # ch num, sample rate, bitrate,
                                # reserved, reserved
                                pid_prms = struct.pack("=IIIIf",
                                                       0, 0, 0, 0, 0.0)

                            # wparam, pid, type, codec
                            pid_hdr = struct.pack("=IHHH",
                                                  0,
                                                  int(pid[0]),
                                                  pid_type,
                                                  codec_int)
                            # codec name
                            cdc_name = struct.pack("=" + self.MAX_STR_SIZE*"B",
                                                   *codec_name)

                            pid_msg = b''.join([pid_hdr, cdc_name, pid_prms])

                            # join with prog message
                            prg_msg = b''.join([prg_msg, pid_msg])

                    # join with stream message
                    strm_msg = b''.join([strm_msg, prg_msg])

            return strm_msg

        # stream info header len
        # *2 - because we send 2 lists - stream and analyzed
        msg_len = 8 * 2
        msg_len += get_len(stream_progs)
        msg_len += get_len(analyzed_progs)

        # pack stream and analyzed prog lists to byte arrays
        packed_stream_progs = pack_prog_list(stream_progs)
        packed_analyzed_progs = pack_prog_list(analyzed_progs)
        # concatenate two arrays
        msg_data = b''.join([packed_stream_progs, packed_analyzed_progs])

        # calculate total messages needed to transmit prog lists
        msg_parts_num = math.ceil(int(msg_len/2)/self.MAX_DATA_SIZE)

        # send n messages to remote client
        for i in range(msg_parts_num):

            # if this message is first
            if i == 0:
                msg_code = 0xc516
                offset = msg_len >> 1  # divide by 2
            else:
                msg_code = 0xc516 & 0x7fff
                offset = i*self.MAX_DATA_SIZE

            # if this message is last
            if i == msg_parts_num - 1:
                data_len = int(msg_len/2) - \
                           (msg_parts_num - 1)*self.MAX_DATA_SIZE + 4
                cod_command = self.SEND_PERS_BUF | self.EXIT_RECEIVE
            else:
                data_len = self.MAX_DATA_SIZE + 4
                cod_command = self.SEND_PERS_BUF

            # pack message header
            # header, length data, client id, msg cod, req id, length msg
            PROG_LIST_MSG = self.HEADER + "HHHHH"
            hdr = struct.pack("="+PROG_LIST_MSG,
                              usb_msgs.PREFIX,
                              cod_command,
                              data_len,
                              client_id,
                              msg_code,
                              request_id,
                              offset)

            # slice total data payload into parts
            # *2 - because we manipulate bytes, not words
            if i == 0:
                d = msg_data[:self.MAX_DATA_SIZE*2]
            elif i == msg_parts_num - 1:
                d = msg_data[offset*2:]
            else:
                d = msg_data[offset*2:(i+1)*self.MAX_DATA_SIZE*2]

            # pack message data slice
            data = struct.pack("="+"B"*len(d), *d)
            # concatenate header and data
            msg = b''.join([hdr, data])
            # send message
            self.write(msg)

    def send_tuner_settings(self,
                            tuner_settings,
                            client_id,
                            request_id):

        # header, length data, client id, msg cod, req id, length msg
        TUNER_SET_MSG = self.HEADER + "HHHHH" # 10 bytes
        # control, data len, reserved, reserved
        CTRL_DATA = "BBII"  # 10 bytes
        # device, reserved, reserved, c freq, t freq, t band, reserve,
        # t2 freq, t2 band, t2 plp id, reserved
        PARAMS = "BBHIIHHIHBB"

        settings_msg = struct.pack("="+TUNER_SET_MSG+CTRL_DATA,
                              usb_msgs.PREFIX,
                              self.SEND_PERS_BUF | self.EXIT_RECEIVE,
                              68,
                              client_id,
                              0xc518,
                              request_id,
                              64,
                              self.dvb_cont_ver & 0xf, 96, 0, 0)

        for slot_index, slot_settings in tuner_settings.items():
            slot_msg = struct.pack("="+PARAMS,
                                   slot_settings['device'],
                                   0, 0,
                                   slot_settings['c_freq'],
                                   slot_settings['t_freq'],
                                   2 - slot_settings['t_bw'],
                                   0,
                                   slot_settings['t2_freq'],
                                   2 - slot_settings['t2_bw'],
                                   slot_settings['t2_plp_id'],
                                   0)
            settings_msg = b''.join([settings_msg, slot_msg])

        RESERVED = "B"*22
        rsrvd = struct.pack("="+RESERVED,
                            *[0 for _ in range(22)])

        msg = b''.join([settings_msg, rsrvd])
        self.write(msg)

    def send_tuner_status(self,
                          tuner_status,
                          tuner_params,
                          tuner_measured_data,
                          tuner_settings,
                          client_id,
                          request_id):

        if len(tuner_params) != 0:
            if tuner_params[0] == 0x8000:
                status = 0x8000
            else:
                # FIXME: change 0x1, 0x2 to constants
                level_ok = bool(tuner_params[0] & 0x1)
                lock_ok = bool(tuner_params[0] & 0x2)
                if level_ok is False:
                    status = 0x0000
                elif lock_ok is False:
                    status = 0x0100
                else:
                    status = 0x0300
        else:
            status = 0x8000

        if len(tuner_measured_data) != 0:
            mer = tuner_measured_data[0]
            ber1 = tuner_measured_data[2]
            ber2 = tuner_measured_data[4]
            ber3 = tuner_measured_data[6]
        else:
            mer = 0.0
            ber1 = 0.0
            ber2 = 0.0
            ber3 = 0.0

        # header, length data, client id, msg cod, req id, length msg
        TUNER_STATUS_HDR = self.HEADER + "HHHHH"

        # stat ver, data len, opt type, opt ver, reserved, reserved,
        # device, reserved, status, mer, ber1, ber2, ber3
        TUNER_STATUS_DATA = "BBBBIHBBHffff"

        # FIXME temp!!!
        device = 0

        msg = struct.pack("="+TUNER_STATUS_HDR+TUNER_STATUS_DATA,
                          usb_msgs.PREFIX,
                          self.SEND_PERS_BUF | self.EXIT_RECEIVE,
                          19,
                          client_id,
                          0xc519,
                          request_id,
                          15,
                          self.dvb_stat_ver & 0xff,
                          10,
                          9, 2,
                          0, 0,
                          device,
                          0,
                          status,
                          mer, ber1, ber2, ber3)

        self.write(msg)

