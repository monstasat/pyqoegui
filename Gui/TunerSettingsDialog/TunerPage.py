from gi.repository import Gtk

from Control.DVBTunerConstants import *
from Gui.BaseDialog import ComboBox
from Gui.TunerSettingsDialog.TunerStatusBox import TunerStatusBox
from Gui.TunerSettingsDialog.TunerSettingsBox import TunerSettingsBox
from Gui import Spacing

class TunerPage(Gtk.Box):
    def __init__(self, slot_id, settings, standard_model):
        # standard selection page
        Gtk.Box.__init__(self,
                         spacing=Spacing.ROW_SPACING,
                         orientation=Gtk.Orientation.HORIZONTAL,
                         valign=Gtk.Align.FILL,
                         halign=Gtk.Align.FILL,
                         vexpand=True,
                         hexpand=True)

        self.slot_id = slot_id

        self.standard_combo = ComboBox("Выбор стандарта ТВ сигнала",
                                       standard_model)
        self.standard_box = Gtk.Box(spacing=Spacing.ROW_SPACING,
                                    border_width=Spacing.BORDER,
                                    orientation=Gtk.Orientation.VERTICAL)
        self.standard_box.add(self.standard_combo)
        self.standard_box.show_all()

        # standard settings pages
        self.dvbt2_box = TunerSettingsBox(DVBT2)
        self.dvbt_box = TunerSettingsBox(DVBT)
        self.dvbc_box = TunerSettingsBox(DVBC)
        self.status_box = TunerStatusBox(slot_id, settings)

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

        self.on_new_tuner_settings(settings)

    def on_new_tuner_settings(self, settings):
        if "device" in settings:
            self.standard_combo.combobox.set_active(settings['device'])
        if "t2_freq" in settings:
            self.dvbt2_box.frequency = settings['t2_freq']
        if "t2_bw" in settings:
            self.dvbt2_box.bandwidth = settings['t2_bw']
        if "t2_plp_id" in settings:
            self.dvbt2_box.plp_id = settings['t2_plp_id']
        if "t_freq" in settings:
            self.dvbt_box.frequency = settings['t_freq']
        if "t_bw" in settings:
            self.dvbt_box.bandwidth = settings['t_bw']
        if "c_freq" in settings:
            self.dvbc_box.frequency = settings['c_freq']
        if "c_bw" in settings:
            self.dvbc_box.bandwidth = settings['c_bw']

        self.status_box.on_new_tuner_settings(settings)

    def on_new_devinfo(self, devinfo):
        self.status_box.on_new_devinfo(devinfo)

    def on_new_meas(self, meas):
        self.status_box.on_new_meas(meas)

    def on_new_params(self, params):
        self.status_box.on_new_params(params)

    def on_new_plp_list(self, plp_list):
        self.dvbt2_box.on_new_plp_list(plp_list)
