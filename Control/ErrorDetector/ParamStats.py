from Control.ErrorDetector.StatusTypes import STYPES

class ParamStats():

    def __init__(self, name):

        self.name = name

        self.total_values = 0
        self.counter = 0
        self.error_sequence = 0

        self.peak_error = False
        self.cont_error = False

        self.cont_predicate = lambda x: False
        self.peak_predicate = lambda x: False
        self.time_predicate = lambda x, y: x == y

        self.time = 0
        self.time_cnt = 0

    def eval(self, buf):
        # accumulate values number
        self.total_values += len(buf[0]) if (type(buf) is tuple) else len(buf)

        # find values higher than peak threshold value
        iterable = zip(*buf) if (type(buf) is tuple) else buf
        for val in iterable:
            if self.peak_predicate(val) is True:
                self.peak_error = True

            if self.cont_predicate(val) is True:
                self.counter += 1
            else:
                if self.counter > self.error_sequence:
                    self.error_sequence = self.counter
                self.counter = 0

        # find values higher that continuous threshold value
        #self.error_values += len(list(filter(self.cont_predicate, buf)))

    def get_error(self):
        error_flag = STYPES['unkn']
        loss_flag = (self.total_values == 0)
        seq_equal_flag = False

        self.time_cnt += 1

        if self.counter > self.error_sequence:
            self.error_sequence = self.counter

        if self.name == 'black':
            print("err_seq: ", self.error_sequence)
            print("tot_seq: ", self.total_values)

        seq_equal_flag = False if loss_flag else \
                         self.time_predicate(self.total_values,
                                             self.error_sequence)

        if self.time_cnt >= self.time:
            if seq_equal_flag is True:
                self.cont_error = True
            # reset counters
            self.total_values = 0
            self.error_sequence = 0
            self.counter = 0
            self.time_cnt = 0

        if seq_equal_flag is False:
            self.cont_error = False

        error_flag = STYPES['err'] if (self.peak_error | self.cont_error) \
                     else STYPES['norm']

        self.peak_error = False

        return (loss_flag, error_flag)

