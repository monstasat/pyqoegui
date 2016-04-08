from gi.repository import Gtk

from Gui import Spacing


class BaseDialog(Gtk.Dialog):

    def __init__(self, myTitle, parent):
        Gtk.Dialog.__init__(self, myTitle, parent,
                            Gtk.DialogFlags.USE_HEADER_BAR)

        self.set_modal(True)
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
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
        mainBox.set_hexpand(True)

        # connect to show signal
        self.connect('show', self.on_shown)

        # delete all children from main box
        list(map(lambda x: mainBox.remove(x), mainBox.get_children()))

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
        Gtk.Box.__init__(self, hexpand=True, vexpand=False,
                         orientation=Gtk.Orientation.HORIZONTAL,
                         spacing=Spacing.COL_SPACING)

        # value entry
        self.combobox = Gtk.ComboBox(hexpand=True, vexpand=False, model=store,
                                     halign=Gtk.Align.END,
                                     valign=Gtk.Align.CENTER)
        self.combobox.set_size_request(150, -1)
        renderer_text = Gtk.CellRendererText()
        self.combobox.pack_start(renderer_text, True)
        self.combobox.add_attribute(renderer_text, "text", 0)
        self.combobox.set_active(0)

        # setting name
        self.label = Gtk.Label(label=label, hexpand=True, vexpand=False,
                               halign=Gtk.Align.START, valign=Gtk.Align.CENTER)

        self.add(self.label)
        self.add(self.combobox)
        self.show_all()


# box with label and spin button
class SettingEntry(Gtk.Box):
    def __init__(self, index, label, min_, max_, switch=False):
        Gtk.Box.__init__(self, hexpand=True, vexpand=False,
                         orientation=Gtk.Orientation.HORIZONTAL,
                         spacing=Spacing.COL_SPACING)

        self.index = index

        # value entry
        self.spinBtn = Gtk.SpinButton(numeric=True, digits=2, climb_rate=2,
                                      hexpand=True, vexpand=True,
                                      halign=Gtk.Align.END,
                                      valign=Gtk.Align.CENTER)
        self.spinBtn.set_range(min_, max_)
        self.spinBtn.set_increments(0.1, 1)
        self.spinBtn.set_size_request(150, -1)

        self.switch = Gtk.Switch(halign=Gtk.Align.END)

        # setting name
        self.label = Gtk.Label(label=label, hexpand=True, vexpand=False,
                               halign=Gtk.Align.START, valign=Gtk.Align.CENTER)

        self.add(self.label)
        self.add(self.spinBtn)
        if switch is True:
            self.add(self.switch)
        self.show_all()

    def set_label(self, text):
        self.label.set_text(text)

    def set_value(self, value):
        self.spinBtn.set_value(value)

