from gi.repository import Gtk

from Gui.CurrentResultsPage.RendererGrid import RendererGrid
from Gui.CurrentResultsPage.ProgramTable import ProgramTable
from Gui.Placeholder import Placeholder
from Gui import Spacing
from Control import CustomMessages


class CurrentResultsPage(Gtk.Box):
    def __init__(self, parent):
        Gtk.Grid.__init__(self, orientation=Gtk.Orientation.VERTICAL,
                          spacing=Spacing.ROW_SPACING)

        # main window
        self.mainWnd = parent

        # creating renderers
        self.rend = RendererGrid()
        self.rend.connect(CustomMessages.VOLUME_CHANGED,
                          self.on_volume_changed)

        # creating renderers overlay
        overlay = Gtk.Overlay(valign=Gtk.Align.FILL,
                              hexpand=True, vexpand=True)
        overlay.add(self.rend)
        self.holder = Placeholder("face-smirk-symbolic",
                                  'Нет анализируемых программ :('
                                  '\nНо их можно добавить в меню '
                                  '"Выбор программ для анализа"!',
                                  72)
        overlay.add_overlay(self.holder)

        # creating prog table
        self.prgtbl = ProgramTable()
        # creating prog table revealer
        self.tableRevealer = Gtk.Revealer(
                    reveal_child=True,
                    valign=Gtk.Align.END,
                    transition_type=Gtk.RevealerTransitionType.SLIDE_UP)
        self.tableRevealer.add(self.prgtbl)

        self.add(overlay)
        self.add(self.tableRevealer)

    # when user changes volume of renderer
    def on_volume_changed(self, wnd, stream_id, prog_id, pid, value):
        self.mainWnd.emit(CustomMessages.VOLUME_CHANGED,
                          stream_id, prog_id, pid, value)

    def on_prog_list_changed(self, prog_list):
        prog_num = 0
        for stream in prog_list:
            prog_num += len(stream[1])

        if prog_num == 0:
            self.holder.show()
            self.prgtbl.hide()
        else:
            self.holder.hide()
            self.prgtbl.show_all()

        self.prgtbl.add_rows(prog_list)
        self.rend.draw_renderers(prog_list)

    def get_prog_table_visible(self):
        return self.prgtbl.get_visible()

    def hide_renderer_and_table(self):
        # if table does not have any rows, hide it
        if len(self.prgtbl.get_model()) == 0:
            self.prgtbl.hide()
        # if rows added, hide renderers overlay
        else:
            self.holder.hide()

    def get_table_revealer(self):
        return self.tableRevealer

    def mute_all_renderers(self):
        map(lambda x: x.set_volume(0), self.rend.rend_arr)

