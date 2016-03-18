from gi.repository import Gtk


# list store containing terrestrial frequencies
class TerrestrialFrequencyModel(Gtk.ListStore):
    def __init__(self):
        Gtk.ListStore.__init__(self, str, int, int)
        self.fill_model()

    # fill model with frequency values
    def fill_model(self):
        for index in range(1, 57):
            if index == 0:
                ch = 0
                freq = 0
            elif index <= 7:
                ch = index + 5
                freq = (ch*8 + 130) * 1000000
            else:
                ch = index + 13
                freq = (ch*8 + 306) * 1000000
            ch_string = 'ТВК %02d (%g МГц)' % (ch, freq / 1000000)
            self.append([ch_string, ch, freq])

