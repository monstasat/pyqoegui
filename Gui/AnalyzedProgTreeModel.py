import json
from gi.repository import Gtk

class AnalyzedProgTreeModel(Gtk.TreeStore):
    def __init__(self):
        # icon name, prog name, is selected, is partly selected, stream id (or type if prog), type, prog info
        Gtk.TreeStore.__init__(self, str, str, bool, bool, int, str)

        self.TREE_ICONS = {
                3 : "applications-multimedia",
                1 : "video-x-generic",
                2 : "audio-x-generic",
                'video' : "video-x-generic",
                'audio' : "audio-x-generic"}

    def clear_all_programs(self):
        self.clear()

    def get_selected_programs(self):
        pass

    # show new program list received from backend
    def add_new_programs(self, progList):
        self.clear_all_programs()
        # fill the model
        streams = []
        for prog in progList:
            # get prog params
            stream = prog[0]
            for id in streams:
                if id == stream:
                    break
            else:
                streams.append(stream)
        for stream in streams:
            piter = self.append(None, ["view-grid-symbolic", "Поток №" + str(stream + 1), False, False, stream, ""])
            for prog in progList:
                if stream == prog[0]:
                    citer = self.append(piter, [self.TREE_ICONS[prog[3]], prog[2], False, False, prog[3], json.dumps(prog) ] )
                pids = prog[4]
                for pid in pids:
                    self.append(citer, [self.TREE_ICONS[pid[1].split('-')[0]], "PID " + pid[0] + ", " + pid[1] , False, False, prog[0], json.dumps(pid)])

        print(streams)
