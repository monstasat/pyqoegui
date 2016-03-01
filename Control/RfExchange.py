import serial
import sys
import glob

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
        #self.serial.open()
        print("serial ports: ", self.serial_ports())

    def tuner_set_params(self):
        self.serial.open()
        param_msg = []

        # message start byte
        param_msg.append(START_BYTE)
        # message source
        param_msg.append(SOURCE)
        # message cod command
        param_msg.append(COD_COMAND_SET_PARAMS)
        # message length
        params_msg.append(10)
        # frequency
        params_msg.append(586)

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
