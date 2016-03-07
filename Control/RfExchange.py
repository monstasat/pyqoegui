import serial
import sys
import glob
import struct
import threading
import time
from concurrent import futures

from gi.repository import GObject

from Control import TunerSettingsModel as tm
from Control import CustomMessages

# msg start byte
START_BYTE = 0x55
# msg address
ADDRESS = 0xB5
# msg source
SOURCE = 0x01

# commands
COD_COMAND_GET_STATUS = 1
COD_COMAND_SET_PARAMS = 28
COD_COMAND_GET_PARAMS = 33
COD_COMAND_GET_MER_BER = 29
COD_COMAND_GET_CH_LEVEL = 46
COD_COMAND_GET_VERSION_INFO = 49
COD_COMAND_RESET = 5


# class for dvb-t2 tuner management via com-port
class RfExchange(GObject.GObject):

    __gsignals__ = {
        CustomMessages.NEW_TUNER_STATUS: (GObject.SIGNAL_RUN_FIRST,
                                          None, (int, int, int)),
        CustomMessages.NEW_TUNER_MEASURED_DATA: (GObject.SIGNAL_RUN_FIRST,
                                                 None,
                                                 (float,
                                                  bool,
                                                  float,
                                                  bool,
                                                  float,
                                                  bool,
                                                  float,
                                                  bool)),
        CustomMessages.NEW_TUNER_PARAMS: (GObject.SIGNAL_RUN_FIRST,
                                          None, (int, int, int))}

    def __init__(self, settings):
        GObject.GObject.__init__(self)
        self.serial = serial.Serial()
        self.is_opened = False

        self.connect_to_port()

        #self.apply_settings(settings)

        GObject.timeout_add(1000, self.on_read_tuner)

    def on_read_tuner(self):
        executor = futures.ProcessPoolExecutor()
        future = executor.submit(read_from_port, self)
        future.add_done_callback(self.done_callback)

        return True

    def done_callback(self, future):
        results = future.result()
        status = results[0]
        measured_data = results[1]
        params = results[2]

        if len(status) != 0:
            self.emit(CustomMessages.NEW_TUNER_STATUS,
                      status[0],            # status
                      status[1],            # hw errors
                      status[2])            # temperature

        if len(measured_data) != 0:
            self.emit(CustomMessages.NEW_TUNER_MEASURED_DATA,
                      measured_data[0],     # mer
                      measured_data[1],     # mer updated
                      measured_data[2],     # ber1
                      measured_data[3],     # ber1 updated
                      measured_data[4],     # ber2
                      measured_data[5],     # ber2 updated
                      measured_data[6],     # ber3
                      measured_data[7],)    # ber3 updated

        if len(params) != 0:
            self.emit(CustomMessages.NEW_TUNER_PARAMS,
                      params[0],            # status
                      params[1],            # modulation
                      params[2])            # params

    def read(self, size):
        buf = b""
        if self.is_opened is True:
            try:
                buf = self.serial.read(size=size)
            except:
                buf = b''

        return buf

    def write(self, msg):
        if self.is_opened is True:
            try:
                self.serial.write(msg)
            except:
                pass

    def connect_to_port(self):
        # configure com port
        try:
            self.serial.baudrate = 115200
            self.serial.port = '/dev/ttyUSB0'
            self.serial.parity = serial.PARITY_NONE
            self.serial.bytesize = serial.EIGHTBITS
            self.serial.stopbits = serial.STOPBITS_ONE
            self.serial.timeout = 1
        except:
            self.is_opened = False
            return False

        # open com port
        try:
            self.serial.open()
        # couldn't open port
        except serial.SerialException:
            print("exception")
            self.is_opened = False
            return False
        else:
            self.is_opened = True
            return True

    def disconnect(self):
        # close com port
        self.serial.close()
        self.is_opened = False

    def check_start_byte(self, byte):
        if byte == START_BYTE:
            return True
        else:
            return False

    def tuner_get_status(self):

        # construct message``
        msg = struct.pack("=BBHB",
                          START_BYTE,
                          SOURCE,
                          2,
                          COD_COMAND_GET_STATUS)

        # compute and append crc to message
        crc = self.compute_crc(msg[1:])
        msg += struct.pack('B', crc)

        # send message to tuner
        self.write(msg)

        # read tuner answer
        buf = self.read(20)

        data = []
        if len(buf) == 20:
            # start byte, address, length, command
            # status, num cur channel, ch count, hw errors, temperature,
            # page num, page size, reserved, crc
            buf_list = struct.unpack("=BBHBBBBHBHHIB", buf)
            if self.check_start_byte(buf_list[0]) is True:
                status = buf_list[4]
                hw_errors = buf_list[7]
                temperature = buf_list[8]
                data = [status, hw_errors, temperature]

        # return received data
        return data

    def tuner_set_params(self, tuner_settings):

        # tuner settings format:
        # device, t2 freq, t2 bw, t2 plp id, t freq, t bw, c freq

        # get settings from received settings list.
        # check input settings list
        # if list is not compatible, return empty array
        if len(tuner_settings) != 7:
            return []
        else:
            device = tuner_settings[0][0]
            # if standard is DVB-T2
            if device == tm.DVBT2:
                frequency = tuner_settings[1][0]
                modulation = 9
                width = tuner_settings[2][0]
                dvb_c_t_t2_params = tuner_settings[3][0]
            # if standard is DVB-T
            elif device == tm.DVBT:
                frequency = tuner_settings[4][0]
                modulation = 6
                width = tuner_settings[5][0]
                dvb_c_t_t2_params = 0
            # if standard is DVB-C
            elif device == tm.DVBC:
                frequency = tuner_settings[6][0]
                modulation = 3
                width = 0
                dvb_c_t_t2_params = 0
            # if standard is unknown, return empty array
            else:
                print("unknown")
                return []

        # [15:3] - reserved, [12:10] - khz, [9:0] - mhz
        mhz = frequency // 1000000
        khz = int(frequency % 1000000 / 1000) // 125
        frequency = (khz << 10) | mhz

        # modulation
        # 0 - unknown
        # 3 - DVB-C/QAM64
        # 4 - DVB-C/QAM128
        # 5 - DVB-C/QAM256
        # 6 - DVB-T/QPSK
        # 7 - DVB-T/QAM16
        # 8 - DVB-T/QAM64
        # 9 - DVB-T2

        # dvb_c_t_t2_params
        # for dvb-c:
        # dvb_c_t_t2_params[15..0]
        # sr: symbol rate in KSps (5000..7000)

        # for dvb-t:
        # dvb_c_t_t2_params[15..14]
        # fft: 0 - 2K, 1 - 8K
        # dvb_c_t_t2_params[13..12]
        # gui: 0 - 1/32, 1 - 1/16, 2 - 1/8, 3 - 1/4
        # dvb_c_t_t2_params[11..10]
        # hierarch: 0 - w/out, 1 - a = 1, 2 - a = 2, 3 - a = 4
        # dvb_c_t_t2_params[9]
        # spectrum: 0 - straight, 1 - iverted
        # dvb_c_t_t2_params[8:6]
        # fec_lp: 0 - 1/2, 1 - 2/3, 2 - 3/4, 3 - 5/6, 4 - 7/8
        # dvb_c_t_t2_params[5:3]
        # fec_hp: 0 - 1/2, 1 - 2/3, 2 - 3/4, 3 - 5/6, 4 - 7/8
        # dvb_c_t_t2_params[2:1]
        # bw: 0 - 6 MHz, 1 - 7 MHz, 2 - 8 MHz
        # dvb_c_t_t2_params[0]
        # reserved

        # for dvb-t2
        # dvb_c_t_t2_params[15:8]
        # plp_id
        # dvb_c_t_t2_params[7:4]
        # qam_id: 0 - QPSK, 1 - QAM16, 2 - QAM64, 3 - QAM256
        # dvb_c_t_t2_params[3:2]
        # reserved
        # dvb_c_t_t2_params[1:0]
        # bw: 0 - 6 MHz, 1 - 7 MHz, 2 - 8 MHz

        # width
        # 0 - 6 mhz, 1 - 7 mhz, 2 - 8 mhz

        # construct message
        msg = struct.pack('=BBHBBHBHBBH',
                          START_BYTE,               # message start (byte)
                          SOURCE,                   # message source (byte)
                          12,                       # message length (word)
                          COD_COMAND_SET_PARAMS,    # message code (byte)
                          0,                        # reserved (byte)
                          frequency,                # frequency (word)
                          modulation,               # modulation (byte)
                          dvb_c_t_t2_params,        # params (word)
                          0,                        # reserved (byte)
                          width,                    # bandwidth (byte)
                          0)                        # reserved (word)

        # compute and append crc to message
        crc = self.compute_crc(msg[1:])
        msg += struct.pack('B', crc)

        # send message to tuner
        self.write(msg)

        # read tuner answer
        buf = self.read(7)

        # return received data
        return buf

    def tuner_get_params(self):
        # construct message
        msg = struct.pack("=BBHB",
                          START_BYTE,
                          SOURCE,
                          2,
                          COD_COMAND_GET_PARAMS)

        # compute and append crc to message
        crc = self.compute_crc(msg[1:])
        msg += struct.pack('B', crc)

        # send message to tuner
        self.write(msg)

        # read tuner answer
        buf = self.read(15)

        data = []
        if len(buf) == 15:
            # start byte, address, length, command
            # status(1), reserved(1), modulation(1), dvb_c_t_t2_params(2)
            # reserved(4), crc(1)
            buf_list = struct.unpack("=BBHBBBBHIB", buf)
            if self.check_start_byte(buf_list[0]) is True:
                status = buf_list[4]
                modulation = buf_list[6]
                dvb_c_t_t2_params = buf_list[7]
                data = [status, modulation, dvb_c_t_t2_params]

        # return received data
        return data

    def tuner_get_measured_info(self):

        # construct message
        msg = struct.pack("=BBHB",
                          START_BYTE,
                          SOURCE,
                          2,
                          COD_COMAND_GET_MER_BER)

        # compute and append crc to message
        crc = self.compute_crc(msg[1:])
        msg += struct.pack('B', crc)

        # send message to tuner
        self.write(msg)

        # read tuner answer
        buf = self.read(17)

        def get_mantissa(data):
            return 1 + (data << 15)/(2**23)

        data = []
        if len(buf) == 17:
            # start byte, address, length, command
            # status, mer, ber1, ber2, ber3, reserved
            buf_list = struct.unpack("=BBHBBHBBBBBBHB", buf)

            # if first byte is start byte (little security check:)
            if self.check_start_byte(buf_list[0]) is True:
                status = buf_list[4]
                level_ok = bool(status & 0x1)
                lock_ok = bool(status & 0x2)

                # default values
                mer = 0
                mer_updated = False
                ber1 = 0
                ber1_updated = False
                ber2 = 0
                ber2_updated = False
                ber3 = 0
                ber3_updated = False

                # if signal is locked
                if (level_ok is True) and (lock_ok is True):
                    # set mer
                    mer_updated = not bool(status & 8)
                    mer = buf_list[5] / 10
                    # set ber1 if ber1 is not 0
                    ber1_updated = not(status & 16)
                    if buf_list[6] != 0 or buf_list[7] != 0:
                        ber1 = float(
                            get_mantissa(buf_list[6]) * 2**(buf_list[7]-127))
                    # set ber2 if ber2 is not 0
                    ber2_updated = not(status & 32)
                    if buf_list[8] != 0 or buf_list[9] != 0:
                        ber2 = float(
                            get_mantissa(buf_list[8]) * 2**(buf_list[9]-127))
                    # set ber3 if ber3 is not 0
                    ber3_updated = not(status & 64)
                    if buf_list[10] != 0 or buf_list[11] != 0:
                        ber3 = float(
                            get_mantissa(buf_list[10]) * 2**(buf_list[11]-127))

                # fill data list
                data = [mer, mer_updated,
                        ber1, ber1_updated,
                        ber2, ber2_updated,
                        ber3, ber3_updated]

        # return received data list
        return data

    def tuner_get_version_info(self):

        # construct message
        msg = struct.pack("=BBHBI",
                          START_BYTE,                   # start byte
                          SOURCE,                       # message source
                          6,                            # len
                          COD_COMAND_GET_VERSION_INFO,  # message code
                          0)                            # reserved

        # compute and append crc to message
        crc = self.compute_crc(msg[1:])
        msg += struct.pack('B', crc)

        # send message to tuner
        self.write(msg)

        # read tuner answer
        buf = self.read(30)

        # return received data
        return buf

    def tuner_reset(self):

        # construct message
        msg = struct.pack("=BBHBBH",
                          START_BYTE,               # start byte
                          SOURCE,                   # message source
                          5,                        # len
                          COD_COMAND_RESET,         # message code
                          1,                        # load main prog / loader
                          0)                        # reserved

        # compute and append crc to message
        crc = self.compute_crc(msg[1:])
        msg += struct.pack('B', crc)

        # send message to tuner
        self.write(msg)

        # read tuner answer
        buf = self.read(7)

        # return received data
        return buf

    # computes message crc
    def compute_crc(self, msg):
        crc = 0
        for byte in msg:
            crc ^= byte
        return crc

    # return list of available com ports (lightened code from stackoverflow)
    def serial_ports(self):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')

        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        return result

    def apply_settings(self, settings):
        thread = threading.Thread(
            target=self.tuner_set_params,
            args=(settings,))
        thread.start()


def read_from_port(rf_tuner):
    # read status
    if rf_tuner.is_opened is False:
        rf_tuner.connect_to_port()

    if rf_tuner.is_opened is True:

        status = rf_tuner.tuner_get_status()
        measured_data = rf_tuner.tuner_get_measured_info()
        params = rf_tuner.tuner_get_params()

    return [status, measured_data, params]

