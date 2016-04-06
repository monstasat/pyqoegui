from Control.ErrorDetector.ErrorCounter import ErrorCounter

class ErrorDetector():

    def __init__(self, video_data_header, audio_data_header):

        self.video_data_header = video_data_header
        self.audio_data_header = audio_data_header

        # loss counters
        self.video_loss_cnt = 0
        self.audio_loss_cnt = 0

        self.vloss_thrsh = 0
        self.aloss_thrsh = 0

        self.video_errs = {'black': ErrorCounter(), 'freeze': ErrorCounter(),
                           'blocky': ErrorCounter()}
        self.audio_errs = {'silence': ErrorCounter(),
                           'loudness': ErrorCounter()}

        self.err_flags = {'vloss': False, 'black': False, 'freeze': False,
                          'blocky': False, 'aloss': False, 'silence': False,
                          'loudness': False}

    def eval_video(self, bufs):
        for k, v in self.video_errs.items():
            if k == 'black':
                v.eval((bufs[0], bufs[3]))
            elif k == 'freeze':
                v.eval((bufs[1], bufs[4]))
            elif k == 'blocky':
                v.eval(bufs[2])

    def eval_audio(self, bufs):
        for k, v in self.audio_errs.items():
            if k == 'silence':
                v.eval(bufs[1])
            elif k == 'loudness':
                v.eval(bufs[1])

    def get_errors(self):
        aloss_flag = False
        vloss_flag = False

        self.err_flags['aloss'] = False
        self.err_flags['vloss'] = False

        for k, v in self.video_errs.items():
            loss_flag, error = v.get_error()
            self.err_flags[k] = error
            vloss_flag = loss_flag

        for k, v in self.audio_errs.items():
            loss_flag, error = v.get_error()
            self.err_flags[k] = error
            aloss_flag = loss_flag

        if aloss_flag is True:
            self.audio_loss_cnt += 1
            if self.audio_loss_cnt >= self.aloss_thrsh:
                self.err_flags['aloss'] = True
        else:
            self.audio_loss_cnt = 0

        if vloss_flag is True:
            self.video_loss_cnt += 1
            if self.video_loss_cnt >= self.vloss_thrsh:
                self.err_flags['vloss'] = True
        else:
            self.video_loss_cnt = 0

        return (self.video_data_header, self.audio_data_header, self.err_flags)

