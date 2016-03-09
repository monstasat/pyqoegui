from gi.repository import Gtk


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
        self.clrs = {'1': '#80FF80',
                     '2': '#FFFF80',
                     '3': '#FF7878',
                     '0': '#CCCCCC'}

        # associates status code with a cell text (temporary)
        self.stattxt = {'1': "", '2': "Опасно", '3': "Брак"}

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
                                   str, str)        # loudness

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
            progName = guiProgInfo[i][2]
            treeiter = store.append(
                        [i+1, '#FFFFFF',                        # prog num
                         progName, '#FFFFFF',                   # prog name
                         '%g' % (0.0), '#FFFFFF',               # lufs level
                         self.stattxt["1"], self.clrs['0'],     # video loss
                         self.stattxt["1"], self.clrs['0'],     # black frame
                         self.stattxt["1"], self.clrs['0'],     # freeze
                         self.stattxt["1"], self.clrs['0'],     # blockiness
                         self.stattxt["1"], self.clrs['0'],     # audio loss
                         self.stattxt["1"], self.clrs['0'],     # silence
                         self.stattxt["1"], self.clrs['0']])    # loudness

    def update(self, results):
        for i, row in enumerate(self.get_model()):
            # video loss
            row[6] = self.stattxt[str(results[i][1][0])]
            row[7] = self.clrs[str(results[i][1][0])]
            # black frame
            row[8] = self.stattxt[str(results[i][1][1])]
            row[9] = self.clrs[str(results[i][1][1])]
            # freeze
            row[10] = self.stattxt[str(results[i][1][2])]
            row[11] = self.clrs[str(results[i][1][2])]
            # blockiness
            row[12] = self.stattxt[str(results[i][1][3])]
            row[13] = self.clrs[str(results[i][1][3])]
            # audio loss
            row[14] = self.stattxt[str(results[i][1][4])]
            row[15] = self.clrs[str(results[i][1][4])]
            # audio silence
            row[16] = self.stattxt[str(results[i][1][5])]
            row[17] = self.clrs[str(results[i][1][5])]
            # audio loudness
            row[18] = self.stattxt[str(results[i][1][6])]
            row[19] = self.clrs[str(results[i][1][6])]


