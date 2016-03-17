import cyusb
import struct
import random
import math

from Usb import UsbMessageTypes as usb_msgs
from Control import ProgramListControl
from Control import AnalysisSettingsIndexes as ai
from Control import TunerSettingsIndexes as ti


class UsbExchange():
    """UsbExchange class"""
    VERSION = 0x3
    TYPE = 0x2
    EXIT_RECEIVE = 0x40
    START_MSG = 0x10
    STOP_MSG = 0x20
    MSG_VAR_LEN = 0x01
    MSG_CRC = 0x02
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

        cyusb.init()

        self.connection = cyusb.Connection()

        self.cpu_load = 0

    def __destroy__(self):
        cyusb.close()

    def read(self):
        buf = self.connection.recv()
        fmt = "H"*int(len(buf)/2) + "B"*(len(buf) & 0x01)
        buf = struct.unpack(fmt, buf)
        return buf

    def send_init(self):
        msg_code = (0x0100 | self.START_MSG) | \
                   (self.STOP_MSG | self.EXIT_RECEIVE)

        msg = struct.pack("="+self.MSG_12,
                          usb_msgs.PREFIX,
                          msg_code,
                          self.TYPE,
                          self.VERSION,
                          0)
        self.connection.send(msg)

    def send_status(self):
        STATUS_MSG = self.HEADER
        # reserved, ts count, reserved
        STATUS_MSG += "HHBBB"
        # flags, stat ver, sett ver, video load, aud load,
        # dvbt2 stat ver, dvbt2 cont ver
        STATUS_MSG += "BBBBBBB"
        # err flags
        ERROR_MSG = "%sB" % self.MAX_PROG_NUM
        # loudness levels
        LOUD_MSG = "%sB" % self.MAX_PROG_NUM
        VOID_MSG = "%sH" % 225

        tmp_err = [0 for _ in range(self.MAX_PROG_NUM)]
        tmp_lou = [0 for _ in range(self.MAX_PROG_NUM)]
        tmp_zer = [0 for _ in range(225)]

        msg_code = (0x0300 | self.START_MSG) | \
                   (self.STOP_MSG | self.EXIT_RECEIVE)

        b = struct.pack("="+STATUS_MSG,
                        usb_msgs.PREFIX,
                        msg_code,
                        0, 0, 0, 1, 0,
                        0,
                        self.status_version & 0xff,
                        self.settings_version & 0xff,
                        int(self.cpu_load/100*255 + 0.5), 0,
                        self.dvb_stat_ver & 0xff,
                        self.dvb_cont_ver & 0xff)

        err = struct.pack("=%sB" % self.MAX_PROG_NUM, *tmp_err)
        loud = struct.pack("=%sB" % self.MAX_PROG_NUM, *tmp_lou)
        rsrvd = struct.pack("=%sH" % 225, *tmp_zer)

        msg = b''.join([b, err, loud, rsrvd])
        self.connection.send(msg)

    def send_errors(self):
        pass

    def send_video_analysis_settings(self,
                                     analysis_settings,
                                     client_id,
                                     request_id):

        # header, length data, client id, msg cod, req id, length msg
        VIDEO_ANALYSIS_MSG = self.HEADER + "HHHHH"
        # level black warn, level black, level freeze warn, level freeze
        # level diff warn, time to video loss, level luma warn
        LEVELS = "fffffBB"
        # num of black frames, black level, pixel diff, num of freeze frames
        PARAMS = "BBBB"
        RESERVED = "HI"

        msg = struct.pack("="+VIDEO_ANALYSIS_MSG+LEVELS+PARAMS+RESERVED,
                          usb_msgs.PREFIX,
                          self.SEND_PERS_BUF | self.EXIT_RECEIVE,
                          20,
                          client_id,
                          0xc514,
                          request_id,
                          16,
                          float(analysis_settings[ai.BLACK_WARN][2]),
                          float(analysis_settings[ai.BLACK_ERR][2]),
                          float(analysis_settings[ai.FREEZE_WARN][2]),
                          float(analysis_settings[ai.FREEZE_ERR][2]),
                          float(analysis_settings[ai.DIFF_WARN][2]),
                          int(analysis_settings[ai.VIDEO_LOSS][2]),
                          int(analysis_settings[ai.LUMA_WARN][2]),
                          int(analysis_settings[ai.BLACK_ERR][5]),
                          int(analysis_settings[ai.BLACK_PIXEL][2]),
                          int(analysis_settings[ai.PIXEL_DIFF][2]),
                          int(analysis_settings[ai.FREEZE_ERR][5]),
                          0, 0)

        self.connection.send(msg)

    def send_audio_analysis_settings(self,
                                     analysis_settings,
                                     client_id,
                                     request_id):

        # header, length data, client id, msg cod, req id, length msg
        AUDIO_ANALYSIS_MSG = self.HEADER + "HHHHH"
        # level black warn, level black, level freeze warn, level freeze
        # level diff warn, time to video loss, level luma warn
        LEVELS = "ffffB"
        RESERVED = "BHI"
        msg = struct.pack("="+AUDIO_ANALYSIS_MSG+LEVELS+RESERVED,
                          usb_msgs.PREFIX,
                          self.SEND_PERS_BUF | self.EXIT_RECEIVE,
                          16,
                          client_id,
                          0xc515,
                          request_id,
                          12,
                          float(analysis_settings[ai.OVERLOAD_WARN][2]),
                          float(analysis_settings[ai.OVERLOAD_ERR][2]),
                          float(analysis_settings[ai.SILENCE_WARN][2]),
                          float(analysis_settings[ai.SILENCE_ERR][2]),
                          int(analysis_settings[ai.AUDIO_LOSS][2]),
                          0, 0, 0)

        self.connection.send(msg)

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
            self.connection.send(msg)

    def send_tuner_settings(self,
                            tuner_settings,
                            client_id,
                            request_id):

        # header, length data, client id, msg cod, req id, length msg
        TUNER_SET_MSG = self.HEADER + "HHHHH"
        # control, data len, reserved, reserved
        CTRL_DATA = "BBII"
        # device, reserved, reserved, c freq, t freq, t band, reserve,
        # t2 freq, t2 band, t2 plp id
        PARAMS = "BBHIIHHIHB"

        msg = struct.pack("="+TUNER_SET_MSG+CTRL_DATA+PARAMS,
                          usb_msgs.PREFIX,
                          self.SEND_PERS_BUF | self.EXIT_RECEIVE,
                          68,
                          client_id,
                          0xc518,
                          request_id,
                          64,
                          self.dvb_cont_ver & 0xf,
                          54,
                          0, 0,
                          tuner_settings[ti.DEVICE][0],
                          0, 0,
                          tuner_settings[ti.C_FREQ][0],
                          tuner_settings[ti.T_FREQ][0],
                          2 - tuner_settings[ti.T_BW][0],
                          0,
                          tuner_settings[ti.T2_FREQ][0],
                          2 - tuner_settings[ti.T2_BW][0],
                          tuner_settings[ti.T2_PLP_ID][0])

        RESERVED = "B"*95
        rsrvd = struct.pack("="+RESERVED,
                            *[0 for _ in range(95)])

        msg = b''.join([msg, rsrvd])
        self.connection.send(msg)

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
                          tuner_settings[ti.DEVICE][0],
                          0,
                          status,
                          mer,
                          ber1,
                          ber2,
                          ber3)

        self.connection.send(msg)

