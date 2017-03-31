import serial
import sys
import glob
import struct
import threading
import time

from gi.repository import GObject

from Control import CustomMessages
from Control.DVBTunerConstants import *

# class for dvb-t2 tuner management via com-port
class DVBTunerControl(GObject.GObject):

    __gsignals__ = {
        CustomMessages.NEW_TUNER_STATUS: (GObject.SIGNAL_RUN_FIRST,
                                          None, (int, int, int)),
        CustomMessages.NEW_TUNER_MEASURED_DATA: (GObject.SIGNAL_RUN_FIRST,
                                                 None,
                                                 (int, bool, int, int,
                                                  int, int, int)),
        CustomMessages.NEW_TUNER_PARAMS: (GObject.SIGNAL_RUN_FIRST,
                                          None, (int, int, int)),
        CustomMessages.TUNER_SETTINGS_APPLIED: (GObject.SIGNAL_RUN_FIRST,
                                                None, (int,))}

    def __init__(self, settings):
        GObject.GObject.__init__(self)
        self.serial = serial.Serial()

        # remember user settings
        self.settings = settings.copy()

        self.serial_ports()

        self.tuner_idxs = []
        self.status = []
        self.measured_data = {}
        self.params = []

        self.thread_active = True
        self.reading_thread = threading.Thread(target=self.read_from_port, args=())
        self.reading_thread.start()

        self.writing_thread = None

    def on_pass_data(self):
        if len(self.status) != 0:
            self.emit(CustomMessages.NEW_TUNER_STATUS,
                      self.status[0],            # status
                      self.status[1],            # hw errors
                      self.status[2])            # temperature

        if len(self.measured_data) != 0:
            for k,v in self.measured_data.copy().items():
                self.emit(CustomMessages.NEW_TUNER_MEASURED_DATA,
                          k,
                          v["lock"],
                          v["rf_power"],
                          v["mer"],
                          v["ber"],
                          v["freq"],
                          v["bitrate"])

        if len(self.params) != 0:
            self.emit(CustomMessages.NEW_TUNER_PARAMS,
                      self.params[0],            # status
                      self.params[1],            # modulation
                      self.params[2])            # params

        return True

    def flush(self):
        timeout = self.serial.timeout
        self.serial.timeout = 0
        flush_buf = self.read(100000000)
        self.serial.timeout = timeout

    def read(self, size):
        if self.serial.isOpen() is True:
            try:
                return self.serial.read(size=size)
            except:
                # self.serial.close()
                return b''
        return b''

    def write(self, msg):
        n = 0
        if self.serial.isOpen() is True:
            try:
                n = self.serial.write(msg)
                self.serial.reset_input_buffer()
            except:
                pass
                # self.serial.close()
        return n

    def serial_ports(self):
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
        print(ports)
        for port in ports:
            if self.thread_active is False:
                break;
            # configure com port
            try:
                self.serial.baudrate = 115200
                self.serial.port = port
                self.serial.parity = serial.PARITY_NONE
                self.serial.bytesize = serial.EIGHTBITS
                self.serial.stopbits = serial.STOPBITS_ONE
                self.serial.xonxoff = False
                self.serial.dsrdtr = False
                self.serial.rtscts = False
                self.serial.timeout = TIME_RESPONSE_MSG
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
                    if self.thread_active is False:
                        break;
                    status = self.tuner_get_status()
                    if len(status) != 0:
                        found = True
                        break
                if found is True:
                    # print("port found", port)
                    break
                else:
                    self.serial.close()

        return found

    def disconnect(self):
        self.serial.close()

    def check_start_tag(self, tag):
        return tag == ((UART_TAG_START_INV << 8) | UART_TAG_START)

    def read_rsp_ok(self):
        cnt = 0
        self.serial.timeout = TIME_RESPONSE_OK

        buf = self.read(UART_RSP_LEN_OK + 5)
        success = True
        while (len(buf) != UART_RSP_LEN_OK + 5):
            if cnt == 2:
                success = False
                break
            cnt += 1
            buf = self.read(UART_RSP_LEN_OK + 5)

        if success is True:
            buf_list = struct.unpack("=HBBBBB", buf)
            if (self.check_start_tag(buf_list[0]) is False) or \
               (self.compute_crc(buf_list[2:-2]) != buf_list[-2]) or \
               (buf_list[2] != UART_TAG_OK):
                success = False

        self.serial.timeout = TIME_RESPONSE_MSG
        return success

    def tuner_get_status(self):
        self.flush()

        # construct message``
        msg = struct.pack("=BBBBB",
                          UART_TAG_START,
                          UART_TAG_START_INV,
                          UART_CMD_LEN_DEVINFO,
                          UART_TAG_DEVINFO,
                          0x00)

        # compute and append crc to message
        crc = self.compute_crc(msg[3:])
        msg += struct.pack('B', crc)

        # append message_stop
        msg += struct.pack('B', UART_TAG_STOP)

        # send message to tuner
        n = self.write(msg)

        print("CMD DEVINFO data written: ", msg.hex(), \
              "bytes in message: ", len(msg), \
              " bytes written: ", n)


        # read tuner answer
        data = {}

        if self.read_rsp_ok() is False:
            print("DEVINFO rsp ok failure", "\n")
            self.disconnect()
            return data

        buf = self.read(UART_RSP_LEN_DEVINFO + 5)
        if len(buf) == (UART_RSP_LEN_DEVINFO + 5):
            # [tag start, ~tag start], length, command,
            # serial num lsb, serial num msb, hw version,
            # fpga version, soft version, hardware cfg,
            # 0, 0, 0, 0, crc, tag stop
            buf_list = struct.unpack("=HBBBBBBBBBBBBBB", buf)
            print("RSP_DEVINFO: ", [hex(x) for x in buf_list])
            if self.check_start_tag(buf_list[0]) is True and \
               self.compute_crc(buf_list[2:-2]) == buf_list[-2] and \
               (buf_list[2] & 0xf0) == UART_TAG_DEVINFO:
                serial = (buf_list[4] << 8) | buf_list[3]
                hw_ver = buf_list[5]
                fpga_ver = buf_list[6]
                soft_ver = buf_list[7]
                hw_cfg = buf_list[8]
                asi = (hw_cfg & 9) > 0
                indexes = []
                for idx in range(4):
                    if (hw_cfg & (2**idx)) > 0:
                        indexes.append(idx)
                how_many_tuners = len(indexes)
                self.tuner_idxs = indexes

                data = {"serial": serial, "hw_ver": hw_ver,
                        "fpga_ver": fpga_ver, "soft_ver": soft_ver,
                        "tuner_idxs": indexes, "asi": asi}

                print("Received tuner status: ", data, "\n")
            else:
                print("RSP DEVINFO start or crc failure", "\n")
        else:
            print("RSP DEVINFO len failure", "\n")

        # return received data
        return data

    def tuner_set_settings(self, tuner_settings):
        self.flush()
        answ_dict = {}

        for k, slot_settings in tuner_settings.copy().items():
            if not k in self.tuner_idxs:
                print(k, " not in indexes. Indexes: ", self.tuner_idxs, "\n")
                continue
            
            # get settings from received settings list.
            device = slot_settings['device']  #device means DVB standard: T2, T, C
            # if standard is DVB-T2
            if device == DVBT2:
                frequency = slot_settings['t2_freq']
                modulation = 0
                width = slot_settings['t2_bw']
                plp_id = slot_settings['t2_plp_id']
                # if standard is DVB-T
            elif device == DVBT:
                frequency = slot_settings['t_freq']
                modulation = 0
                width = slot_settings['t_bw']
                plp_id = 0
                # if standard is DVB-C
            elif device == DVBC:
                frequency = slot_settings['c_freq']
                modulation = 0 #modulation = slot_settings['c_mod']
                width = 0 #width = slot_settings['c_bw']
                plp_id = 0
                # if standard is unknown, return empty array
            else:
                print("rf std err", "\n")
                continue
        
            # construct message
            msg = struct.pack('=BBBBBBBBIBB',
                              UART_TAG_START,                 # message start
                              UART_TAG_START_INV,             # message start inverted
                              UART_CMD_LEN_TUNER_SET,         # tag length
                              UART_TAG_TUNER_SET | int(k),    # cmd setconf | tuner addr
                              device + 1,                     # tuner mode (1=T2, 2=T, 3=C)
                              width,                          # tuner bandwidth
                              0,
                              modulation,
                              frequency,
                              plp_id,
                              0)
            
            # compute and append crc to message
            crc = self.compute_crc(msg[3:])
            msg += struct.pack('B', crc)
            
            # append message_stop
            msg += struct.pack('B', UART_TAG_STOP)

            # send message to tuner
            n = self.write(msg)
            print("CMD TUNER SET data written: ", msg.hex(), \
                  "bytes in message: ", len(msg), \
                  " bytes written: ", n)


            # return tuner answer
            if self.read_rsp_ok() is False:
                print("TUNER SET rsp ok failure", "\n")
                self.disconnect()
                return answ_dict

            answer = self.read(UART_RSP_LEN_TUNER_SET + 5)
            if len(answer) == UART_RSP_LEN_TUNER_SET + 5:
                buf_list = struct.unpack("=HBBBBBBBBBBBBBB", answer)
                if self.check_start_tag(buf_list[0]) is True and \
                   self.compute_crc(buf_list[2:-2]) == buf_list[-2] and \
                   (buf_list[2] & 0xf0) == UART_TAG_TUNER_SET:
                    # [tag start, tag start inv], length,
                    # tag|addr, mode, bw, hw present, dvbc qam,
                    # freq lsb, freq, freq, freq msb, lock, 0,
                    # crc, tag stop

                    data = {"addr": buf_list[2] & 0xf, "mode": buf_list[3],
                            "bw": buf_list[4], "hw_present": buf_list[5],
                            "dvbc_qam": buf_list[6],
                            "frequency": ((buf_list[10] << 24) |
                                          (buf_list[9] << 16) |
                                          (buf_list[8] << 8) |
                                          buf_list[7]),
                            "lock": buf_list[11]}

                    print("RSP TUNER SET: ", [hex(x) for x in buf_list])
                    print("Tuner ID=", k, " response after settings setup: ", data, "\n")

                    answ_dict.update(dict([(k, data),]))
                    self.emit(CustomMessages.TUNER_SETTINGS_APPLIED,
                              int(k))
                else:
                    print("RSP TUNER SET crc or start err or tag err", k,"\n")
            else:
                print("RSP TUNER SET len err", k, "\n")

        return answ_dict

    def tuner_get_params(self):
        answ_dict = {}
        for i in self.tuner_idxs:
            
            # construct message
            msg = struct.pack('=BBBBB',
                              UART_TAG_START,                 # message start
                              UART_TAG_START_INV,             # message start inverted
                              UART_CMD_LEN_PARAMS,            # tag length
                              UART_TAG_PARAMS | int(i),       # cmd setconf | tuner addr
                              0)
            
            # compute and append crc to message
            crc = self.compute_crc(msg[3:])
            msg += struct.pack('B', crc)
            
            # append message_stop
            msg += struct.pack('B', UART_TAG_STOP)

            # send request to tuner
            n = self.write(msg)
            # print("CMD PARAMS data written: ", msg.hex(), \
            #       "bytes in message: ", len(msg), \
            #       " bytes written: ", n)

            # return tuner answer
            if self.read_rsp_ok() is False:
                print("PARAMS rsp ok failure", "\n")
                self.disconnect()
                return answ_dict

            answer = self.read(UART_RSP_LEN_PARAMS + 5)
            if len(answer) == UART_RSP_LEN_PARAMS + 5:
                buf_list = struct.unpack("=H" + ((UART_RSP_LEN_PARAMS + 3)*'B'), answer)
                if self.check_start_tag(buf_list[0]) is True and \
                   self.compute_crc(buf_list[2:-2]) == buf_list[-2] and \
                   (buf_list[2] & 0xf0) == UART_TAG_PARAMS:
                    # print("RSP PARAMS: ", [hex(x) for x in buf_list], "\n")
                    pass

        return answ_dict

    def tuner_get_measured_info(self):

        answ_dict = {}
        for i in self.tuner_idxs:
            
            # construct message
            msg = struct.pack('=BBBBB',
                              UART_TAG_START,                 # message start
                              UART_TAG_START_INV,             # message start inverted
                              UART_CMD_LEN_MEAS,              # tag length
                              UART_TAG_MEAS | int(i),         # cmd setconf | tuner addr
                              0)
            
            # compute and append crc to message
            crc = self.compute_crc(msg[3:])
            msg += struct.pack('B', crc)
            
            # append message_stop
            msg += struct.pack('B', UART_TAG_STOP)

            # send request to tuner
            n = self.write(msg)
            # print("CMD MEAS data written: ", msg.hex(), \
            #       "bytes in message: ", len(msg), \
            #       "bytes written: ", n)

            # return tuner answer
            if self.read_rsp_ok() is False:
                print("MEAS rsp ok failure", "\n")
                self.disconnect()
                return answ_dict

            answer = self.read(UART_RSP_LEN_MEAS + 5)
            if len(answer) == UART_RSP_LEN_MEAS + 5:
                buf_list = struct.unpack("=H" + ((UART_RSP_LEN_MEAS + 3)*'B'), answer)
                if self.check_start_tag(buf_list[0]) is True and \
                   self.compute_crc(buf_list[2:-2]) == buf_list[-2] and \
                   (buf_list[2] & 0xf0) == UART_TAG_MEAS:
                    # [tag start, tag start inv], length, tag|addr,
                    # lock, rf power lsb, rf power msb,
                    # mer lsb, mer msb, ber lsb, ber, ber, ber msb,
                    # freq lsb, freq, freq, freq msb,
                    # br lsb, br, br, br msb, crc, tag stop

                    lock = (buf_list[3] == 0xff)
                    rf_power = struct.unpack("=H", bytearray(buf_list[4:6]))[0]
                    mer = struct.unpack("=H", bytearray(buf_list[6:8]))[0]
                    ber = struct.unpack("=I", bytearray(buf_list[8:12]))[0]
                    freq = struct.unpack("=I", bytearray(buf_list[12:16]))[0]
                    bitrate = struct.unpack("=I", bytearray(buf_list[16:20]))[0]

                    data = {"lock": lock, "rf_power": rf_power,
                            "mer": mer, "ber": ber,
                            "freq": freq, "bitrate":bitrate}

                    # print("RSP MEAS: ", [hex(x) for x in buf_list], "\n")
                    # print("Tuner ID=", i, "measured data:", data)

                    answ_dict.update(dict([(i, data),]))
                else:
                    print("RSP MEAS: start or crc or tag failure")
            else:
                print("RSP MEAS: length failure")

        return answ_dict

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
                filtered_settings.update({new[0]: new[1]})

        self.settings = settings.copy()

        self.writing_thread = threading.Thread(target=self.tuner_set_settings,
                                               args=(filtered_settings,))
        self.writing_thread.start()

    def read_from_port(self):
        while self.thread_active:
            # read status
            if self.serial.isOpen() is False:
                self.params = [0x8000, 0, 0]
                self.connect_to_port()

                # if opening port succeeded
                if self.serial.isOpen() is True:
                    time.sleep(1)

                    # apply tuners settings
                    set_answ = self.tuner_set_settings(self.settings)
                    # if failed applying settings, try apply again in a loop
                    cnt = 0
                    while (len(set_answ) == 0) and \
                          (self.thread_active is True):
                        if cnt > 1:
                            self.disconnect()
                            break;
                        set_answ = self.tuner_set_settings(self.settings)
                        cnt += 1
                        time.sleep(1)

            # read tuner status and params
            elif self.serial.isOpen() is True:
                pass
                # self.status = self.tuner_get_status()
                self.measured_data = self.tuner_get_measured_info()
                self.params = self.tuner_get_params()
                self.on_pass_data()

            # sleep for a second
            time.sleep(1)

        return True

