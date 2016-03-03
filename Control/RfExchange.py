import serial
import sys
import glob
import struct

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
class RfExchange():
    def __init__(self):
        self.serial = serial.Serial()
        self.connect()

    def connect(self):
        self.serial.baudrate = 115200
        self.serial.port = '/dev/ttyUSB0'
        self.serial.parity = serial.PARITY_NONE
        self.serial.bytesize = serial.EIGHTBITS
        self.serial.stopbits = serial.STOPBITS_ONE
        self.serial.timeout = 2
        #self.serial.open()
        print("serial ports: ", self.serial_ports())
        self.tuner_set_params()
        #self.tuner_get_status()

    def tuner_get_status(self):

        self.serial.open()

        msg = struct.pack("=BBHB",
                          START_BYTE,
                          SOURCE,
                          2,
                          COD_COMAND_GET_STATUS)

        crc = self.compute_crc(msg[1:])
        msg += struct.pack('B', crc)

        self.serial.write(msg)

        buf = self.serial.read(size=20)
        print("tuner returned: ", buf, "len: ", len(buf))

        self.serial.close()

    def tuner_set_params(self):
        # open com port
        self.serial.open()

        # [15:3] - reserved, [12:10] - khz, [9:0] - mhz
        frequency = 586
        # 0 - unknown
        # 3 - DVB-C/QAM64
        # 4 - DVB-C/QAM128
        # 5 - DVB-C/QAM256
        # 6 - DVB-T/QPSK
        # 7 - DVB-T/QAM16
        # 8 - DVB-T/QAM64
        # 9 - DVB-T2
        modulation = 9
        #for dvb-c:
        #dvb_c_t_t2_params[15..0]       sr: symbol rate in KSps (5000..7000)
        #for dvb-t:
        # dvb_c_t_t2_params[15..14]     fft: 0 - 2K, 1 - 8K
        # dvb_c_t_t2_params[13..12]     gui: 0 - 1/32, 1 - 1/16, 2 - 1/8, 3 - 1/4
        # dvb_c_t_t2_params[11..10]     hierarch: 0 - w/out, 1 - a = 1, 2 - a = 2, 3 - a = 4
        # dvb_c_t_t2_params[9]          spectrum: 0 - straight, 1 - iverted
        # dvb_c_t_t2_params[8:6]        fec_lp: 0 - 1/2, 1 - 2/3, 2 - 3/4, 3 - 5/6, 4 - 7/8
        # dvb_c_t_t2_params[5:3]        fec_hp: 0 - 1/2, 1 - 2/3, 2 - 3/4, 3 - 5/6, 4 - 7/8
        # dvb_c_t_t2_params[2:1]        bw: 0 - 6 MHz, 1 - 7 MHz, 2 - 8 MHz
        # dvb_c_t_t2_params[0]          reserved
        # for dvb-t2
        # dvb_c_t_t2_params[15:8]       plp_id
        # dvb_c_t_t2_params[7:4]        qam_id: 0 - QPSK, 1 - QAM16, 2 - QAM64, 3 - QAM256
        # dvb_c_t_t2_params[3:2]        reserved
        # dvb_c_t_t2_params[1:0]        bw: 0 - 6 MHz, 1 - 7 MHz, 2 - 8 MHz
        dvb_c_t_t2_params = 2
        # 0 - 6 mhz, 1 - 7 mhz, 2 - 8 mhz
        width = 2

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

        crc = self.compute_crc(msg[1:])
        msg += struct.pack('B', crc)

        self.serial.write(msg)

        buf = self.serial.read(size=7)
        print("tuner returned: ", buf, "len: ", len(buf))

        # close com port
        self.serial.close()

    # computes message crc
    def compute_crc(self, msg):
        crc = 0;
        for byte in msg:
            crc ^= byte;
        return crc

    def serial_ports(self):
        """ Lists serial port names

            :raises EnvironmentError:
                On unsupported or unknown platforms
            :returns:
                A list of the serial ports available on the system
        """
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
