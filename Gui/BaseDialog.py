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
        self.header = Gtk.HeaderBar(title=myTitle)
        # not showing 'x' at the header bar
        self.header.set_show_close_button(False)
        cancelBtn = Gtk.Button(stock=Gtk.STOCK_CANCEL)
        cancelBtn.connect('clicked', self.on_btn_clicked_cancel)
        self.header.pack_start(cancelBtn)
        self.applyBtn = Gtk.Button(stock=Gtk.STOCK_APPLY)
        self.applyBtn.connect('clicked', self.on_btn_clicked_apply)
        self.applyBtn.get_style_context().add_class(
            Gtk.STYLE_CLASS_SUGGESTED_ACTION)
        self.header.pack_end(self.applyBtn)
        self.set_titlebar(self.header)

        mainBox = self.get_content_area()

        # connect to show signal
        self.connect('show', self.on_shown)

        # delete all children from main box
        # (I don't know why there are any of them in newly created dialog)
        children = mainBox.get_children()
        for child in children:
            mainBox.remove(child)

    # when dialog is to be shown
    def on_shown(self, widget):
        self.show_all()

    # event when user clicks apply button
    def on_btn_clicked_apply(self, widget):
        self.response(Gtk.ResponseType.APPLY)

    # event when user clicks cancel button
    def on_btn_clicked_cancel(self, widget):
        self.response(Gtk.ResponseType.CANCEL)


# box with label and combobox
class ComboBox(Gtk.Box):
    def __init__(self, label, store):
        Gtk.Box.__init__(self)

        self.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.set_hexpand(True)
        self.set_vexpand(False)
        self.set_spacing(Spacing.COL_SPACING)

        # value entry
        self.combobox = Gtk.ComboBox.new_with_model(store)
        self.combobox.set_hexpand(True)
        self.combobox.set_vexpand(False)
        self.combobox.set_halign(Gtk.Align.END)
        self.combobox.set_valign(Gtk.Align.CENTER)
        self.combobox.set_size_request(150, -1)
        renderer_text = Gtk.CellRendererText()
        self.combobox.pack_start(renderer_text, True)
        self.combobox.add_attribute(renderer_text, "text", 0)
        self.combobox.set_active(0)

        # setting name
        self.label = Gtk.Label(label=label)
        self.label.set_hexpand(True)
        self.label.set_vexpand(False)
        self.label.set_halign(Gtk.Align.START)
        self.label.set_valign(Gtk.Align.CENTER)

        self.add(self.label)
        self.add(self.combobox)

        self.show_all()


# box with label and spin button
class SettingEntry(Gtk.Box):
    def __init__(self, index, label, min_, max_):
        Gtk.Box.__init__(self)

        self.index = index

        self.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.set_hexpand(True)
        self.set_vexpand(False)
        self.set_spacing(Spacing.COL_SPACING)

        # value entry
        self.spinBtn = Gtk.SpinButton()
        self.spinBtn.set_numeric(True)
        self.spinBtn.set_range(min_, max_)
        self.spinBtn.set_digits(2)
        self.spinBtn.set_increments(0.1, 1)
        self.spinBtn.set_hexpand(True)
        self.spinBtn.set_vexpand(False)
        self.spinBtn.set_halign(Gtk.Align.END)
        self.spinBtn.set_valign(Gtk.Align.CENTER)
        self.spinBtn.set_size_request(150, -1)
        self.spinBtn.set_property('climb-rate', 2)

        # setting name
        self.label = Gtk.Label(label=label)
        self.label.set_hexpand(True)
        self.label.set_vexpand(False)
        self.label.set_halign(Gtk.Align.START)
        self.label.set_valign(Gtk.Align.CENTER)

        self.add(self.label)
        self.add(self.spinBtn)

        self.show_all()

    def set_label(self, text):
        self.label.set_text(text)

    def set_value(self, value):
        self.spinBtn.set_value(value)

