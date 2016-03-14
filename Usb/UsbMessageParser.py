from collections import deque

from Usb import UsbMessageTypes as usb_msgs


class UsbMessageParser():

    def __init__(self):
        # create parser buffer
        self.buffer = deque()
        # create message buffer
        self.message_buffer = []
        # create queue state
        self.queue_state = 0

    def extend(self, data):
        '''
        Extends parser buffer by 'data' bytes, received from remote client
        '''
        self.buffer.extend(data)

    def parse_queue(self):
        '''
        Method for parsing input usb queue
        '''
        messages = []

        # get word from queue
        while len(self.buffer) != 0:

            word = self.buffer.popleft()

            if word == usb_msgs.PREFIX:
                # if message buffer is not empty, parse it
                if len(self.message_buffer) > 0:
                    res = self.parse_message(self.message_buffer)
                    messages.append(res)

                # clear previous message
                self.message_buffer.clear()

                # push new prefix to message buffer
                self.message_buffer.append(word)

            else:
                self.message_buffer.append(word)

        return messages

    def parse_message(self, buf):
        msg_code = buf[1]
        msg_data = buf[2:]
        return [msg_code, msg_data]

