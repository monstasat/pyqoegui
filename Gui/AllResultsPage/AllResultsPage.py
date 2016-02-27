from gi.repository import Gtk

from Gui.Placeholder import Placeholder


class AllResultsPage(Gtk.VBox):
    def __init__(self):
        Gtk.VBox.__init__(self)
        self.add(Placeholder("action-unavailable-symbolic",
                             "Окно временно недоступно. "
                             "Ведётся разработка интерфейса.",
                             72))

