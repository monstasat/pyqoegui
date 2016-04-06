from Control.ErrorDetector.ErrorDetector import ErrorDetector

class ErrorDetectorControl():
    def __init__(self, prog_list, analysis_settings):

        # create error detectors
        self.error_detectors = []
        self.set_prog_list(prog_list)

        self.set_analysis_settings(analysis_settings)

    def create_error_detectors(self, prog_list):
        error_detectors = []
        # create error detectors
        for stream in prog_list:
            for prog in stream[1]:
                stream_id = int(stream[0])
                prog_id = int(prog[0])
                audio_data_header = [stream_id, prog_id, None]
                video_data_header = [stream_id, prog_id, None]
                for pid in prog[4]:
                    pid_type = pid[2].split('-')[0]
                    if pid_type == 'audio':
                        audio_data_header[2] = int(pid[0])
                    elif pid_type == 'video':
                        video_data_header[2] = int(pid[0])

                # append error detector for program
                error_detectors.append(ErrorDetector(video_data_header,
                                                     audio_data_header,
                                                     analysis_settings))

        return error_detectors

    def set_prog_list(self, prog_list):
        list(map((lambda x: x.__destroy__()), self.error_detectors))
        self.error_detectors.clear()
        self.error_detectors = self.create_error_detectors(prog_list)

    def set_analysis_settings(self, analysis_settings):
        list(map((lambda x: x.set_analysis_settings(analysis_settings)),
                 self.error_detectors))

    def parse_data(self, data, data_type):
        # get error detectors with specified data header
        detectors = list(filter(
            lambda x: getattr(x, data_type + '_data_header') == data[0],
            self.error_detectors))

        # push data to corresponding error detectors
        list(map(lambda x: getattr(x, 'fill_' + data_type + '_data')(data[1]),
                 detectors))

    def get_errors(self):
        err_list = []
        for detector in self.error_detectors:
            err_list.append(detector.get_errors())

        return err_list



