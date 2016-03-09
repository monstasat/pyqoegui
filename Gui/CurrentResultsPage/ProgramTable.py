from gi.repository import Gtk

from Control.ErrorDetector import StatusTypes as types


# class for viewing current program status
# (such as artifacts/loudndess) in a table
class ProgramTable(Gtk.TreeView):

    def __init__(self):
        Gtk.TreeView.__init__(self)

        # prog table column names
        self.heading_labels = [
            "№", "Программа", "Громкость",
            "Нет видео", "Чёрный кадр", "Заморозка",
            "Блочность", "Нет аудио", "Тихо",
            "Громко"]

        # associates status code with a cell color
        self.clrs = {types.NO_ERR: '#80FF80',
                     types.WARN: '#FFFF80',
                     types.ERR: '#FF7878',
                     types.UNKNOWN: '#CCCCCC'}

        # associates status code with a cell text (temporary)
        self.stattxt = {types.UNKNOWN: "",
                        types.NO_ERR: "",
                        types.WARN: "Опасно",
                        types.ERR: "Брак"}

        # our table should be horizontally expandable
        self.set_hexpand(True)
        self.set_halign(Gtk.Align.FILL)

        # remove any selections
        sel = self.get_selection()
        sel.set_mode(Gtk.SelectionMode.NONE)

        # our table should be attached to the bottom of main app window
        self.set_vexpand(False)
        self.set_valign(Gtk.Align.END)

        # table should be with horizontal and vertical lines that divide cells
        self.set_grid_lines(Gtk.TreeViewGridLines.BOTH)

        # attaching list store to tree view widget
        self.store = Gtk.ListStore(int, str,        # n
                                   str, str,        # prog name
                                   str, str,        # lufs
                                   str, str,        # video loss
                                   str, str,        # black frame
                                   str, str,        # freeze
                                   str, str,        # blockiness
                                   str, str,        # audio loss
                                   str, str,        # silence
                                   str, str,        # loudness
                                   int,             # prog type
                                   int,             # stream id
                                   int,             # prog id
                                   int,             # video pid
                                   int)             # audio pid

        self.set_model(self.store)

        # constructing columns and cells of the table
        for i in range(0, 20, 2):

            # i - index of cell in list store describing cell text
            # color - index of cell in list store describing background color
            color = i + 1

            # 3rd column is a progress bar for lufs levels
            if i == 4:
                renderer = Gtk.CellRendererProgress()
                # renderer.props.inverted = True
                column = Gtk.TreeViewColumn(self.heading_labels[int(i/2)],
                                            renderer,
                                            text=i)

            # other colums are text labels
            else:
                renderer = Gtk.CellRendererText()
                renderer.set_alignment(0.5, 0.5)
                # setting parameters for artifact columns
                if i > 4:
                    # setting column text color - black
                    renderer.set_property("foreground", "black")
                    column = Gtk.TreeViewColumn(self.heading_labels[int(i/2)],
                                                renderer,
                                                text=i,
                                                background=color)

                    # all artifact columns should have the same width
                    column.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
                    column.set_fixed_width(100)
                # setting parameters for the rest columns
                else:
                    column = Gtk.TreeViewColumn(self.heading_labels[int(i/2)],
                                                renderer,
                                                text=i)

            # all columns besides first are expandable
            if i > 0:
                column.set_expand(1)

            # placing column name in the center
            column.set_alignment(0.5)
            # adding column to treeview
            self.append_column(column)

    def add_rows(self, progNum, guiProgInfo):
        store = self.get_model()
        store.clear()

        for i in range(progNum):
            prog_name = guiProgInfo[i][2]
            prog_type = int(guiProgInfo[i][3])
            stream_id = int(guiProgInfo[i][0])
            prog_id = int(guiProgInfo[i][1])

            video_pid = 0
            audio_pid = 0
            for pid in guiProgInfo[i][4]:
                if pid[1].split('-')[0] == 'video':
                    video_pid = int(pid[0])
                elif pid[1].split('-')[0] == 'audio':
                    audio_pid = int(pid[0])

            treeiter = store.append(
                # start of visible part
                # prog num
                [i+1, '#FFFFFF',
                 # prog name
                 prog_name, '#FFFFFF',
                 # lufs level
                 '%g' % (0.0), '#FFFFFF',
                 # video loss
                 self.stattxt[types.UNKNOWN], self.clrs[types.UNKNOWN],
                 # black frame
                 self.stattxt[types.UNKNOWN], self.clrs[types.UNKNOWN],
                 # freeze
                 self.stattxt[types.UNKNOWN], self.clrs[types.UNKNOWN],
                 # blockiness
                 self.stattxt[types.UNKNOWN], self.clrs[types.UNKNOWN],
                 # audio loss
                 self.stattxt[types.UNKNOWN], self.clrs[types.UNKNOWN],
                 # silence
                 self.stattxt[types.UNKNOWN], self.clrs[types.UNKNOWN],
                 # loudness
                 self.stattxt[types.UNKNOWN], self.clrs[types.UNKNOWN],
                 # start of invisible part
                 # prog type
                 prog_type,
                 # stream id
                 stream_id,
                 # prog id
                 prog_id,
                 # video pid
                 video_pid,
                 # audio pid
                 audio_pid])

    def update_table_cell(self, row, index, val):
        # FIXME prog type 1, 2 change to VIDEO, AUDIO (define types somewhere)
        prog_type = 1 if index < 14 else 2
        if (row[20] & prog_type) != 0:
            data = val
        else:
            data = 0
        row[index] = self.stattxt[data]
        row[index + 1] = self.clrs[data]

    def update(self, results, param_type):
        # set values for some variables dependent on content type
        if param_type == 'audio':
            pid_index = 24
            shift = 14
            cell_num = 6
        elif param_type == 'video':
            pid_index = 23
            shift = 6
            cell_num = 8

        # iterating over programs in table
        for row in self.get_model():

            # create data header
            # stream id, prog id, audio pid
            data_header = [row[21], row[22], row[pid_index]]

            for result in results:
                try:
                    index = result.index(data_header)
                except:
                    pass
                else:
                    data = result[1]
                    # iterating over row cells with parameters
                    for i in range(0, cell_num, 2):
                        self.update_table_cell(row,             # row
                                               i+shift,         # row index
                                               data[int(i/2)])  # data

                    # remove current item from result list
                    # as we don't need it anymore
                    results.remove(result)

    def update_video(self, results):
        self.update(results, 'video')

    def update_audio(self, results):
        self.update(results, 'audio')

