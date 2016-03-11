import json

from gi.repository import Gtk

from Gui.BaseDialog import BaseDialog
from Gui.PlotPage.PlotProgramTreeView import PlotProgramTreeView
from Gui.PlotPage import PlotTypes


class PlotTypeSelectDialog(BaseDialog):
    def __init__(self, parent):
        BaseDialog.__init__(self, "Настройка параметров графика", parent)

        # remember store
        self.store = parent.analyzed_progs_model

        # get main widget
        mainBox = self.get_content_area()

        # create type select page
        self.type_select_page = Gtk.ListBox(hexpand=True)
        # set selection mode (selection should always be done)
        self.type_select_page.set_property('selection-mode',
                                           Gtk.SelectionMode.BROWSE)
        # add plot types to list
        for type_ in PlotTypes.PLOT_TYPES:
            row = Gtk.Label(label=type_[0])
            self.type_select_page.insert(row, -1)

        # selecting first type
        self.type_select_page.select_row(
            self.type_select_page.get_row_at_index(0))
        self.selected_row = self.get_selected_plot_type()

        # create program select page
        self.prog_select_page = PlotProgramTreeView(self.store)
        self.store.unselect_all()
        self.prog_select_page.renderer_check.connect(
            'toggled',
            self.on_program_selection_changed)

        # fill page list with created pages
        pages = []
        pages.append((self.type_select_page,
                      "type_select",
                      "Тип графика"))
        pages.append((self.prog_select_page,
                      "prog_select",
                      "Программы на графике"))

        # create stack
        self.stack = Gtk.Stack(halign=Gtk.Align.FILL, hexpand=True)
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_UP_DOWN)
        # add callback when page is switched
        self.stack.connect("notify::visible-child", self.on_page_switched)
        # add pages to stack
        for page in pages:
            self.stack.add_titled(page[0], page[1], page[2])

        # create stack sidebar
        self.stackSidebar = Gtk.StackSidebar(
            vexpand=True,
            hexpand=False,
            halign=Gtk.Align.START)
        self.stackSidebar.set_stack(self.stack)
        self.stackSidebar.show()

        # set initial label of 'apply' button
        self.applyBtn.set_property('label', Gtk.STOCK_GO_FORWARD)

        # configure main container orientation
        mainBox.set_orientation(Gtk.Orientation.HORIZONTAL)
        # pack items to main container
        mainBox.pack_start(self.stackSidebar, False, False, 0)
        separator = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        mainBox.pack_start(separator, False, False, 0)
        mainBox.pack_start(self.stack, True, True, 0)

        # connect to store signals
        parent.analyzed_progs_model.connect('row-deleted',
                                            self.on_row_deleted)
        parent.analyzed_progs_model.connect('row-inserted',
                                            self.on_row_inserted)

        self.show_all()
        # set dialog view
        self.set_dialog_view()

    # when suggested button is clicked
    def on_btn_clicked_apply(self, widget):
        visible_page = self.stack.get_visible_child()
        if visible_page is self.type_select_page:
            self.stack.set_visible_child(self.prog_select_page)
        else:
            BaseDialog.on_btn_clicked_apply(self, widget)

    # when user selects/deselects programs from list
    def on_program_selection_changed(self, widget, path):
        # if nothing is selected, deactivate suggested button
        if len(self.get_selected_programs()) is 0:
            self.applyBtn.set_sensitive(False)
        # if smth is selected, activate button
        else:
            self.applyBtn.set_sensitive(True)

    # when dialog page is switched (to plot type select or progs select)
    def on_page_switched(self, stack, gparam):
        # get visible page
        visible_page = self.stack.get_visible_child()

        # if type selection page is visible now
        if visible_page is self.type_select_page:
            # change text on suggested button
            self.applyBtn.set_property('label', Gtk.STOCK_GO_FORWARD)
            self.applyBtn.set_sensitive(True)
        # if prog selection type is visible now
        else:
            # get currently selected plot type
            row = self.get_selected_plot_type()
            # if currently selected type is different from previous selection
            if row != self.selected_row:
                # clear program selection
                self.store.unselect_all()

            # rewrite previously selected row
            self.selected_row = row

            # get current plot type info
            plot_info = self.get_selected_plot_type_info(row)
            # we need to filter all programs
            # that are not consistent with selected plot type
            self.prog_select_page.set_filter_type(plot_info[3])
            self.prog_select_page.store_filter.refilter()
            # restore dialog view
            self.set_dialog_view()

            # change text on suggested button
            self.applyBtn.set_property('label', Gtk.STOCK_APPLY)
            # if no programs selected, deactivate suggested button
            if len(self.get_selected_programs()) is 0:
                self.applyBtn.set_sensitive(False)
            else:
                self.applyBtn.set_sensitive(True)

    # get information about selected plot type
    def get_selected_plot_type_info(self, row):
        return PlotTypes.PLOT_TYPES[row.get_index()]

    # get selected plot type
    def get_selected_plot_type(self):
        return self.type_select_page.get_selected_row()

    # get selected programs
    def get_selected_programs(self):
        piter = self.store.get_iter_first()
        selected_progs = []
        while piter is not None:
            citer = self.store.iter_children(piter)
            while citer is not None:
                if self.store[citer][2] is True:
                    prog_info = json.loads(self.store[citer][5])
                    prog_info.insert(0, self.store[piter][4])
                    selected_progs.append(prog_info)
                citer = self.store.iter_next(citer)
            piter = self.store.iter_next(piter)
        return selected_progs

    # if rows were inserted to model
    def on_row_inserted(self, path, iter, user_data):
        self.set_dialog_view()

    # if rows were deleted from model
    def on_row_deleted(self, path, user_data):
        self.set_dialog_view()

    # decide how to show dialog
    def set_dialog_view(self):
        # if some streams are appended to store, do not show placeholder
        if len(self.prog_select_page.store) > 0:
            # open all program rows
            piter = self.prog_select_page.store.get_iter_first()
            while piter is not None:
                path = self.prog_select_page.store.get_path(piter)
                if self.prog_select_page.row_expanded(path) is False:
                    self.prog_select_page.expand_row(path, False)
                piter = self.prog_select_page.store.iter_next(piter)
            # hide placeholder
            # self.holder.hide()
        else:
            pass
            # self.holder.set_text('Программ не найдено')
            # self.holder.show_all()
        self.prog_select_page.store_filter.refilter()

