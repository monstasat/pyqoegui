from gi.repository import Gtk

from Gui.BaseDialog import BaseDialog


class TerrestrialFrequencyModel(Gtk.ListStore):
    def __init__(self):
        Gtk.ListStore.__init__(self, int, int)

        # fill the model with values
        self.fill_model()

    # fill model with frequency values
    def fill_model(self):

        # tv channel number
        ch = 0
        # tv channel frequency
        freq = 0

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
            self.append([ch, freq])


class CableFrequencyModel(Gtk.ListStore):
    def __init__(self):
        Gtk.ListStore.__init__(self, int, int, bool)

        # fill the model with values
        self.fill_model()

    # fill model with frequency values
    def fill_model(self):

        # tv channel number
        ch = 0
        # tv channel frequency
        freq = 0
        # special channel flag
        spec = False

        for index in range(1, 100):
            if index == 0:
                ch = 0
                freq = 0
                spec = False
            elif index == 1:
                ch = index
                freq = 52500000
                spec = False
            elif index == 2:
                ch = index
                freq = (index*8 + 46) * 1000000
                spec = False
            elif (index >= 3) and (index <= 5):
                ch = index
                freq = (index*8 + 56) * 1000000
                special = False
            elif (index >= 6) and (index <= 13):
                ch = index - 5
                freq = (index*8 + 66) * 1000000
                spec = True
            elif (index >= 14) and (index <= 17):
                ch = index - 8
                freq = (index*8 + 66) * 1000000
                spec = False
            elif (index >= 18) and (index <= 20):
                ch = index - 8
                freq = (index*8 + 66) * 1000000
                spec = False
            elif (index >= 21) and (index <= 50):
                ch = index - 10
                freq = (index*8 + 66) * 1000000
                spec = True
            else:
                ch = index - 30
                freq = (index*8 + 66) * 1000000
                spec = False


class TunerSettingsDialog(BaseDialog):
    def __init__(self, parent):
        BaseDialog.__init__(self, "Настройки тюнера", parent)

        freq_terrestrial = TerrestrialFrequencyModel()
        freq_cable = CableFrequencyModel()

        mainBox = self.get_content_area()

        # fill page list with created pages
        self.pages = []

        # create stack
        self.stack = Gtk.Stack(halign=Gtk.Align.FILL, hexpand=True)

        # set stack transition type
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_UP_DOWN)

        # add pages to stack
        for page in self.pages:
            self.stack.add_titled(page[0], page[1], page[2])

        # create stack sidebar
        self.stackSidebar = Gtk.StackSidebar(
            vexpand=True,
            hexpand=False,
            halign=Gtk.Align.START)
        self.stackSidebar.set_stack(self.stack)
        self.stackSidebar.show()

        # configure main container orientation
        mainBox.set_orientation(Gtk.Orientation.HORIZONTAL)
        # pack items to main container
        mainBox.pack_start(self.stackSidebar, False, False, 0)
        separator = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        mainBox.pack_start(separator, False, False, 0)
        mainBox.pack_start(self.stack, True, True, 0)

        self.show_all()

