from gi.repository import GObject

from Control.ErrorDetector.DataStorage import DataStorage
from Control import ErrorTypesModel as em

NO_ERR = 1
WARN = 2
ERR = 3
UNKNOWN = 0


class ErrorDetector(GObject.GObject):
    def __init__(self,
                 prog_list,
                 analysis_settings,
                 gui):

        # main gui window
        self.gui = gui

        # list of measured data headers
        self.valid_video_headers = []
        self.storage_list = []

        self.black_err = 0
        self.black_warn = 0
        self.black_luma_warn = 0

        self.freeze_err = 0
        self.freeze_warn = 0
        self.freeze_diff_warn = 0

        self.block_err = 0
        self.block_warn = 0

        self.set_programs_list(prog_list)
        self.set_analysis_settings(analysis_settings)

        GObject.timeout_add(1000, self.on_get_average)

    def set_programs_list(self, prog_list):

        self.valid_video_headers.clear()
        self.storage_list.clear()

        # get list of measured data headers for video
        for stream in prog_list:
            stream_id = stream[0]
            for prog in stream[1]:
                data_header = []
                prog_id = prog[0]
                data_header.append(int(stream_id))
                data_header.append(int(prog_id))
                for pid in prog[4]:
                    pid_type = pid[2].split('-')[0]
                    if pid_type == 'video':
                        data_header.append(int(pid[0]))
                        self.valid_video_headers.append(data_header)

        for prog in self.valid_video_headers:
            self.storage_list.append(DataStorage(prog))

    def set_analysis_settings(self, analysis_settings):

        self.black_err = analysis_settings[em.BLACK_ERR][2]
        self.black_warn = analysis_settings[em.BLACK_WARN][2]
        self.black_luma_warn = analysis_settings[em.LUMA_WARN][2]

        self.freeze_err = analysis_settings[em.FREEZE_ERR][2]
        self.freeze_warn = analysis_settings[em.FREEZE_WARN][2]
        self.freeze_diff_warn = analysis_settings[em.DIFF_WARN][2]

        self.block_err = analysis_settings[em.BLOCK_ERR][2]
        self.block_warn = analysis_settings[em.BLOCK_WARN][2]

    def is_blocky(self, blocky_level):
        if blocky_level > self.block_err:
            return ERR
        elif blocky_level > self.block_warn:
            return WARN
        else:
            return NO_ERR

    def is_black(self, black_pix_num, av_luma):
        if black_pix_num > self.black_err:
            return ERR
        elif black_pix_num > self.black_warn:
            return WARN
        elif av_luma < self.black_luma_warn:
            return WARN
        else:
            return NO_ERR

    def is_freeze(self, freeze_pix_num, av_diff):
        if freeze_pix_num > self.freeze_err:
            return ERR
        elif freeze_pix_num > self.freeze_warn:
            return WARN
        elif av_diff < self.freeze_diff_warn:
            return WARN
        else:
            return NO_ERR

    def set_video_data(self, vparams):
        try:
            index = self.valid_video_headers.index(vparams[0])
        except:
            print("no such prog")
        else:
            storage = self.storage_list[index]
            storage.black_num.extend(vparams[1][0])
            storage.freeze_num.extend(vparams[1][1])
            storage.blocky_level.extend(vparams[1][2])
            storage.av_luma.extend(vparams[1][3])
            storage.av_diff.extend(vparams[1][4])

    def on_get_average(self):
        results = []
        for storage in self.storage_list:
            av_black = storage.black_average
            av_freeze = storage.freeze_average
            av_block = storage.blocky_average
            av_luma = storage.luma_average
            av_diff = storage.diff_average

            is_black = self.is_black(av_black, av_luma)
            is_freeze = self.is_freeze(av_freeze, av_diff)
            is_blocky = self.is_blocky(av_block)

            results.append([storage.prog_info,
                            [NO_ERR,        # video loss
                             is_black,      # black frame
                             is_freeze,     # freeze
                             is_blocky,     # blockiness
                             NO_ERR,        # audio loss
                             NO_ERR,        # silence
                             NO_ERR]])      # loudness

        self.gui.on_data_from_error_detector(results)

        return True

