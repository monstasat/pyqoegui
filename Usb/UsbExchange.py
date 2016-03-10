import cyusb
import struct

class UsbExchange:
    """UsbExchange class"""
    PREFIX = 0x55AA
    VERSION = 0x3
    TYPE = 0x2
    EXIT_RECEIVE = 0x40
    START_MSG = 0x10
    STOP_MSG = 0x20
    MSG_VAR_LEN = 0x01
    MSG_CRC = 0x02
    # TODO: change prog num
    MAX_PROG_NUM = 20
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
        
        self.status_version = 0
        self.settings_version = 0
        self.dvb_cont_ver = 0
        self.dvb_stat_ver = 0
        
        cyusb.init()
        self.connection = cyusb.Connection()

    def __destroy__(self):
        cyusb.close()

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

        tmp_err = [0x11 for _ in range(self.MAX_PROG_NUM)]
        tmp_lou = [25 for _ in range(self.MAX_PROG_NUM)]
        tmp_zer = [0 for _ in range(225)]
        
        b = struct.pack("="+STATUS_MSG,
                        self.PREFIX,
                        (0x0300 | self.START_MSG | self.STOP_MSG | self.EXIT_RECEIVE),
                        0, 0 , 0, 1, 0,
                        0,
                        self.status_version,
                        self.settings_version,
                        50, 25,
                        self.dvb_stat_ver,
                        self.dvb_cont_ver)

        err = struct.pack("=%sB" % self.MAX_PROG_NUM, *tmp_err)
        lou = struct.pack("=%sB" % self.MAX_PROG_NUM, *tmp_lou)
        zer = struct.pack("=%sH" % 225, *tmp_zer)

        msg = b''.join([b, err, lou, zer])
        for i in b:
            print("%x" % i)
        print (len(msg))
        self.connection.send(msg)
