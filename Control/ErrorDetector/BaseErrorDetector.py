from collections import deque

from gi.repository import GObject

from Control.ErrorDetector import StatusTypes as types


class BaseErrorDetector(GObject.GObject):
    def __init__(self,
                 prog_info,
                 thresholds,
                 detector_type):

        # detector type: audio/video
        self.type = detector_type
        # corresponding program info
        self.prog_info = prog_info

        self.buffers = []

        # buffers for storing data
        self.params_num = 5 if (self.type is 'video') else 2
        self.buffers = [deque()]*self.params_num

        # list of error seconds sequences
        err_seconds = [0]*self.params_num

        # data loss counter
        self.loss_cnt = 0

        self.set_thresholds(thresholds)

    def set_analysis_settings(self, analysis_settings):

        self.video_loss = analysis_settings[ai.VIDEO_LOSS][2]

        self.black_err = analysis_settings[ai.BLACK_ERR][2]
        self.black_warn = analysis_settings[ai.BLACK_WARN][2]
        self.black_luma_warn = analysis_settings[ai.LUMA_WARN][2]

        self.freeze_err = analysis_settings[ai.FREEZE_ERR][2]
        self.freeze_warn = analysis_settings[ai.FREEZE_WARN][2]
        self.freeze_diff_warn = analysis_settings[ai.DIFF_WARN][2]

        self.block_err = analysis_settings[ai.BLOCK_ERR][2]
        self.block_warn = analysis_settings[ai.BLOCK_WARN][2]

        self.audio_loss = analysis_settings[ai.AUDIO_LOSS][2]

        self.overload_err = analysis_settings[ai.OVERLOAD_ERR][2]
        self.overload_warn = analysis_settings[ai.OVERLOAD_WARN][2]

        self.silence_err = analysis_settings[ai.SILENCE_ERR][2]
        self.silence_warn = analysis_settings[ai.SILENCE_WARN][2]

    def set_data(self, params):
        for buf, param in list(zip(self.buffers, params)):
            buf.extend(param)

