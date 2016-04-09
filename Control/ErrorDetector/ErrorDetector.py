from Control.ErrorDetector.ProgramStats import ProgramStats

class ErrorDetector():
    def __init__(self, prog_list, analysis_settings):

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
                audio_data_header = [stream_id, prog_id, 0]
                video_data_header = [stream_id, prog_id, 0]
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
        self.error_detectors.clear()
        self.error_detectors = self.create_error_detectors(prog_list)

    def set_analysis_settings(self, analysis_settings):

        for dt in self.error_detectors:
            # loss thresholds
            dt.vloss_thrsh = analysis_settings['vloss']
            dt.aloss_thrsh = analysis_settings['aloss']

            # predicates for error detection
            # black frame
            if analysis_settings['black_cont_en'] is True:
                black_cont_predicate = lambda x: \
                    (x[0] >= float(analysis_settings['black_cont'])) or \
                    (x[1] <= float(analysis_settings['luma_cont']))
            else:
                black_cont_predicate = lambda x: False
            if analysis_settings['black_peak_en'] is True:
                black_peak_predicate = lambda x: \
                    (x[0] >= float(analysis_settings['black_peak'])) or \
                    (x[1] <= float(analysis_settings['luma_peak']))
            else:
                black_peak_predicate = lambda x: False

            # freeze frame
            if analysis_settings['freeze_cont_en'] is True:
                freeze_cont_predicate = lambda x: \
                    (x[0] >= float(analysis_settings['freeze_cont'])) or \
                    (x[1] <= float(analysis_settings['diff_cont']))
            else:
                freeze_cont_predicate = lambda x: False
            if analysis_settings['freeze_peak_en'] is True:
                freeze_peak_predicate = lambda x: \
                    (x[0] >= float(analysis_settings['freeze_peak'])) or \
                    (x[1] <= float(analysis_settings['diff_peak']))
            else:
                freeze_peak_predicate = lambda x: False

            # blockiness
            if analysis_settings['blocky_cont_en'] is True:
                blocky_cont_predicate = lambda x: \
                    x >= float(analysis_settings['blocky_cont'])
            else:
                blocky_cont_predicate = lambda x: False
            if analysis_settings['blocky_peak_en'] is True:
                blocky_peak_predicate = lambda x: \
                    x >= float(analysis_settings['blocky_peak'])
            else:
                blocky_peak_predicate = lambda x: False

            # silence
            if analysis_settings['silence_cont_en'] is True:
                silence_cont_predicate = lambda x: \
                    x <= float(analysis_settings['silence_cont'])
            else:
                silence_cont_predicate = lambda x: False
            if analysis_settings['silence_peak_en'] is True:
                silence_peak_predicate = lambda x: \
                    x <= float(analysis_settings['silence_peak'])
            else:
                silence_peak_predicate = lambda x: False

            # loudness
            if analysis_settings['loudness_cont_en'] is True:
                loudness_cont_predicate = lambda x: \
                    x >= float(analysis_settings['loudness_cont'])
            else:
                loudness_cont_predicate = lambda x: False
            if analysis_settings['loudness_peak_en'] is True:
                loudness_peak_predicate = lambda x: \
                    x >= float(analysis_settings['loudness_peak'])
            else:
                loudness_peak_predicate = lambda x: False

            # apply predicates
            for k, v in dt.verr_cnts.items():
                v.time = int(analysis_settings[k + '_time'])
                if k == 'black':
                    v.cont_predicate = black_cont_predicate
                    v.peak_predicate = black_peak_predicate
                elif k == 'freeze':
                    v.cont_predicate = freeze_cont_predicate
                    v.peak_predicate = freeze_peak_predicate
                elif k == 'blocky':
                    v.cont_predicate = blocky_cont_predicate
                    v.peak_predicate = blocky_peak_predicate

            for k, v in dt.aerr_cnts.items():
                v.time = int(analysis_settings[k + '_time'])
                if k == 'silence':
                    v.cont_predicate = silence_cont_predicate
                    v.peak_predicate = silence_peak_predicate
                elif k == 'loudness':
                    v.cont_predicate = loudness_cont_predicate
                    v.peak_predicate = loudness_peak_predicate

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
        list(map(lambda x: err_list.append(x.get_errors()),
                 self.error_detectors))

        return err_list

