from gi.repository import Gtk

from Gui.BaseDialog import BaseDialog
from Gui.Placeholder import Placeholder
from Gui import Spacing

class DumpSettingsDialog(BaseDialog):
    def __init__(self, parent):

        BaseDialog.__init__(self, "Запись ТВ программ", parent)

        mainBox = self.get_content_area()
        mainBox.set_valign(Gtk.Align.CENTER)
        mainBox.set_border_width(Spacing.BORDER)

        temp_view = Placeholder("action-unavailable-symbolic",
                                "Функция записи программ находится"
                                " в стадии разработки",
                                72)

        self.applyBtn.set_sensitive(False)

        mainBox.add(temp_view)

