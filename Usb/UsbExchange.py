import cyusb
import struct
import random

from gi.repository import GObject

from Usb import UsbMessageTypes as usb_msgs

class UsbExchange(GObject.GObject):
    """UsbExchange class"""
    PREFIX = 0x55AA
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
    
    def __init__(self,
                 stream_progs_model = [],
                 analyzed_progs_model = [],
                 error_model = [],
                 tuner_model = []):
        
        GObject.GObject.__init__(self)

        self.status_version = 0
        self.settings_version = 0
        self.dvb_cont_ver = 0
        self.dvb_stat_ver = 0
        
        cyusb.init()

        self.connection = cyusb.Connection()

        self.state = 0
        self.msg_count = 0
        self.init_done = False
        self.cpu_load = 0

        GObject.timeout_add(1000, self.read)

    def __destroy__(self):
        cyusb.close()

    def write(self):
        if self.init_done is False:
            self.send_init()
        else:
            self.send_status()
            self.status_version += 1
            self.send_errors()

            #print("settings version: ", self.settings_version)
            #print("status_version: ", self.status_version)
            #print("tuner set ver: ", self.dvb_cont_ver)
            #print("tuner stat ver:", self.dvb_stat_ver)

    def read(self):
        buf = self.connection.recv()

        buf = struct.unpack("H"*int(len(buf)/2), buf)

        for i, word in enumerate(buf):
            if word == self.PREFIX:
                self.state = self.PREFIX
                self.msg_count = 0
                continue

            if self.state == self.PREFIX:
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

            elif self.state == usb_msgs.SET_BOARD_MODE_EXT:
                if self.msg_count == 0:
                    print("usb set board mode ext")

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
                    print("usb get video analysis settings")

            elif self.state == usb_msgs.GET_AUDIO_ANALYSIS_SETTINGS:
                if self.msg_count == 0:
                    print("usb get audio analysis settings")

            elif self.state == usb_msgs.GET_ANALYZED_PROG_LIST:
                if self.msg_count == 0:
                    print("usb get analyzed prog list")

            elif self.state == usb_msgs.RESET:
                if self.msg_count == 0:
                    print("usb reset")

            elif self.state == usb_msgs.GET_TUNER_SETTINGS:
                if self.msg_count == 0:
                    print("usb get tuner settings")

            elif self.state == usb_msgs.GET_TUNER_STATUS:
                if self.msg_count == 0:
                    print("usb get tuner status")

            elif self.state == usb_msgs.POWEROFF:
                if self.msg_count == 0:
                    print("usb poweroff")

            self.msg_count += 1

    def message_parser(self, message):
        pass

    def send_init(self):
        tmp = (0x0100 | self.START_MSG | self.STOP_MSG | self.EXIT_RECEIVE)
        b = struct.pack("="+self.MSG_12,
                        self.PREFIX,
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
                        self.PREFIX,
                        (0x0300 | self.START_MSG | self.STOP_MSG | self.EXIT_RECEIVE),
                        0, 0, 0, 1, 0,
                        0,
                        self.status_version % 255,
                        self.settings_version % 255,
                        int(self.cpu_load/100*255 + 0.5), 0,
                        self.dvb_stat_ver % 255,
                        self.dvb_cont_ver % 255)

        err = struct.pack("=%sB" % self.MAX_PROG_NUM, *tmp_err)
        lou = struct.pack("=%sB" % self.MAX_PROG_NUM, *tmp_lou)
        zer = struct.pack("=%sH" % 225, *tmp_zer)

        msg = b''.join([b, err, lou, zer])
        #for i in b:
        #    print("%x" % i)
        #print (len(msg))
        self.connection.send(msg)

    def send_errors(self):
        pass

    def send_prog_list(self):
        PROG_MSG = self.HEADER + "HHHHH" #+ ("%sH" % MAX_DATA_SIZE)
        b = struct.pack("="+PROG_MSG,
                        self.PREFIX,
                        self.SEND_PERS_BUF,
                        100,
                        0,
                        1,
                        0,
                        0)
        data = [0 for _ in range(self.MAX_DATA_SIZE)]
        msg = struct.pack("=%sH" % self.MAX_DATA_SIZE, *data)
        s = b''.join([b, msg])
        self.connection.send(s)

