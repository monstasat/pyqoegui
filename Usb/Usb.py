from gi.repository import GObject

from BaseInterface import BaseInterface
from Usb.UsbExchange import UsbExchange


class Usb(BaseInterface):

    def __init__(self,
                 analyzed_progs_list,
                 analysis_settings_list,
                 tuner_settings_list):

        BaseInterface.__init__(self,
                               analyzed_progs_list,
                               analysis_settings_list,
                               tuner_settings_list)

        GObject.timeout_add(1000, self.send_messages)

        #self.exchange = UsbExchange()

    def send_messages(self):
        print("sending message")
        return True

