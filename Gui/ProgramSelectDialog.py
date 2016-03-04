# data format from gs pipeline
# stream id
# num
# name
# provider
# pids num
# pid
# pid type
# codec name

from gi.repository import Gtk

from Gui.Placeholder import Placeholder
from Gui.BaseDialog import BaseDialog
from Gui.ProgramTreeView import ProgramTreeView
from Gui import Spacing


class ProgramSelectDialog(BaseDialog):

    def __init__(self, parent):
        BaseDialog.__init__(self, "Выбор программ для анализа", parent)

        self.set_default_size(500, 0)

        # get dialog box
        mainBox = self.get_content_area()

        # packing elements to dialog
        scrollWnd = Gtk.ScrolledWindow(vexpand=True,
                                       hexpand=True,
                                       halign=Gtk.Align.FILL,
                                       valign=Gtk.Align.FILL,
                                       hscrollbar_policy=2)
        scrollWnd.set_size_request(400, 400)
        self.progTree = ProgramTreeView(parent.store)

        # creating prog list overlay
        overlay = Gtk.Overlay(valign=Gtk.Align.FILL,
                              hexpand=True,
                              vexpand=True)
        overlay.add(self.progTree)
        self.holder = Placeholder("dialog-warning-symbolic",
                                  'Программ не найдено',
                                  72)
        overlay.add_overlay(self.holder)

        # connect to store signals
        parent.store.connect('row-deleted', self.on_row_deleted)
        parent.store.connect('row-inserted', self.on_row_inserted)

        # connect to show signal
        self.connect('show', self.on_shown)

        scrollWnd.add(overlay)

        # add box container to mainBox
        mainBox.add(scrollWnd)

        # to determine if we need to display placeholder initially
        self.on_store_changed()

    def on_shown(self, widget):
        self.show_all()
        self.on_store_changed()

    def on_btn_clicked_apply(self, widget):
        BaseDialog.on_btn_clicked_apply(self, widget)

    def on_row_inserted(self, path, iter, user_data):
        self.on_store_changed()

    def on_row_deleted(self, path, user_data):
        self.on_store_changed()

    def on_store_changed(self):
        # if some streams are appended to store, do not show placeholder
        if len(self.progTree.store) > 0:
            # open all program rows
            piter = self.progTree.store.get_iter_first()
            while piter is not None:
                path = self.progTree.store.get_path(piter)
                if self.progTree.row_expanded(path) is False:
                    self.progTree.expand_row(path, False)
                piter = self.progTree.store.iter_next(piter)
            # hide placeholder
            self.holder.hide()
        else:
            self.holder.set_text('Программ не найдено')
            self.holder.show_all()

