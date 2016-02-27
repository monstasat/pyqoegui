from gi.repository import Gtk

class PlotProgramTreeView(Gtk.TreeView):
    def __init__(self, store):
        Gtk.TreeView.__init__(self)

        self.set_grid_lines(Gtk.TreeViewGridLines.BOTH)
        self.set_show_expanders(True)
        self.set_enable_tree_lines(True)
        sel = self.get_selection()
        sel.set_mode(Gtk.SelectionMode.NONE)

        # what programs to display?
        self.filter_type = 0

        # remember store
        self.store = store

        # creating store filter
        self.store_filter = self.store.filter_new()
        # setting the filter function
        self.store_filter.set_visible_func(self.pid_filter_func)

        # set model for tree view
        self.set_model(self.store_filter)

        # the cellrenderer for the first column - icon
        renderer_icon = Gtk.CellRendererPixbuf()
        renderer_icon.set_alignment(0.5, 0.5)

        # the cellrenderer for the first column - text
        renderer_text = Gtk.CellRendererText()

        # the cellrenderer for the second column - toogle
        self.renderer_check = Gtk.CellRendererToggle()
        self.renderer_check.set_alignment(0.5, 0.5)
        self.renderer_check.connect('toggled', self.on_toggled)

        # create first column
        column_prog = Gtk.TreeViewColumn("Анализируемые программы")
        column_prog.set_alignment(0.5)
        column_prog.set_expand(True)
        column_prog.pack_start(renderer_icon, False)
        column_prog.pack_start(renderer_text, True)
        column_prog.add_attribute(renderer_icon, "icon-name", 0)
        column_prog.add_attribute(renderer_text, "text", 1)
        # append first column
        self.append_column(column_prog)

        # create second column
        column_check = Gtk.TreeViewColumn("Отображать?")
        column_check.set_alignment(0.5)
        column_check.set_expand(False)
        column_check.pack_start(self.renderer_check, False)
        column_check.add_attribute(self.renderer_check, "active", 2)
        column_check.add_attribute(self.renderer_check, "inconsistent", 3)
        # append second column
        self.append_column(column_check)

    def on_toggled(self, widget, path):
        # the boolean value of the selected row
        current_value = self.store_filter[path][2]
        # change the boolean value of the selected row in the model
        self.store_filter[path][2] = not current_value
        # new current value!
        current_value = not current_value

        # if length of the path is 1 (that is, if we are selecting a stream)
        if len(path) == 1:
            # get the iter associated with the stream path
            streamIter = self.store_filter.get_iter(path)
            # inconsistent state is not valid when selecting a stream
            self.store_filter[streamIter][3] = False
            # get the iter associated with its first child (program)
            progIter = self.store_filter.iter_children(streamIter)
            # while there are programs, change the state of their boolean value
            while progIter is not None:
                self.store_filter[progIter][2] = current_value
                # inconsistent state is not valid when selecting a stream
                self.store_filter[progIter][3] = False
                progIter = self.store_filter.iter_next(progIter)

        #if length of the path is 3 (that is, if we are selecting a program)
        elif len(path) == 3:
            # get the iter associated with the program path
            progIter = self.store_filter.get_iter(path)

            #set stream check button state
            self.set_check_parent_button_state(progIter)

    # call to set parent check button state (if pid - set program state, if program - set stream state)
    def set_check_parent_button_state(self, citer):
        # set parent check button state dependent on children choosen
        # if all children are choosen - parent is choosen
        # if some children are choosen - parent is in inconsistent state
        # if no children are choosen - parent is also not choosen

        piter = self.store_filter.iter_parent(citer)

        citer = self.store_filter.iter_children(piter)
        # check if all the children are selected, or only some are selected
        all_selected = True
        some_selected = False
        while citer is not None:
            # if at least one program is not selected, set all_selected flag to false
            if self.store_filter[citer][2] == False:
                all_selected = False
            # if at least one program is selected, set some_selected flag to true
            else:
                some_selected = True
            citer = self.store_filter.iter_next(citer)

        # if all programs are selected, the stream as well is selected
        # if some programs are selected , the stream is partly selected (inconsistent)
        # if no programs selected, the stream as well is not selected
        self.store_filter[piter][2] = all_selected
        if all_selected is False:
            self.store_filter[piter][3] = some_selected

    def unselect_all(self):
        piter = self.store_filter.get_iter_first()
        while piter is not None:
            self.store_filter[piter][2] = False
            self.store_filter[piter][3] = False
            citer = self.store_filter.iter_children(piter)
            while citer is not None:
                self.store_filter[citer][2] = False
                self.store_filter[citer][3] = False
                citer = self.store_filter.iter_next(citer)
            piter = self.store_filter.iter_next(piter)
    def set_filter_type(self, type):
        self.filter_type = type

    # filtering function for tree view
    def pid_filter_func(self, model, iter, data):
        # hides pids from tree view
        if model.iter_children(iter) is None:
            return False
        # hide progs of type that is not supported by selected graph
        elif len(str(model.get_path(iter))) == 3 and ((model[iter][4] & self.filter_type) is 0):
            return False
        else:
            return True
