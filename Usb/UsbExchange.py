import cyusb
import struct
import random

from Usb import UsbMessageTypes as usb_msgs
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
    MAX_DATA_SIZE = 243
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
        return self.connection.recv()

    def send_init(self):
        tmp = (0x0100 | self.START_MSG | self.STOP_MSG | self.EXIT_RECEIVE)
        b = struct.pack("="+self.MSG_12,
                        usb_msgs.PREFIX,
                        tmp,
                        self.TYPE,
                        self.VERSION,
                        0)
        self.connection.send(b)

    def send_status(self):
        STATUS_MSG = self.HEADER
        # reserved, ts count, reserved 
        STATUS_MSG += "HHBBB"
        # flags, stat ver, sett ver, video load, aud load, dvbt2 stat ver, dvbt2 cont ver
        STATUS_MSG += "BBBBBBB"
        # err flags
        ERROR_MSG = "%sB" % self.MAX_PROG_NUM
        # loudness levels
        LOUD_MSG = "%sB" % self.MAX_PROG_NUM
        VOID_MSG = "%sH" % 225

        tmp_err = [0 for _ in range(self.MAX_PROG_NUM)]
        tmp_lou = [0 for _ in range(self.MAX_PROG_NUM)]
        tmp_zer = [0 for _ in range(225)]

        b = struct.pack("="+STATUS_MSG,
                        usb_msgs.PREFIX,
                        (0x0300 | self.START_MSG | self.STOP_MSG | self.EXIT_RECEIVE),
                        0, 0, 0, 1, 0,
                        0,
                        self.status_version & 0xff,
                        self.settings_version & 0xff,
                        int(self.cpu_load/100*255 + 0.5), 0,
                        self.dvb_stat_ver & 0xff,
                        self.dvb_cont_ver & 0xff)

        err = struct.pack("=%sB" % self.MAX_PROG_NUM, *tmp_err)
        lou = struct.pack("=%sB" % self.MAX_PROG_NUM, *tmp_lou)
        zer = struct.pack("=%sH" % 225, *tmp_zer)

        msg = b''.join([b, err, lou, zer])
        self.connection.send(msg)

    def send_errors(self):
        pass

    def send_video_analysis_settings(self,
                                     analysis_settings,
                                     client_id,
                                     request_id):

        # header, length data, client id, msg cod, req id, length msg
        VIDEO_ANALYSIS_MSG = self.HEADER + "HHHHH"
        b = struct.pack("="+VIDEO_ANALYSIS_MSG,
                        usb_msgs.PREFIX,
                        self.SEND_PERS_BUF | self.EXIT_RECEIVE,
                        20,
                        client_id,
                        0xc514,
                        request_id,
                        16)

        # level black warn, level black, level freeze warn, level freeze
        # level diff warn, time to video loss, level luma warn
        LEVELS = "fffffBB"
        lvls = struct.pack("="+LEVELS,
                           float(analysis_settings[ai.BLACK_WARN][2]),
                           float(analysis_settings[ai.BLACK_ERR][2]),
                           float(analysis_settings[ai.FREEZE_WARN][2]),
                           float(analysis_settings[ai.FREEZE_ERR][2]),
                           float(analysis_settings[ai.DIFF_WARN][2]),
                           int(analysis_settings[ai.VIDEO_LOSS][2]),
                           int(analysis_settings[ai.LUMA_WARN][2]))

        # num of black frames, black level, pixel diff, num of freeze frames
        PARAMS = "BBBB"
        prms = struct.pack("="+PARAMS,
                           int(analysis_settings[ai.BLACK_ERR][5]),
                           int(analysis_settings[ai.BLACK_PIXEL][2]),
                           int(analysis_settings[ai.PIXEL_DIFF][2]),
                           int(analysis_settings[ai.FREEZE_ERR][5]))

        RESERVED = "HI"
        rsrvd = struct.pack("="+RESERVED,
                            0, 0)

        msg = b''.join([b, lvls, prms, rsrvd])
        self.connection.send(msg)

    def send_audio_analysis_settings(self,
                                     analysis_settings,
                                     client_id,
                                     request_id):

        # header, length data, client id, msg cod, req id, length msg
        AUDIO_ANALYSIS_MSG = self.HEADER + "HHHHH"
        b = struct.pack("="+AUDIO_ANALYSIS_MSG,
                        usb_msgs.PREFIX,
                        self.SEND_PERS_BUF | self.EXIT_RECEIVE,
                        16,
                        client_id,
                        0xc515,
                        request_id,
                        12)

        # level black warn, level black, level freeze warn, level freeze
        # level diff warn, time to video loss, level luma warn
        LEVELS = "ffffB"
        lvls = struct.pack("="+LEVELS,
                           float(analysis_settings[ai.OVERLOAD_WARN][2]),
                           float(analysis_settings[ai.OVERLOAD_ERR][2]),
                           float(analysis_settings[ai.SILENCE_WARN][2]),
                           float(analysis_settings[ai.SILENCE_ERR][2]),
                           int(analysis_settings[ai.AUDIO_LOSS][2]))

        RESERVED = "BHI"
        rsrvd = struct.pack("="+RESERVED,
                            0, 0, 0)

        msg = b''.join([b, lvls, rsrvd])
        self.connection.send(msg)

    def send_analyzed_prog_list(self,
                                analyzed_progs,
                                client_id,
                                request_id):

        PROG_LIST_MSG = self.HEADER + "HHHHH"
        b = struct.pack("="+PROG_LIST_MSG,
                        usb_msgs.PREFIX,
                        self.SEND_PERS_BUF | self.EXIT_RECEIVE,
                        100,
                        client_id,
                        0xc516,
                        request_id,
                        1)
        data = [0 for _ in range(self.MAX_DATA_SIZE)]
        msg = struct.pack("=%sH" % self.MAX_DATA_SIZE, *data)
        s = b''.join([b, msg])
        #self.connection.send(s)

    def send_tuner_settings(self,
                            tuner_settings,
                            client_id,
                            request_id):

        TUNER_SET_MSG = self.HEADER + "HHHHH"
        b = struct.pack("="+TUNER_SET_MSG,
                        usb_msgs.PREFIX,
                        self.SEND_PERS_BUF | self.EXIT_RECEIVE,
                        68,
                        client_id,
                        0xc518,
                        request_id,
                        64)

        # control, data len, reserved, reserved
        CTRL_DATA = "BBII"
        ctrl = struct.pack("="+CTRL_DATA,
                           self.dvb_cont_ver & 0xf,
                           54,
                           0, 0)

        # device, reserved, reserved, c freq, t freq, t band, reserve,
        # t2 freq, t2 band, t2 plp id
        PARAMS = "BBHIIHHIHB"
        prms = struct.pack("="+PARAMS,
                           tuner_settings[ti.DEVICE][0],
                           0, 0,
                           tuner_settings[ti.C_FREQ][0],
                           tuner_settings[ti.T_FREQ][0],
                           tuner_settings[ti.T_BW][0],
                           0,
                           tuner_settings[ti.T2_FREQ][0],
                           tuner_settings[ti.T2_BW][0],
                           tuner_settings[ti.T2_PLP_ID][0])

        RESERVED = "B"*95
        rsrvd = struct.pack("="+RESERVED,
                            *[0 for _ in range(95)])

        msg = b''.join([b, ctrl, prms, rsrvd])
        self.connection.send(msg)

