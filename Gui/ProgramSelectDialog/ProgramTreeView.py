from gi.repository import Gtk


# Base class for prog list display
# Child class should add attributes for second column
class ProgramTreeView(Gtk.TreeView):

    def __init__(self, store):

        self.PROG_PARAMS = {"number": 0,
                            "prog_name": 1,
                            "prov_name": 2,
                            "pids_num": 3}

        # dividers for string with program parameters
        self.STREAM_DIVIDER = ':$:'
        self.PROG_DIVIDER = ':*:'
        self.PARAM_DIVIDER = '^:'

        Gtk.TreeView.__init__(self)
        self.set_hexpand(True)
        self.set_vexpand(True)
        self.set_halign(Gtk.Align.FILL)
        self.set_valign(Gtk.Align.FILL)
        self.set_grid_lines(Gtk.TreeViewGridLines.BOTH)
        self.set_show_expanders(True)
        self.set_enable_tree_lines(True)
        sel = self.get_selection()
        sel.set_mode(Gtk.SelectionMode.NONE)

        # set the model
        self.set_model(store)
        # remember the model
        self.store = store

        # the cellrenderer for the first column - icon
        self.renderer_icon = Gtk.CellRendererPixbuf()
        self.renderer_icon.set_alignment(0.5, 0.5)

        # the cellrenderer for the first column - text
        self.renderer_text = Gtk.CellRendererText()

        # the cellrenderer for the second column - toogle
        self.renderer_check = Gtk.CellRendererToggle()
        self.renderer_check.set_alignment(0.5, 0.5)
        self.renderer_check.connect('toggled', self.on_toggled)

        # create first column
        self.column_prog = Gtk.TreeViewColumn("Найденные программы")
        self.column_prog.set_alignment(0.5)
        self.column_prog.set_expand(True)
        self.column_prog.pack_start(self.renderer_icon, False)
        self.column_prog.pack_start(self.renderer_text, True)
        self.column_prog.add_attribute(self.renderer_icon, "icon-name", 0)
        self.column_prog.add_attribute(self.renderer_text, "text", 1)

        # append first column
        self.append_column(self.column_prog)

        # create second column
        self.column_check = Gtk.TreeViewColumn("Анализировать?")
        self.column_check.set_alignment(0.5)
        self.column_check.set_expand(False)
        self.column_check.pack_start(self.renderer_check, False)
        self.column_check.add_attribute(self.renderer_check, "active", 2)
        self.column_check.add_attribute(self.renderer_check, "inconsistent", 3)
        # append second column
        self.append_column(self.column_check)

        self.show_all()

    def on_store_changed(self):
        pass

    def on_toggled(self, widget, path):
        # the boolean value of the selected row
        current_value = self.store[path][2]
        # change the boolean value of the selected row in the model
        self.store[path][2] = not current_value
        self.store[path][3] = False
        # new current value!
        current_value = not current_value

        # if length of the path is 1
        # (that is, if we are selecting a stream)
        if len(path) == 1:
            # get the iter associated with the stream path
            streamIter = self.store.get_iter(path)
            # get the iter associated with its first child (program)
            progIter = self.store.iter_children(streamIter)
            # while there are programs, change the state of their boolean value
            while progIter is not None:
                self.store[progIter][2] = current_value
                # inconsistent state is not applicable
                # when selecting/deselecting a stream
                self.store[progIter][3] = False
                pidIter = self.store.iter_children(progIter)
                # if new value is True (program is selected),
                # then select default pids
                if current_value is True:
                    self.set_default_pids(pidIter)
                # if new value is False (program is unselected),
                # the unselect all program pids
                else:
                    while pidIter is not None:
                        self.store[pidIter][2] = current_value
                        pidIter = self.store.iter_next(pidIter)
                progIter = self.store.iter_next(progIter)

        # if length of the path is 3 (that is, if we are selecting a program)
        elif len(path) == 3:
            # get the iter associated with the program path
            progIter = self.store.get_iter(path)
            # get the iter associated with its first child (pid)
            pidIter = self.store.iter_children(progIter)
            # if new value is True (program is selected),
            # then select default pids
            if current_value is True:
                self.set_default_pids(pidIter)
            # if new value is False (program is unselected),
            # the unselect all program pids
            else:
                while pidIter is not None:
                    self.store[pidIter][2] = current_value
                    pidIter = self.store.iter_next(pidIter)

            # get the first pid of the program
            progIter = self.store.get_iter(path)
            # set stream check button state
            self.set_check_parent_button_state(progIter)

        # in other cases we are selecting a pid
        else:
            # get the iter associated with the path
            pidIter = self.store.get_iter(path)
            # check if other pid of the same type is selected
            # and uncheck it if yes
            self.check_if_other_pids_selected(pidIter)
            # set program check button state
            self.set_check_parent_button_state(pidIter)
            # set stream check button state
            self.set_check_parent_button_state(self.store.iter_parent(pidIter))

    # call to check if other pid of the same type was selected.
    # If was, unselect it
    def check_if_other_pids_selected(self, pidIter):
        # get the first pid of the program
        progIter = self.store.iter_parent(pidIter)
        firstPidIter = self.store.iter_children(progIter)

        # marking current pid is unselected and receive other pid status
        current_value = self.store[pidIter][2]
        self.store[pidIter][2] = False
        pid_status = self.scan_pids(firstPidIter)
        self.store[pidIter][2] = current_value

        # determine pid type
        pidType = '0'if \
            (self.store[pidIter][0] == self.store.TREE_ICONS['video']) else '1'

        # if we select the pid, then we need to check
        # if other pid of the same type is selected
        if current_value is True:
            # is some other pid of same type is selected?
            if pid_status[2 + int(pidType)] is True:
                self.store[pid_status[4 + int(pidType)]][2] = False

    # call to set parent check button state
    # (if pid - set program state, if program - set stream state)
    def set_check_parent_button_state(self, citer):
        # set parent check button state dependent on children choosen
        # if all children are choosen - parent is choosen
        # if some children are choosen - parent is in inconsistent state
        # if no children are choosen - parent is also not choosen

        piter = self.store.iter_parent(citer)

        citer = self.store.iter_children(piter)
        # check if all the children are selected, or only some are selected
        all_selected = True
        some_selected = False
        while citer is not None:
            if self.store[citer][2] == False:
                all_selected = False
                # if child is not selected,
                # but its child's children are selected, set some_selected flag
                if self.store[citer][3] == True:
                    some_selected = True
            else:
                some_selected = True
            citer = self.store.iter_next(citer)

        # if we are analyzing pid level
        # it is not necessary that all pids are selected
        # all selected flag should be True if
        # video pid is present and it is selected
        # and
        # audio pid is present and it is selected
        citer = self.store.iter_children(piter)
        path = self.store.get_path(citer)
        if len(str(path)) == 5:
            pids_ok = False
            pid_status = self.scan_pids(citer)
            # 0 - video pid found,
            # 2 - video pid selected;
            # 1 - audio pid found,
            # 3 - audio pid selected
            if (not (pid_status[0] ^ pid_status[2])) and \
                    (not (pid_status[1] ^ pid_status[3])):
                pids_ok = True
            all_selected = pids_ok

        # if all programs are selected,
        # the stream as well is selected
        # if some programs are selected ,
        # the stream is partly selected (inconsistent)
        # if no programs selected,
        # the stream as well is not selected
        self.store[piter][2] = all_selected
        if all_selected is False:
            self.store[piter][3] = some_selected
            # if selected at least one pid from a program,
            # mark stream as partly selected
            stream = self.store.iter_parent(piter)
            if stream is not None:
                self.store[stream][3] = some_selected

    # set default pids if program state changes to 'choosen'
    def set_default_pids(self, pidIter):
        # 0 - video_found,
        # 1 - audio_found,
        # 2 - video_selected,
        # 3 - audio_selected
        pid_status = self.scan_pids(pidIter)

        # if no selected video pid was found and video pid present,
        # set default pid
        if (pid_status[2] is False) and (pid_status[0] is True):
            self.set_default_pid(pidIter, 'video')
        if (pid_status[3] is False) and (pid_status[1] is True):
            self.set_default_pid(pidIter, 'audio')

    # sets the default pid
    def set_default_pid(self, pidIter, pidType):
        pid_selected = False
        while (pid_selected is False) and (pidIter is not None):
            if self.store[pidIter][0] == self.store.TREE_ICONS[pidType]:
                self.store[pidIter][2] = True
                pid_selected = True
            pidIter = self.store.iter_next(pidIter)

    # scan pids for video/audio pids, and check if some are selected
    def scan_pids(self, pidIter):

        video_found = False
        audio_found = False
        video_selected = False
        audio_selected = False
        selected_video_pid = None
        selected_audio_pid = None

        # scan all program pids
        while pidIter is not None:
            # if pid has video type
            if self.store[pidIter][0] == self.store.TREE_ICONS['video']:
                video_found = True
                # if pid is selected
                if self.store[pidIter][2] == True:
                    video_selected = True
                    selected_video_pid = pidIter
            # if pid has audio type
            elif self.store[pidIter][0] == self.store.TREE_ICONS['audio']:
                audio_found = True
                # if pid is selected
                if self.store[pidIter][2] == True:
                    audio_selected = True
                    selected_audio_pid = pidIter

            pidIter = self.store.iter_next(pidIter)

        return [video_found,
                audio_found,
                video_selected,
                audio_selected,
                selected_video_pid,
                selected_audio_pid]

