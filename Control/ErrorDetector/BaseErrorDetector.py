from gi.repository import GObject

from Control.ErrorDetector.VideoDataStorage import VideoDataStorage
from Control.ErrorDetector.AudioDataStorage import AudioDataStorage
from Control.ErrorDetector import StatusTypes as types


class BaseErrorDetector(GObject.GObject):
    def __init__(self,
                 prog_list,
                 detector_type):

        # detector type: audio/video
        self.type = detector_type

        # set list of measured data headers and buffers for storing data
        self.valid_headers = []
        self.buffers = []
        # fill valid headers and
        self.set_programs_list(prog_list)

        # buffers for storing data
        self.deque_num = 5 if (self.type is 'video') else 2

        # data loss counter
        self.loss_cnt = 0

    def set_data(self, vparams):
        try:
            index = self.valid_headers.index(vparams[0])
            buf = self.buffers[index][1]
        except:
            pass
        else:
            for i, param in enumerate(vparams[1]):
                try:
                    buf[i] = param
                except:
                    print("error while pushing data")

    def set_programs_list(self, prog_list):

        self.valid_headers.clear()
        self.buffers.clear()

        # get list of measured data headers
        for stream in prog_list:
            stream_id = stream[0]
            for prog in stream[1]:
                hdr = []
                prog_id = prog[0]
                hdr.append(int(stream_id))
                hdr.append(int(prog_id))
                for pid in prog[4]:
                    pid_type = pid[2].split('-')[0]
                    if pid_type == self.type:
                        hdr.append(int(pid[0]))
                        self.valid_headers.append(hdr)
                        # one instance of buffer contains deques
                        # for measured parameters
                            # video: [black num, freeze num,
                            # blocky level, av luma, av diff]
                            # audio : [momentary loudness,
                            # short term loudness]
                        self.buffers.append([hdr, [deque()]*self.deque_num])

