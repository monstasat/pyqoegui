from gi.repository import GObject

from Control.ErrorDetector.VideoDataStorage import VideoDataStorage
from Control.ErrorDetector.AudioDataStorage import AudioDataStorage
from Control import ErrorTypesModel as em
from Control.ErrorDetector import StatusTypes as types


class BaseErrorDetector(GObject.GObject):
    def __init__(self,
                 prog_list,
                 detector_type):

        # detector type: audio/video
        self.type = detector_type

        # list of measured data headers
        self.valid_headers = []
        # list of value storages
        self.storage_list = []

        self.set_programs_list(prog_list)

    def set_data(self, vparams):
        try:
            index = self.valid_headers.index(vparams[0])
        except:
            pass
        else:
            storage = self.storage_list[index]
            storage.push_new_data(vparams[1])

    def set_programs_list(self, prog_list):

        self.valid_headers.clear()
        self.storage_list.clear()

        # get list of measured data headers for video
        for stream in prog_list:
            stream_id = stream[0]
            for prog in stream[1]:
                data_header = []
                prog_id = prog[0]
                data_header.append(int(stream_id))
                data_header.append(int(prog_id))
                for pid in prog[4]:
                    pid_type = pid[2].split('-')[0]
                    if pid_type == self.type:
                        data_header.append(int(pid[0]))
                        self.valid_headers.append(data_header)

        for prog in self.valid_headers:
            if self.type == 'video':
                self.storage_list.append(VideoDataStorage(prog))
            else:
                self.storage_list.append(AudioDataStorage(prog))

