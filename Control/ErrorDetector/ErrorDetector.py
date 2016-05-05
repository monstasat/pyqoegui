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

    def set_analysis_settings(self, aset):
        # predicates for error detection
        # black frame
        fun1 = fun2 = lambda x: False
        if aset['black_cont_en'] is True:
            fun1 = lambda x: (x >= float(aset['black_cont']))
        if aset['luma_cont_en'] is True:
            fun2 = lambda x: (x <= float(aset['luma_cont']))
        black_cont_predicate = lambda x: fun1(x[0]) or fun2(x[1])

        fun1 = fun2 = lambda x: False
        if aset['black_peak_en'] is True:
            fun1 = lambda x: (x >= float(aset['black_peak']))
        if aset['luma_peak_en'] is True:
            fun2 = lambda x: (x <= float(aset['luma_peak']))
        black_peak_predicate = lambda x: fun1(x[0]) or fun2(x[1])

        # freeze frame
        fun1 = fun2 = lambda x: False
        if aset['freeze_cont_en'] is True:
            fun1 = lambda x: (x >= float(aset['freeze_cont']))
        if aset['diff_cont_en'] is True:
            fun2 = lambda x: (x <= float(aset['diff_cont']))
        freeze_cont_predicate = lambda x: fun1(x[0]) or fun2(x[1])

        fun1 = fun2 = lambda x: False
        if aset['freeze_peak_en'] is True:
            fun1 = lambda x: (x >= float(aset['freeze_peak']))
        if aset['diff_peak_en'] is True:
            fun2 = lambda x: (x <= float(aset['diff_peak']))
        freeze_peak_predicate = lambda x: fun1(x[0]) or fun2(x[1])

        # blockiness
        block_cont_pr = lambda x: False
        if aset['blocky_cont_en'] is True:
            block_cont_pr = lambda x: x >= float(aset['blocky_cont'])

        block_peak_pr = lambda x: False
        if aset['blocky_peak_en'] is True:
            block_peak_pr = lambda x: x >= float(aset['blocky_peak'])

        # silence
        sil_cont_pr = lambda x: False
        if aset['silence_cont_en'] is True:
            sil_cont_pr = lambda x: x <= float(aset['silence_cont'])

        sil_peak_pr = lambda x: False
        if aset['silence_peak_en'] is True:
            sil_peak_pr = lambda x: x <= float(aset['silence_peak'])

        # loudness
        loud_cont_pr = lambda x: False
        if aset['loudness_cont_en'] is True:
            loud_cont_pr = lambda x: x >= float(aset['loudness_cont'])

        loud_peak_pr = lambda x: False
        if aset['loudness_peak_en'] is True:
            loud_peak_pr = lambda x: x >= float(aset['loudness_peak'])

        for dt in self.error_detectors:
            # loss thresholds
            dt.vloss_thrsh = aset['vloss']
            dt.aloss_thrsh = aset['aloss']

            # apply predicates
            for k, v in dt.verr_cnts.items():
                v.time = int(aset[k + '_time'])
                if k == 'black':
                    v.cont_predicate = black_cont_predicate
                    v.peak_predicate = black_peak_predicate
                elif k == 'freeze':
                    v.cont_predicate = freeze_cont_predicate
                    v.peak_predicate = freeze_peak_predicate
                elif k == 'blocky':
                    v.cont_predicate = block_cont_pr
                    v.peak_predicate = block_peak_pr

            for k, v in dt.aerr_cnts.items():
                v.time = int(aset[k + '_time'])
                if k == 'silence':
                    v.cont_predicate = sil_cont_pr
                    v.peak_predicate = sil_peak_pr
                elif k == 'loudness':
                    v.cont_predicate = loud_cont_pr
                    v.peak_predicate = loud_peak_pr

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

