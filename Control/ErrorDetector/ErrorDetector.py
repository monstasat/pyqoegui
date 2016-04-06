from Control.ErrorDetector.ErrorCounter import ErrorCounter

class ErrorDetector():

    def __init__(self, video_data_header, audio_data_header, thresholds):

        self.video_data_header = video_data_header
        self.audio_data_header = audio_data_header

        # loss counters
        self.video_loss_cnt = 0
        self.audio_loss_cnt = 0

        self.set_thresholds(thresholds)

        errs = {'black': ErrorCounter(),
                'freeze': ErrorCounter(),
                'blocky': ErrorCounter(),
                'silence': ErrorCounter(),
                'loudness': ErrorCounter()}

    def set_analysis_settings(self, analysis_settings):
        pass

    def get_errors(self):
        results = []

        # flags to send
        video_flags = [False]*4
        audio_flags = [False]*3
        # iterating over measured parameters
        for buf in self.buffers:
            loss_flag, err_flag = self.parse_buffer(self.buffers.index(buf),
                                                    buf)

        if loss_flag is True:
            self.video_loss_cnt += 1
            if self.video_loss_cnt >= self.video_loss:
                pass
        else:
            self.loss_cnt = 0

        results.append(([video_data_header, video_flags],
                        [audio_data_header, audio_flags]))

        return results

