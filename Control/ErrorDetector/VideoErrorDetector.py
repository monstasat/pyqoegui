from collections import deque

from gi.repository import GObject

from Control import AnalysisSettingsIndexes as ai
from Control.ErrorDetector import StatusTypes as types
from Control.ErrorDetector.BaseErrorDetector import BaseErrorDetector

class VideoErrorDetector(BaseErrorDetector):

    def __init__(self,
                 prog_info,
                 thresholds):

        BaseErrorDetector.__init__(self, prog_info, thresholds, 'video')

        GObject.timeout_add(1000, self.on_parse_video_data)

    def parse_buffer(self, thresh_cont, thresh_time, thresh_peak, buf):
        loss_flag = False
        err_flag = False

        # if buffer is not empty
        if len(buf) > 0:
            # find values higher than peak threshold value
            peaks = list(filter((lambda x: x >= thresh_peak), buf))
            # if peaks were detected
            if len(peaks) > 0:
                err_flag = True

            # find values higher that continuous threshold value
            err_values = list(filter((lambda x: x >= thresh_cont), buf))
            # if all values in buffer are about threshold
            if len(err_values) == len(buf):
                err_flag = True
        else:
            loss_flag = True

        return [loss_flag, err_flag]

    def on_parse_video_data(self):
        # iterating over measured parameters
        for buf in self.buffers:
            self.parse_buffer(thresh_cont, thresh_time, thresh_peak, buf)

            results.append([hdr,
                            [self.is_loss_flag,           # video loss
                             self.is_black_flag,          # black frame
                             self.is_freeze_flag,         # freeze
                             self.is_blocky_flag]])       # blockiness

        for interface in self.interfaces:
            interface.update_video_status(list(results))

        return True

