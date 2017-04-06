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
        CustomMessages.NEW_TUNER_DEVINFO: (GObject.SIGNAL_RUN_FIRST,
                                           None, (bool, int, int, int, int, int)),
        CustomMessages.NEW_TUNER_MEAS: (GObject.SIGNAL_RUN_FIRST,
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
        self.new_settings = {}
        self.settings = settings.copy()

        self.serial_ports()

        self.tuner_idxs = set([])

        self.devinfo = {}
        self.meas = {}
        self.params = {}
        self.plp_list = {}

        self.emit_flags_lock = threading.Lock()
        self.new_devinfo = False
        self.new_meas = False
        self.new_params = False
        self.new_plp_list = False

        self.thread_active = True
        self.reading_thread = threading.Thread(target=self.read_from_port, args=())
        self.reading_thread.start()

        self.settings_changed = False
        self.settings_lock = threading.Lock()

        GObject.timeout_add(1000, self.on_pass_data)

    def flush(self):
        timeout = self.serial.timeout
        self.set_timeout(0)
        flush_buf = self.read(100000000)
        self.set_timeout(timeout)

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

    def set_timeout(self, t):
        try:
            self.serial.timeout = t
        except:
            return False
        else:
            return True

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
        status = {}
        # print(ports)
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
                self.set_timeout(TIME_RESPONSE_MSG)
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
                    status = self.get_devinfo()
                    if len(status) != 0:
                        return status
                else:
                    self.serial.close()

        return status

    def disconnect(self):
        self.serial.close()

    def check_start_tag(self, tag):
        return tag == ((UART_TAG_START_INV << 8) | UART_TAG_START)

    def read_rsp_ok(self):
        cnt = 0
        self.set_timeout(TIME_RESPONSE_OK)

        length = UART_RSP_LEN_OK + HEADER_LEN + TAIL_LEN
        buf = self.read(length)
        success = True
        while (len(buf) != length):
            if cnt == 2:
                success = False
                break
            cnt += 1
            buf = self.read(length)

        if success is True:
            buf_list = struct.unpack("=HBBBBB", buf)
            crc = self.compute_crc(buf_list[HEADER_LEN-1:-TAIL_LEN])
            if (self.check_start_tag(buf_list[0]) is False) or \
               (crc != buf_list[-TAIL_LEN]) or \
               (buf_list[2] != UART_TAG_OK) or \
               (buf_list[-1] != UART_TAG_STOP):
                success = False

        self.set_timeout(TIME_RESPONSE_MSG)
        return success

    def get_devinfo(self):
        self.flush()

        # construct message``
        msg = struct.pack("=BBBBB",
                          UART_TAG_START,
                          UART_TAG_START_INV,
                          UART_CMD_LEN_DEVINFO,
                          UART_TAG_DEVINFO,
                          0x00)
        # compute and append crc to message
        crc = self.compute_crc(msg[HEADER_LEN:])
        msg += struct.pack('B', crc)
        # append message_stop
        msg += struct.pack('B', UART_TAG_STOP)
        # send message to tuner
        n = self.write(msg)

        # read tuner answer
        data = {}
        if self.read_rsp_ok() is False:
            self.disconnect()
            return data

        length = UART_RSP_LEN_DEVINFO + HEADER_LEN + TAIL_LEN
        buf = self.read(length)
        if len(buf) == length:
            # [tag start, ~tag start], length, command,
            # serial num lsb, serial num msb, hw version,
            # fpga version, soft version, hardware cfg,
            # 0, 0, 0, 0, crc, tag stop
            buf_list = struct.unpack("=HBBBBBBBBBBBBBB", buf)
            crc = self.compute_crc(buf_list[HEADER_LEN-1:-TAIL_LEN])
            if self.check_start_tag(buf_list[0]) is True and \
               crc == buf_list[-TAIL_LEN] and \
               buf_list[2] == UART_TAG_DEVINFO and \
               buf_list[-1] == UART_TAG_STOP:
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

                data = {"connected": True, "serial": serial,
                        "hw_ver": hw_ver, "fpga_ver": fpga_ver,
                        "soft_ver": soft_ver, "hw_cfg": hw_cfg,
                        "tuner_idxs": indexes, "asi": asi}

        # return received data
        return data

    def set_settings(self, tuner_settings):
        self.flush()
        answ_dict = {}

        for k, slot_settings in tuner_settings.copy().items():
            if not k in self.tuner_idxs:
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
                              device + 1,                     # tuner mode
                              3 - width,                      # tuner bandwidth
                              0,
                              modulation,
                              frequency,
                              plp_id,
                              0)
            # compute and append crc to message
            crc = self.compute_crc(msg[HEADER_LEN:])
            msg += struct.pack('B', crc)
            # append message_stop
            msg += struct.pack('B', UART_TAG_STOP)
            # send message to tuner
            n = self.write(msg)

            # return tuner answer
            if self.read_rsp_ok() is False:
                self.disconnect()
                return answ_dict

            length = UART_RSP_LEN_TUNER_SET + HEADER_LEN + TAIL_LEN
            answer = self.read(length)
            if len(answer) == length:
                buf_list = struct.unpack("=HBBBBBBBBBBBBBB", answer)
                crc = self.compute_crc(buf_list[HEADER_LEN-1:-TAIL_LEN])
                if self.check_start_tag(buf_list[0]) is True and \
                   crc == buf_list[-TAIL_LEN] and \
                   (buf_list[2] & 0xf0) == UART_TAG_TUNER_SET and \
                   (buf_list[2] & 0x0f) == k and \
                   buf_list[-1] == UART_TAG_STOP:
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

                    answ_dict.update(dict([(k, data),]))
                    self.emit(CustomMessages.TUNER_SETTINGS_APPLIED,
                              int(k))

        return answ_dict

    def get_params(self):
        self.flush()

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
            crc = self.compute_crc(msg[HEADER_LEN:])
            msg += struct.pack('B', crc)
            # append message_stop
            msg += struct.pack('B', UART_TAG_STOP)
            # send request to tuner
            n = self.write(msg)

            # return tuner answer
            if self.read_rsp_ok() is False:
                self.disconnect()
                return answ_dict

            length = UART_RSP_LEN_PARAMS + HEADER_LEN + TAIL_LEN
            answer = self.read(length)
            if len(answer) == length:
                buf_list = struct.unpack("=H" + ((UART_RSP_LEN_PARAMS + 3)*'B'), answer)
                crc = self.compute_crc(buf_list[HEADER_LEN-1:-TAIL_LEN])
                if self.check_start_tag(buf_list[0]) is True and \
                   crc == buf_list[-TAIL_LEN] and \
                   (buf_list[2] & 0xf0) == UART_TAG_PARAMS and \
                   (buf_list[2] & 0x0f) == i and \
                   buf_list[-1] == UART_TAG_STOP:

                    data = {"void": None}

                    answ_dict.update(dict([(i, data),]))

        return answ_dict

    def get_meas(self):
        self.flush()

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
            crc = self.compute_crc(msg[HEADER_LEN:])
            msg += struct.pack('B', crc)
            # append message_stop
            msg += struct.pack('B', UART_TAG_STOP)
            # send request to tuner
            n = self.write(msg)

            # return tuner answer
            if self.read_rsp_ok() is False:
                self.disconnect()
                return answ_dict

            length = UART_RSP_LEN_MEAS + HEADER_LEN + TAIL_LEN
            answer = self.read(length)
            if len(answer) == length:
                buf_list = struct.unpack("=H" + ((UART_RSP_LEN_MEAS + 3)*'B'), answer)
                crc = self.compute_crc(buf_list[HEADER_LEN-1:-TAIL_LEN])
                if self.check_start_tag(buf_list[0]) is True and \
                   crc == buf_list[-TAIL_LEN] and \
                   (buf_list[2] & 0xf0) == UART_TAG_MEAS and \
                   (buf_list[2] & 0x0f) == i and \
                   buf_list[-1] == UART_TAG_STOP:
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

                    answ_dict.update(dict([(i, data),]))

        return answ_dict

    def get_plp_list(self):
        self.flush()

        answ_dict = {}
        for i in self.tuner_idxs:
            
            # construct message
            msg = struct.pack('=BBBBB',
                              UART_TAG_START,                 # message start
                              UART_TAG_START_INV,             # message start inverted
                              UART_CMD_LEN_PLP_LIST,          # tag length
                              UART_TAG_PLP_LIST | int(i),     # cmd setconf | tuner addr
                              0)
            # compute and append crc to message
            crc = self.compute_crc(msg[HEADER_LEN:])
            msg += struct.pack('B', crc)
            # append message_stop
            msg += struct.pack('B', UART_TAG_STOP)
            # send request to tuner
            n = self.write(msg)

            # return tuner answer
            if self.read_rsp_ok() is False:
                self.disconnect()
                return answ_dict

            header = self.read(HEADER_LEN)
            if len(header) != HEADER_LEN:
                continue
            header_buf = struct.unpack("=HB", header)
            if self.check_start_tag(header_buf[0]) is False:
                continue

            length = header_buf[1] + TAIL_LEN
            payload = self.read(length)
            if len(payload) == length:
                answer = header + payload
                buf_list = struct.unpack("=H" + (length+HEADER_LEN-2)*'B',
                                         answer)
                crc = self.compute_crc(buf_list[HEADER_LEN-1:-TAIL_LEN])
                if self.check_start_tag(buf_list[0]) is True and \
                   crc == buf_list[-TAIL_LEN] and \
                   (buf_list[2] & 0xf0) == UART_TAG_PLP_LIST and \
                   (buf_list[2] & 0x0f) == i and \
                   buf_list[-1] == UART_TAG_STOP and \
                   buf_list[4] == length - TAIL_LEN - 3:
                    # [tag start, tag start inv], length, tag|addr,
                    # lock, plp qty, plp_id[0], ... , plp_id[n],
                    # crc, tag stop

                    lock = (buf_list[3] == 0xff)
                    plp_qty = buf_list[4]
                    plps = []
                    for k in range(plp_qty):
                        plps.append(buf_list[5+k])

                    data = {"lock": lock, "plp_qty": plp_qty,
                            "plps": plps}
                    answ_dict.update(dict([(i, data),]))

        print(answ_dict)
        return answ_dict

    # computes message crc
    def compute_crc(self, msg):
        crc = 0
        for byte in msg:
            crc ^= byte
        return crc

    def apply_settings(self, settings):
        with self.settings_lock:
            self.new_settings = settings.copy()
            self.settings_changed = True

    def read_from_port(self):

        connected = False

        devinfo_prev_time = 0
        meas_prev_time = 0
        params_prev_time = 0
        plp_list_prev_time = 0

        cur_time = 0

        while self.thread_active:

            devinfo = {}
            meas = {}
            params = {}
            plp_list = {}
            # try to connect to tuner
            if self.serial.isOpen() is False:
                if connected is True:
                    connected = False
                    self.devinfo["connected"] = connected
                    with self.emit_flags_lock:
                        self.new_devinfo = True

                self.connect_to_port()
                # if opening port succeeded
                if self.serial.isOpen() is True:
                    time.sleep(1)
                    # apply tuners settings
                    set_answ = self.set_settings(self.settings)
                    # if failed applying settings, try apply again in a loop
                    cnt = 0
                    while (len(set_answ) == 0) and \
                          (self.thread_active is True):
                        if cnt > 1:
                            self.disconnect()
                            break
                        set_answ = self.set_settings(self.settings)
                        cnt += 1
                        time.sleep(1)
            else:
                if connected is False:
                    connected = True
                    self.devinfo["connected"] = connected
                    devinfo_prev_time = 0
                    meas_prev_time = 0
                    params_prev_time = 0
                    with self.emit_flags_lock:
                        self.new_devinfo = True

                # apply settings if necessary
                with self.settings_lock:
                    if self.settings_changed is True:
                        self.settings_changed = False
                        filtered_settings = {}

                        for new, old in zip(self.new_settings.items(),
                                            self.settings.items()):
                            if new[1] != old[1]:
                                filtered_settings.update({new[0]: new[1]})
                                self.set_settings(filtered_settings)

                        self.settings = self.new_settings
                        self.new_settings = {}

                cur_time = time.perf_counter()

                # get devinfo
                if devinfo_prev_time < (cur_time - TIME_GET_DEVINFO) or \
                   len(self.devinfo) == 0:
                    devinfo = self.get_devinfo()
                    devinfo["connected"] = connected
                    if self.devinfo != devinfo:
                        self.devinfo = devinfo
                        with self.emit_flags_lock:
                            self.new_devinfo = True

                    devinfo_prev_time = cur_time

                # get meas
                if meas_prev_time < (cur_time - TIME_GET_MEAS) or \
                   len(self.meas) == 0:
                    meas = self.get_meas()
                    if self.meas != meas:
                        self.meas = meas
                        with self.emit_flags_lock:
                            self.new_meas = True

                    meas_prev_time = cur_time

                if params_prev_time < (cur_time - TIME_GET_PARAMS) or \
                   len(self.params) == 0:
                    params = self.get_params()
                    if self.params != params:
                        self.params = params
                        with self.emit_flags_lock:
                            self.new_params = True

                    params_prev_time = cur_time

                if plp_list_prev_time < (cur_time - TIME_GET_PLP_LIST):
                    plp_list = self.get_plp_list()
                    if self.plp_list != plp_list:
                        self.plp_list = plp_list
                        with self.emit_flags_lock:
                            self.new_plp_list = True

                    plp_list_prev_time = cur_time

                time.sleep(0.5)

        return True

    def on_pass_data(self):
        with self.emit_flags_lock:
            if self.new_devinfo:
                self.emit_devinfo(self.devinfo)
                self.new_devinfo = False

            if self.new_meas:
                self.emit_meas(self.meas)
                self.new_meas = False

            if self.new_params:
                self.emit_params(self.params)
                self.new_params = False

        return True

    def emit_devinfo(self, devinfo):
        self.emit(CustomMessages.NEW_TUNER_DEVINFO,
                  devinfo.get("connected", False),
                  devinfo.get("serial", 0),
                  devinfo.get("hw_ver", 0),
                  devinfo.get("fpga_ver", 0),
                  devinfo.get("soft_ver", 0),
                  devinfo.get("hw_cfg", 0))

    def emit_meas(self, meas):
        for k,v in meas.items():
            self.emit(CustomMessages.NEW_TUNER_MEAS,
                      k,
                      v["lock"],
                      v["rf_power"],
                      v["mer"],
                      v["ber"],
                      v["freq"],
                      v["bitrate"])

    def emit_params(self, params):
        for k,v in params.items():
            pass

