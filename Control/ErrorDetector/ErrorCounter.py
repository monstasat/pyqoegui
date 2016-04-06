class ErrorCounter():

    def __init__(self):

        self.total_values = 0
        self.error_values = 0

        self.peak_error = False

        self.cont_predicate = lambda x: False
        self.peak_predicate = lambda x: False
        self.perc_predicate = lambda x, y: x == y

    def eval(buf):
        # accumulate values number
        self.total_values += len(buf)

        # find values higher than peak threshold value
        for val in buf:
            if self.peak_predicate(val) is True:
                self.peak_error = True
                break

        # find values higher that continuous threshold value
        self.error_values = len(list(filter(self.cont_predicate, buf)))

        return

    def get_error(self):
        lt_error = False if (self.total_values == 0) else \
                   self.perc_predicate(self.total_values, self.error_values)

        error = self.peak_error | lt_error

        # clear values
        self.peak_error = False
        self.total_values = 0
        self.error_values = 0

        return error

