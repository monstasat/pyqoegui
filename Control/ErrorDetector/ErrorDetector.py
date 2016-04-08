from Control.ErrorDetector.ProgramStats import ProgramStats

class ErrorDetector():
    def __init__(self, prog_list, analysis_settings):
        print(analysis_settings)

        # create error detectors
        self.error_detectors = []
        self.set_prog_list(prog_list)

        # set analysis settings
        self.analysis_settings = analysis_settings
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
                error_detectors.append(ProgramStats(video_data_header,
                                                    audio_data_header))

        return error_detectors

    def set_prog_list(self, prog_list):
        list(map((lambda x: x.__destroy__()), self.error_detectors))
        self.error_detectors.clear()
        self.error_detectors = self.create_error_detectors(prog_list)

    def set_analysis_settings(self, analysis_settings):

        for dt in self.error_detectors:
            dt.vloss_thrsh = analysis_settings['vloss']
            dt.aloss_thrsh = analysis_settings['aloss']

            # FIXME: rewrite
            for k, v in dt.verr_cnts.items():
                if k == 'black':
                    black_cont = float(analysis_settings[k + '_cont'])
                    black_peak = float(analysis_settings[k + '_peak'])
                    luma_cont = int(analysis_settings['luma_cont'])
                    luma_peak = int(analysis_settings['luma_peak'])
                    v.cont_predicate = lambda x: (x[0] >= black_cont) or \
                                                 (x[1] <= luma_cont)
                    v.peak_predicate = lambda x: (x[0] >= black_peak) or \
                                                 (x[1] <= luma_peak)
                    v.time = int(analysis_settings[k + '_time'])
                elif k == 'freeze':
                    freeze_cont = float(analysis_settings[k + '_cont'])
                    freeze_peak = float(analysis_settings[k + '_peak'])
                    diff_cont = float(analysis_settings['diff_cont'])
                    diff_peak = float(analysis_settings['diff_peak'])
                    v.cont_predicate = lambda x: (x[0] >= freeze_cont) or \
                                                 (x[1] <= diff_cont)
                    v.peak_predicate = lambda x: (x[0] >= freeze_peak) or \
                                                 (x[1] <= diff_peak)
                    v.time = int(analysis_settings[k + '_time'])
                elif k == 'blocky':
                    blocky_cont = float(analysis_settings[k + '_cont'])
                    blocky_peak = float(analysis_settings[k + '_peak'])
                    v.cont_predicate = lambda x: x >= blocky_cont
                    v.peak_predicate = lambda x: x >= blocky_peak
                    v.time = int(analysis_settings[k + '_time'])

            for k, v in dt.aerr_cnts.items():
                if k == 'silence':
                    silence_cont = float(analysis_settings[k + '_cont'])
                    silence_peak = float(analysis_settings[k + '_peak'])
                    v.cont_predicate = lambda x: x <= silence_cont
                    v.peak_predicate = lambda x: x <= silence_peak
                    v.time = int(analysis_settings[k + '_time'])
                elif k == 'loudness':
                    loudness_cont = float(analysis_settings[k + '_cont'])
                    loudness_peak = float(analysis_settings[k + '_peak'])
                    v.cont_predicate = lambda x: x >= loudness_cont
                    v.peak_predicate = lambda x: x >= loudness_peak
                    v.time = int(analysis_settings[k + '_time'])

    def eval_video(self, data):
        # get error detectors with specified data header
        detectors = list(filter(lambda x: x.vdata_hdr == data[0],
                         self.error_detectors))

        # push data to corresponding error detector
        list(map(lambda x: x.eval_video(data[1]), detectors))

    def eval_audio(self, data):
        # get error detectors with specified data header
        detectors = list(filter(lambda x: x.adata_hdr == data[0],
                         self.error_detectors))

        # push data to corresponding error detector
        list(map(lambda x: x.eval_audio(data[1]), detectors))

    def get_errors(self):
        err_list = []
        for detector in self.error_detectors:
            err_list.append(detector.get_errors())

        return err_list

