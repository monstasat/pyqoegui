import serial


# class for dvb-t2 tuner management via com-port
class RfExchange():
    def __init__(self):
        self.serial = serial.Serial()

    def connect(self):
        self.serial.baudrate = 19200
        self.serial.port = 'COM1'
