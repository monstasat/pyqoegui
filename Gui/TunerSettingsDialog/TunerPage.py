from gi.repository import Gtk

from Gui.BaseDialog import ComboBox
from Gui.TunerSettingsDialog.TunerStatusBox import TunerStatusBox
from Gui.TunerSettingsDialog.TunerSettingsBox import TunerSettingsBox
from Gui import Spacing

class TunerPage(Gtk.Box):
    def __init__(self, slot_id, tuner_settings, standard_model):
        # standard selection page
        Gtk.Box.__init__(self,
                         spacing=Spacing.ROW_SPACING,
                         orientation=Gtk.Orientation.HORIZONTAL,
                         valign=Gtk.Align.FILL,
                         halign=Gtk.Align.FILL,
                         vexpand=True,
                         hexpand=True)

        self.set_property("margin_top", 5)

        self.slot_id = slot_id
        
        self.standard_box = Gtk.Box(spacing=Spacing.ROW_SPACING,
                                    border_width=Spacing.BORDER,
                                    orientation=Gtk.Orientation.VERTICAL)

        self.standard_combo = ComboBox("Выбор стандарта ТВ сигнала",
                                       standard_model)
        self.standard_box.add(self.standard_combo)
        self.standard_box.show_all()

        # standard settings pages
        self.dvbt2_box = TunerSettingsBox('DVB-T2')
        self.dvbt_box = TunerSettingsBox('DVB-T')
        self.dvbc_box = TunerSettingsBox('DVB-C')
        self.status_box = TunerStatusBox()

        # fill page list with created pages
        self.pages = []
        self.pages.append((self.standard_box, "standard", "Выбор стандарта"))
        self.pages.append((self.dvbt2_box, "dvbt2", "Настройки DVB-T2"))
        self.pages.append((self.dvbt_box, "dvbt", "Настройки DVB-T"))
        self.pages.append((self.dvbc_box, "dvbc", "Настройки DVB-C"))
        self.pages.append((self.status_box, "status", "Статус сигнала"))

        # create stack
        self.stack = Gtk.Stack(halign=Gtk.Align.FILL, hexpand=True)
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_UP_DOWN)
        list(map(lambda x: self.stack.add_titled(x[0], x[1], x[2]),
                 self.pages))

        # create stack sidebar
        self.stackSidebar = Gtk.StackSidebar(vexpand=True, hexpand=False,
                                             halign=Gtk.Align.START,
                                             stack=self.stack)
        # create separator
        separator = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)

        # pack items to main container
        self.pack_start(self.stackSidebar, False, False, 0)
        self.pack_start(separator, False, False, 0)
        self.pack_start(self.stack, True, True, 0)
