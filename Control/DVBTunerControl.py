import serial
import sys
import glob
import struct
import threading
import time

from gi.repository import GObject

from Control import CustomMessages
from Control.DVBTunerConstants import DVBC, DVBT, DVBT2

# tags and commands
UART_TAG_START     = 0xAA
UART_TAG_START_INV = 0x55
UART_TAG_STOP      = 0xFE
UART_TAG_LENGTH    = 11
UART_CMD_DEVINFO   = 0x10
UART_CMD_SETTUNER  = 0x30
UART_CMD_MEASURE   = 0x40
UART_CMD_PARAMS    = 0x50
UART_CMD_MEASURE   = 0x60
UART_CMD_SETMUX    = 0x80
UART_CMD_GETMUX    = 0x90
UART_CMD_LENGTH    = 16


# class for dvb-t2 tuner management via com-port
class DVBTunerControl(GObject.GObject):

    __gsignals__ = {
        CustomMessages.NEW_TUNER_STATUS: (GObject.SIGNAL_RUN_FIRST,
                                          None, (int, int, int)),
        CustomMessages.NEW_TUNER_MEASURED_DATA: (GObject.SIGNAL_RUN_FIRST,
                                                 None,
                                                 (float, bool, float, bool,
                                                  float, bool, float, bool)),
        CustomMessages.NEW_TUNER_PARAMS: (GObject.SIGNAL_RUN_FIRST,
                                          None, (int, int, int)),
        CustomMessages.TUNER_SETTINGS_APPLIED: (GObject.SIGNAL_RUN_FIRST,
                                                None, (int,))}

    def __init__(self, settings):
        GObject.GObject.__init__(self)
        self.serial = serial.Serial()

        # remember user settings
        self.settings = settings

        self.serial_ports()

        self.status = []
        self.measured_data = []
        self.params = []

        self.thread_active = True
        thread = threading.Thread(target=self.read_from_port, args=())
        thread.start()

        GObject.timeout_add(1000, self.on_pass_data)

    def on_pass_data(self):
        if len(self.status) != 0:
            self.emit(CustomMessages.NEW_TUNER_STATUS,
                      self.status[0],            # status
                      self.status[1],            # hw errors
                      self.status[2])            # temperature

        if len(self.measured_data) != 0:
            self.emit(CustomMessages.NEW_TUNER_MEASURED_DATA,
                      self.measured_data[0],     # mer
                      self.measured_data[1],     # mer updated
                      self.measured_data[2],     # ber1
                      self.measured_data[3],     # ber1 updated
                      self.measured_data[4],     # ber2
                      self.measured_data[5],     # ber2 updated
                      self.measured_data[6],     # ber3
                      self.measured_data[7],)    # ber3 updated

        if len(self.params) != 0:
            self.emit(CustomMessages.NEW_TUNER_PARAMS,
                      self.params[0],            # status
                      self.params[1],            # modulation
                      self.params[2])            # params

        return True

    def read(self, size):
        if self.serial.isOpen() is True:
            try:
                return self.serial.read(size=size)
            except:
                self.serial.close()
                return b''
        return b''

    def write(self, msg):
        if self.serial.isOpen() is True:
            try:
                self.serial.write(msg)
            except:
                self.serial.close()

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

    def connect_to_port(self):
        found = False
        ports = self.serial_ports()
        for port in ports:
            # configure com port
            try:
                self.serial.baudrate = 115200
                self.serial.port = port
                self.serial.parity = serial.PARITY_NONE
                self.serial.bytesize = serial.EIGHTBITS
                self.serial.stopbits = serial.STOPBITS_ONE
                self.serial.timeout = 2
            except:
                self.serial.close()
                continue

            # open com port
            try:
                self.serial.open()
            # couldn't open port
            except serial.SerialException:
                self.serial.close()
                continue
            else:
                for i in range(3):
                   status = self.tuner_get_status()
                   # print("Status for port ", port, ": ",  status) 
                   if len(status) != 0:
                       found = True
                       self.serial.timeout = 10
                       break
                if found is True:
                    break
                else:
                    self.serial.close()

        return found

    def disconnect(self):
        self.serial.close()

    def check_start_byte(self, byte):
        return byte == UART_TAG_START

    def tuner_get_status(self):
        # construct message``
        msg = struct.pack("=BBBBBBBBBBBBBB",
                          UART_TAG_START,
                          UART_TAG_START_INV,
                          UART_TAG_LENGTH,
                          UART_CMD_DEVINFO,
                          0,0,0,0,0,0,0,0,0,0)

        # print("get status msg: ", msg.hex())

        # compute and append crc to message
        crc = self.compute_crc(msg[3:])
        msg += struct.pack('B', crc)

        # append message_stop
        msg += struct.pack('B', UART_TAG_STOP)

        # send message to tuner
        self.write(msg)
        # read tuner answer
        buf = self.read(UART_CMD_LENGTH)

        data = []
        if len(buf) == UART_CMD_LENGTH:
            # tag start, ~tag start, length, command,
            # 0, serial num lsb, serial num msb, hw version,
            # fpga version, soft version, hardware cfg, 0,
            # 0, 0, crc, tag stop
            buf_list = struct.unpack("=BBBBBBBBBBBBBBBB", buf)
            if self.check_start_byte(buf_list[0]) is True:
                hw_version = buf_list[7]
                hw_cfg = buf_list[10]
                data = [hw_version, hw_cfg]
                how_many_tuners = ((hw_cfg & 0x08) >> 3) + ((hw_cfg & 0x04) >> 2) +\
                                  ((hw_cfg & 0x02) >> 1) + (hw_cfg & 0x01)
                
        # return received data
        return data

    def tuner_set_params(self, tuner_settings):
        answ_dict = {}
        for k, slot_settings in tuner_settings.items():
            # get settings from received settings list.
            device = slot_settings['device']  #device means DVB standard: T2, T, C
            # if standard is DVB-T2
            if device == DVBT2:
                frequency = slot_settings['t2_freq']
                modulation = 0
                width = 0x20 | slot_settings['t2_bw']
                plp_id = slot_settings['t2_plp_id']
                # if standard is DVB-T
            elif device == DVBT:
                frequency = slot_settings['t_freq']
                modulation = 0
                width = 0x20 | slot_settings['t_bw']
                plp_id = 0
                # if standard is DVB-C
            elif device == DVBC:
                frequency = slot_settings['c_freq']
                modulation = 0 #modulation = slot_settings['c_mod']
                width = 0 #width = slot_settings['c_bw']
                plp_id = 0
                # if standard is unknown, return empty array
            else:
                continue
        
            # construct message
            msg = struct.pack('=BBBBBBBBIBB',
                              UART_TAG_START,                 # message start
                              UART_TAG_START_INV,             # message start inverted
                              UART_TAG_LENGTH,                # tag length
                              UART_CMD_SETTUNER | int(k),     # cmd setconf | tuner addr
                              device + 1,                     # tuner mode (1=T2, 2=T, 3=C)
                              width,                          # tuner bandwidth (T2/T: 0x20=6MHz, 0x21=7MHz, 0x22=8MHz) (C: 0=6MHz, 1=7MHz, 2=8MHz)
                              plp_id,                         # tuner PLP (0-255)
                              modulation,                     # tuner QAM in DVB-C mode
                              frequency,                      # tuner frq
                              0x00,
                              0x00)
            
            # compute and append crc to message
            crc = self.compute_crc(msg[3:])
            msg += struct.pack('B', crc)
            
            # append message_stop
            msg += struct.pack('B', UART_TAG_STOP)

            # print("set settings to tuner", k, msg.hex())
            # send message to tuner
            self.write(msg)
            # return tuner answer
            answer = self.read(UART_CMD_LENGTH)
            # print(k, "tuner answered", answer.hex())
            if len(answer) == UART_CMD_LENGTH:
                answ_dict.update(dict([(k, answer),]))
                self.emit(CustomMessages.TUNER_SETTINGS_APPLIED,
                          int(k))

        return answ_dict

    def tuner_get_params(self):
        # construct message
        msg = struct.pack("=BBHB",
                          START_BYTE, SOURCE, 2, COD_COMAND_GET_PARAMS)

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
                          START_BYTE, SOURCE, 2, COD_COMAND_GET_MER_BER)

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
                data = [mer, mer_updated, ber1, ber1_updated,
                        ber2, ber2_updated, ber3, ber3_updated]

        # return received data list
        return data

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
        # return tuner answer
        return self.read(7)

    # computes message crc
    def compute_crc(self, msg):
        crc = 0
        for byte in msg:
            crc ^= byte
        return crc

    def apply_settings(self, settings):
        filtered_settings = {}
        for new, old in zip(settings.items(), self.settings.items()):
            if new[1] != old[1]:
                filtered_settings.update(dict([(new[0], new[1])]))

        thread = threading.Thread(target=self.tuner_set_params,
                                  args=(filtered_settings,))
        thread.start()
        self.settings = settings

    def read_from_port(self):
        while True:
            # read status
            if self.serial.isOpen() is False:
                self.params = [0x8000, 0, 0]
                self.connect_to_port()

                # if opening port succeeded
                if self.serial.isOpen() is True:
                    time.sleep(1)

                    # apply tuners settings
                    set_answ = self.tuner_set_params(self.settings)
                    # if failed applying settings, try apply again in a loop
                    while (len(set_answ) == 0) and \
                          (self.thread_active is True):
                        set_answ = self.tuner_set_params(self.settings)
                        time.sleep(0.5)

            # read tuner status and params
            elif self.serial.isOpen() is True:
                pass
                # self.status = self.tuner_get_status()
                # self.measured_data = self.tuner_get_measured_info()
                # self.params = self.tuner_get_params()

            # if thread is no more needed, close
            if self.thread_active is False:
                return True

            # sleep for a second
            time.sleep(1)

