from Control.ErrorDetector.StatusTypes import STYPES

class ErrorCounter():

    def __init__(self):

        self.total_values = 0
        self.error_values = 0

        self.peak_error = False

        self.cont_predicate = lambda x: False
        self.peak_predicate = lambda x: False
        self.perc_predicate = lambda x, y: x == y

        self.time = 0
        self.time_cnt = 0

    def eval(self, buf):
        # accumulate values number
        self.total_values += len(buf[0]) if (type(buf) is tuple) else len(buf)

        # find values higher than peak threshold value
        for val in buf:
            if self.peak_predicate(val) is True:
                self.peak_error = True
                break

        # find values higher that continuous threshold value
        self.error_values += len(list(filter(self.cont_predicate, buf)))

    def get_error(self):
        loss_flag, error_flag = False, STYPES['unkn']

        loss_flag = (self.total_values == 0)
        self.time_cnt += 1

        if self.time_cnt >= self.time:

            lt_error = False if loss_flag else \
                       self.perc_predicate(self.total_values,
                                           self.error_values)

            error_flag = STYPES['err'] if (self.peak_error | lt_error) else \
                         STYPES['norm']

            # clear values
            self.peak_error = False
            self.total_values = 0
            self.error_values = 0

            self.time_cnt = 0

        return (loss_flag, error_flag)

