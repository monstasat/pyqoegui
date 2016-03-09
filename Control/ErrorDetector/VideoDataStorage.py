from collections import deque


class VideoDataStorage():
    def __init__(self, prog_info):
        self.prog_info = prog_info
        self.black_num = deque()
        self.freeze_num = deque()
        self.blocky_level = deque()
        self.av_luma = deque()
        self.av_diff = deque()

        self.loss_cnt = 0

    def get_average(self, value_deque):
        if len(value_deque) > 0:
            av = sum(value_deque) / len(value_deque)
            value_deque.clear()
        else:
            av = None

        return av

    @property
    def black_average(self):
        return self.get_average(self.black_num)

    @property
    def freeze_average(self):
        return self.get_average(self.freeze_num)

    @property
    def blocky_average(self):
        return self.get_average(self.blocky_level)

    @property
    def luma_average(self):
        return self.get_average(self.av_luma)

    @property
    def diff_average(self):
        return self.get_average(self.av_diff)
