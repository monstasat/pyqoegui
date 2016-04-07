from Control.ErrorDetector.ErrorCounter import ErrorCounter
from Control.ErrorDetector.StatusTypes import STYPES

class ErrorDetector():

    def __init__(self, video_data_header, audio_data_header):

        self.vdata_hdr = video_data_header
        self.adata_hdr = audio_data_header

        # loss counters
        self.vloss_cnt = 0
        self.aloss_cnt = 0

        self.vloss_thrsh = 0
        self.aloss_thrsh = 0

        self.verr_cnts = {'black': ErrorCounter(),
                          'freeze': ErrorCounter(),
                          'blocky': ErrorCounter()}
        self.aerr_cnts = {'silence': ErrorCounter(),
                          'loudness': ErrorCounter()}

        self.verr_flgs = {'vloss': False, 'black': False,
                          'freeze': False, 'blocky': False}
        self.aerr_flgs = {'aloss': False, 'silence': False,
                          'loudness': False}

    def eval_video(self, bufs):
        for k, v in self.verr_cnts.items():
            if k == 'black':
                v.eval((bufs[0], bufs[3]))
            elif k == 'freeze':
                v.eval((bufs[1], bufs[4]))
            elif k == 'blocky':
                v.eval(bufs[2])

    def eval_audio(self, bufs):
        for k, v in self.aerr_cnts.items():
            if k == 'silence':
                v.eval(bufs[1])
            elif k == 'loudness':
                v.eval(bufs[1])

    def get_errors(self):
        aloss_flag = False
        vloss_flag = False

        self.verr_flgs['vloss'] = STYPES['norm']
        self.aerr_flgs['aloss'] = STYPES['norm']

        for k, v in self.verr_cnts.items():
            loss_flag, error = v.get_error()
            self.verr_flgs[k] = error
            vloss_flag = loss_flag

        for k, v in self.aerr_cnts.items():
            loss_flag, error = v.get_error()
            self.aerr_flgs[k] = error
            aloss_flag = loss_flag

        if aloss_flag is True:
            self.aloss_cnt += 1
            if self.aloss_cnt >= self.aloss_thrsh:
                self.aerr_flgs['aloss'] = STYPES['err']
        else:
            self.aloss_cnt = 0

        if vloss_flag is True:
            self.vloss_cnt += 1
            if self.vloss_cnt >= self.vloss_thrsh:
                self.verr_flgs['vloss'] = STYPES['err']
        else:
            self.vloss_cnt = 0

        return ((self.vdata_hdr, self.verr_flgs),
                (self.adata_hdr, self.aerr_flgs))

