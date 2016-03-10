from collections import deque


class AudioDataStorage():
    def __init__(self, prog_info):
        self.prog_info = prog_info
        self.momentary = deque()
        self.short_term = deque()

        self.loss_cnt = 0

    # extend deques with new data
    def push_new_data(self, data):
        self.momentary.extend(data[0])
        self.short_term.extend(data[1])

    def get_average(self, value_deque):
        if len(value_deque) > 0:
            av = sum(value_deque) / len(value_deque)
            value_deque.clear()
        else:
            av = None

        return av

    @property
    def momentary_average(self):
        return self.get_average(self.momentary)

    @property
    def short_term_average(self):
        return self.get_average(self.short_term)

