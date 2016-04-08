from statistics import mean

from gi.repository import Gtk

from Control.ErrorDetector.StatusTypes import STYPES


# class for viewing current program status
# (such as artifacts/loudndess) in a table
class ProgramTable(Gtk.TreeView):

    def __init__(self):
        Gtk.TreeView.__init__(self, hexpand=True, halign=Gtk.Align.FILL,
                              vexpand=False, valign=Gtk.Align.END)

        # prog table column names
        self.heading_labels = [
            "№", "Программа",
            "Нет видео", "Чёрный кадр", "Заморозка", "Блочность",
            "Нет аудио", "Тихо", "Громко", "Громкость"]

        # associates status code with a cell color
        self.clrs = {STYPES['norm']: '#80FF80', STYPES['warn']: '#FFFF80',
                     STYPES['err']: '#FF7878', STYPES['unkn']: '#CCCCCC'}

        # associates status code with a cell text (temporary)
        self.stattxt = {STYPES['unkn']: "", STYPES['norm']: "",
                        STYPES['warn']: "Опасно", STYPES['err']: "Брак"}

        # associates parameter name with a cell num
        self.param_cell_id = {'vloss': 4, 'black': 6, 'freeze': 8,
                              'blocky': 10, 'aloss': 12, 'silence': 14,
                              'loudness': 16}

        # remove any selections
        sel = self.get_selection()
        sel.set_mode(Gtk.SelectionMode.NONE)

        # table should be with horizontal and vertical lines that divide cells
        self.set_grid_lines(Gtk.TreeViewGridLines.BOTH)

        # attaching list store to tree view widget
        self.set_model(Gtk.ListStore(int, str,        # n
                                     str, str,        # prog name
                                     str, str,        # video loss
                                     str, str,        # black frame
                                     str, str,        # freeze
                                     str, str,        # blockiness
                                     str, str,        # audio loss
                                     str, str,        # silence
                                     str, str,        # loudness
                                     int, str,        # lufs
                                     int,             # stream id
                                     int,             # prog id
                                     int,             # video pid
                                     int))            # audio pid

        # constructing columns and cells of the table
        for i in range(0, 20, 2):

            # i - index of cell in list store describing cell text
            # color - index of cell in list store describing background color
            color = i + 1

            # 3rd column is a progress bar for lufs levels
            if i == 18:
                renderer = Gtk.CellRendererProgress()

                column = Gtk.TreeViewColumn(self.heading_labels[int(i/2)],
                                            renderer,
                                            value=i,
                                            text=i+1)

            # other colums are text labels
            else:
                renderer = Gtk.CellRendererText()
                renderer.set_alignment(0.5, 0.5)
                # setting parameters for artifact columns
                if 2 < i < 18:
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

    def add_rows(self, prog_list):
        store = self.get_model()
        store.clear()

        prog_cnt = 0
        for stream in prog_list:
            stream_id = stream[0]
            for prog in stream[1]:
                prog_cnt += 1
                prog_name = prog[1]
                prog_id = int(prog[0])

                video_pid = None
                audio_pid = None
                for pid in prog[4]:
                    if pid[2].split('-')[0] == 'video':
                        video_pid = int(pid[0])
                    elif pid[2].split('-')[0] == 'audio':
                        audio_pid = int(pid[0])

                def_cells = ["", self.clrs[STYPES['unkn']]]

                store_data = [prog_cnt, '#FFFFFF', prog_name, '#FFFFFF'] + \
                             def_cells*7 + \
                             [0, '0', stream_id, prog_id, video_pid, audio_pid]

                store.append(store_data)

    def update_table_cells(self, row, data):
        for k, v in data.items():
            row[self.param_cell_id[k]] = self.stattxt[v]
            row[self.param_cell_id[k] + 1] = self.clrs[v]

    def update(self, results):
        for result in results:
            # result - video data header, audio data header, error flags
            predicate = lambda x: ([x[20], x[21], x[22]] == result[0]) and \
                                  ([x[20], x[21], x[23]] == result[1])

            match = list(filter(predicate, self.get_model()))
            if not match is False:
                row = match[0]
                self.update_table_cells(row, result[2])

    def update_lufs(self, lufs):
        arow = list(filter(lambda x: [x[20], x[21], x[23]] == lufs[0],
                           self.get_model()))[0]

        # lufs[1][1] - short term loudness
        # check if list is empty
        if not lufs[1][1] is False:
            data = mean(lufs[1][1])
            # limit value to range
            data = max(min(-5, data), -59)
            arow[18] = int(((data - (-59)) / 54)*100)
            arow[19] = '%.2f LUFS' % data

