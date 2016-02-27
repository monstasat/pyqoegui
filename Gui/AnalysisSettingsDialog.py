from gi.repository import Gtk

from Gui.BaseDialog import BaseDialog
from Gui import Spacing

class SettingEntry(Gtk.Box):
    def __init__(self, label, min, max):
        Gtk.Box.__init__(self)

        self.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.set_hexpand(True)
        self.set_vexpand(False)
        self.set_spacing(Spacing.COL_SPACING)
        #self.set_homogeneous(True)

        # value entry
        self.spinBtn = Gtk.SpinButton()
        self.spinBtn.set_numeric(True)
        self.spinBtn.set_range(min, max)
        self.spinBtn.set_digits(3)
        self.spinBtn.set_increments(0.1, 1)
        self.spinBtn.set_hexpand(True)
        self.spinBtn.set_vexpand(False)
        self.spinBtn.set_halign(Gtk.Align.END)
        self.spinBtn.set_valign(Gtk.Align.CENTER)
        self.spinBtn.set_size_request(150, -1)

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

class BaseSettingsPage(Gtk.TreeView):
    def __init__(self, store):
        Gtk.TreeView.__init__(self)

        self.set_grid_lines(Gtk.TreeViewGridLines.BOTH)
        self.set_show_expanders(True)
        self.set_enable_tree_lines(True)
        sel = self.get_selection()
        sel.set_mode(Gtk.SelectionMode.NONE)
        self.set_border_width(Spacing.BORDER)

        # what programs to display?
        self.filter_type = 0

        # remember store
        self.store = store

        # creating store filter
        #self.store_filter = self.store.filter_new()
        # setting the filter function
        #self.store_filter.set_visible_func(self.pid_filter_func)

        # set model for tree view
        self.set_model(self.store)

        # the cellrenderer for the first column - text
        renderer_text = Gtk.CellRendererText()

        # the cellrenderer for the second column - spin
        self.renderer_spin = Gtk.CellRendererSpin()
        self.renderer_spin.set_alignment(0.5, 0.5)

        # create first column
        column_name = Gtk.TreeViewColumn("Параметр")
        column_name.set_alignment(0.5)
        column_name.set_expand(True)
        column_name.pack_start(renderer_text, True)
        column_name.add_attribute(renderer_text, "text", 0)
        # append first column
        self.append_column(column_name)

        # create second column
        column_value = Gtk.TreeViewColumn("Значение")
        column_value.set_alignment(0.5)
        column_value.set_expand(False)
        column_value.pack_start(self.renderer_spin, False)
        column_value.add_attribute(self.renderer_spin, "text", 2)
        # append second column
        self.append_column(column_value)

class AnalysisSettingsDialog(BaseDialog):
    def __init__(self, parent):
        BaseDialog.__init__(self, "Настройки анализа", parent)

        mainBox = self.get_content_area()

        # fill page list with created pages
        pages = []
        pages.append((BaseSettingsPage(parent.errorSettingsStore), "video_loss", "Пропадание видео"))
        pages.append((Gtk.Label(label='2'), "audio_loss", "Пропадание аудио"))
        pages.append((Gtk.Label(label='3'), "black_frame", "Чёрный кадр"))
        pages.append((Gtk.Label(label='4'), "freeze", '"Заморозка" видео"'))
        pages.append((Gtk.Label(label='5'), "blockiness", "Блочность"))
        pages.append((Gtk.Label(label='6'), "overload", '"Перегрузка" звука'))
        pages.append((Gtk.Label(label='7'), "silence", "Тишина"))

        # create stack
        self.stack = Gtk.Stack(halign=Gtk.Align.FILL, hexpand=True)
        #self.stack.set_transition_duration(200)
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_UP_DOWN)
        # add callback when page is switched
        #self.stack.connect("notify::visible-child", self.on_page_switched)
        #add pages to stack
        for page in pages:
            self.stack.add_titled(page[0], page[1], page[2])

        # create stack sidebar
        self.stackSidebar = Gtk.StackSidebar(vexpand=True, hexpand=False, halign=Gtk.Align.START)
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

    def on_draw(self, widget, cr):
        rect = widget.get_allocation()
        cr.rectangle(0, 0, rect.width, rect.height)
        cr.set_source_rgb(1, 1, 1)
        cr.fill()
