from gi.repository import GObject

from Control import AnalysisSettingsIndexes as ai
from Control.ErrorDetector import StatusTypes as types
from Control.ErrorDetector.BaseErrorDetector import BaseErrorDetector


class VideoErrorDetector(BaseErrorDetector):
    def __init__(self,
                 prog_list,
                 analysis_settings,
                 gui):

        BaseErrorDetector.__init__(self, prog_list, 'video')

        # main gui window
        self.gui = gui

        self.is_black_flag = types.UNKNOWN
        self.is_freeze_flag = types.UNKNOWN
        self.is_blocky_flag = types.UNKNOWN
        self.is_loss_flag = types.UNKNOWN

        self.video_loss = 0

        self.black_err = 0
        self.black_warn = 0
        self.black_luma_warn = 0

        self.freeze_err = 0
        self.freeze_warn = 0
        self.freeze_diff_warn = 0

        self.block_err = 0
        self.block_warn = 0

        self.set_analysis_settings(analysis_settings)

        GObject.timeout_add(1000, self.on_parse_video_data)

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

    def is_loss(self, is_black, is_freeze, is_blocky, storage):
        if is_black is types.UNKNOWN or \
                    is_freeze is types.UNKNOWN or \
                    is_blocky is types.UNKNOWN:
            # TODO: see if this value should ever overflow and become 0
            storage.loss_cnt += 1
            if storage.loss_cnt >= self.video_loss:
                return types.ERR
            else:
                if self.is_loss_flag == types.UNKNOWN:
                    return types.UNKNOWN
                # else return that there is no video loss
                else:
                    return types.NO_ERR
        else:
            storage.loss_cnt = 0
            return types.NO_ERR

    def is_blocky(self, blocky_level):
        if blocky_level is None:
            return types.UNKNOWN
        elif blocky_level > self.block_err:
            return types.ERR
        elif blocky_level > self.block_warn:
            return types.WARN
        else:
            return types.NO_ERR

    def is_black(self, black_pix_num, av_luma):
        if black_pix_num is None or av_luma is None:
            return types.UNKNOWN
        elif black_pix_num > self.black_err:
            return types.ERR
        elif black_pix_num > self.black_warn:
            return types.WARN
        elif av_luma < self.black_luma_warn:
            return types.WARN
        else:
            return types.NO_ERR

    def is_freeze(self, freeze_pix_num, av_diff):
        if freeze_pix_num is None or av_diff is None:
            return types.UNKNOWN
        elif freeze_pix_num > self.freeze_err:
            return ERR
        elif freeze_pix_num > self.freeze_warn:
            return types.WARN
        elif av_diff < self.freeze_diff_warn:
            return types.WARN
        else:
            return types.NO_ERR

    def on_parse_video_data(self):
        results = []
        for storage in self.storage_list:
            av_black = storage.black_average
            av_freeze = storage.freeze_average
            av_block = storage.blocky_average
            av_luma = storage.luma_average
            av_diff = storage.diff_average

            self.is_black_flag = self.is_black(av_black, av_luma)
            self.is_freeze_flag = self.is_freeze(av_freeze, av_diff)
            self.is_blocky_flag = self.is_blocky(av_block)
            self.is_loss_flag = self.is_loss(self.is_black_flag,
                                             self.is_freeze_flag,
                                             self.is_blocky_flag,
                                             storage)

            results.append([storage.prog_info,
                            [self.is_loss_flag,           # video loss
                             self.is_black_flag,          # black frame
                             self.is_freeze_flag,         # freeze
                             self.is_blocky_flag]])       # blockiness

        self.gui.update_video_status(results)

        return True
