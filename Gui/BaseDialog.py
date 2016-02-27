from gi.repository import Gtk

from Gui import Spacing


class BaseDialog(Gtk.Dialog):

    def __init__(self, myTitle, parent):
        Gtk.Dialog.__init__(self,
                            myTitle,
                            parent,
                            Gtk.DialogFlags.USE_HEADER_BAR)

        self.set_modal(True)
        self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.set_default_size(500, 500)

        # custom header bar
        header = Gtk.HeaderBar(title=myTitle)
        # not showing 'x' at the header bar
        header.set_show_close_button(False)
        cancelBtn = Gtk.Button(stock=Gtk.STOCK_CANCEL)
        cancelBtn.connect('clicked', self.on_btn_clicked_cancel)
        header.pack_start(cancelBtn)
        self.applyBtn = Gtk.Button(stock=Gtk.STOCK_APPLY)
        self.applyBtn.connect('clicked', self.on_btn_clicked_apply)
        self.applyBtn.get_style_context().add_class(
            Gtk.STYLE_CLASS_SUGGESTED_ACTION)
        header.pack_end(self.applyBtn)
        self.set_titlebar(header)

        mainBox = self.get_content_area()

        # delete all children from main box
        # (I don't know why there are any of them in newly created dialog)
        children = mainBox.get_children()
        for child in children:
            mainBox.remove(child)

    # event when user clicks apply button
    def on_btn_clicked_apply(self, widget):
        self.response(Gtk.ResponseType.APPLY)

    # event when user clicks cancel button
    def on_btn_clicked_cancel(self, widget):
        self.response(Gtk.ResponseType.CANCEL)

