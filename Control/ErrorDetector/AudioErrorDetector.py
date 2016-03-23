from gi.repository import GObject

from Control import AnalysisSettingsIndexes as ai
from Control.ErrorDetector import StatusTypes as types
from Control.ErrorDetector.BaseErrorDetector import BaseErrorDetector


class AudioErrorDetector(BaseErrorDetector):
    def __init__(self,
                 prog_list,
                 analysis_settings,
                 interfaces):

        BaseErrorDetector.__init__(self, prog_list, 'audio')

        # interfaces
        self.interfaces = interfaces

        self.is_overload_flag = types.UNKNOWN
        self.is_silence_flag = types.UNKNOWN
        self.is_loss_flag = types.UNKNOWN

        self.audio_loss = 0

        self.overload_err = 0
        self.overload_warn = 0

        self.silence_err = 0
        self.silence_warn = 0

        self.set_analysis_settings(analysis_settings)

        GObject.timeout_add(1000, self.on_parse_audio_data)

    def set_analysis_settings(self, analysis_settings):

        self.audio_loss = analysis_settings[ai.AUDIO_LOSS][2]

        self.overload_err = analysis_settings[ai.OVERLOAD_ERR][2]
        self.overload_warn = analysis_settings[ai.OVERLOAD_WARN][2]

        self.silence_err = analysis_settings[ai.SILENCE_ERR][2]
        self.silence_warn = analysis_settings[ai.SILENCE_WARN][2]

    def is_loss(self, is_overload, is_silence, storage):
        if is_overload is types.UNKNOWN or \
                    is_silence is types.UNKNOWN:
            # TODO: see if this value should ever overflow and become 0
            storage.loss_cnt += 1
            if storage.loss_cnt >= self.audio_loss:
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

    def is_loud_or_is_silent(self, audio_level):
        if audio_level is None:
            return [types.UNKNOWN, types.UNKNOWN]
        elif audio_level > self.overload_err:
            return [types.ERR, types.NO_ERR]
        elif audio_level > self.overload_warn:
            return [types.WARN, types.NO_ERR]
        elif audio_level < self.silence_err:
            return [types.NO_ERR, types.ERR]
        elif audio_level < self.silence_warn:
            return [types.NO_ERR, types.WARN]
        else:
            return [types.NO_ERR, types.NO_ERR]

    def on_parse_audio_data(self):
        results = []
        for storage in self.storage_list:
            av_momentary = storage.momentary_average
            loud_result = self.is_loud_or_is_silent(storage.short_term_average)

            self.is_overload_flag = loud_result[0]
            self.is_silence_flag = loud_result[1]

            self.is_loss_flag = self.is_loss(self.is_overload_flag,
                                             self.is_silence_flag,
                                             storage)

            results.append([storage.prog_info,
                            [self.is_loss_flag,           # audio loss
                             self.is_silence_flag,        # silence flag
                             self.is_overload_flag]])     # overload flag

        for interface in self.interfaces:
            interface.update_audio_status(results)

        return True

