import json

from gi.repository import Gtk


class StreamProgTreeModel(Gtk.TreeStore):
    def __init__(self):
        # icon name,
        # prog name,
        # is analyzed,
        # is partly choosen,
        # stream id,
        # string describing row
        Gtk.TreeStore.__init__(self, str, str, bool, bool, int, str)

        self.TREE_ICONS = {"ts": "view-grid-symbolic",
                           "program": "applications-multimedia",
                           "video": "video-x-generic",
                           "audio": "audio-x-generic"}

    def clear_model(self):
        self.clear()

    def get_selected_prog_params(self):

        # get root iter
        piter = self.get_iter_first()
        citer = self.iter_children(piter)

        streams_params_list = []
        # iteration
        while piter is not None:
            # get stream id
            stream_id = self[piter][4]
            stream_params = json.loads(self[piter][5])

            # iterating over stream programs
            progs_param_list = []
            while citer is not None:

                # if program is selected
                if (self[citer][2] is True) or (self[citer][3] is True):
                    prog_params = json.loads(self[citer][5])

                    piditer = self.iter_children(citer)

                    # iterate over program pids
                    pids_params_list = []
                    while piditer is not None:
                        # if pid is selected
                        if self[piditer][2] is True:
                            pids_params_list.append(
                                json.loads(self[piditer][5]))
                        piditer = self.iter_next(piditer)

                    # replacing pids info
                    prog_params[4] = pids_params_list
                    progs_param_list.append(prog_params)

                citer = self.iter_next(citer)

            # replacing prog info
            stream_params[1] = progs_param_list
            streams_params_list.append(stream_params)
            # get next stream iter
            piter = self.iter_next(piter)
            citer = self.iter_children(piter)

        return streams_params_list

    # show new program list received from backend
    def update_stream_info(self, progList):

        stream_id = progList[0]

        rootIter = self.get_iter_first()
        if rootIter is not None:
            while rootIter is not None:
                if self[rootIter][4] == stream_id:
                    self.remove(rootIter)
                    break
                rootIter = self.iter_next(rootIter)

        # fill the model
        stream_info = progList[1]
        if len(stream_info) != 0:
            self.update_stream_in_model(progList)

        # return program number
        return len(stream_info)

    # apply new list of streams
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
            self.update_stream_in_model(progList)

    def update_stream_in_model(self, progList):
        piter = self.append(None, [self.TREE_ICONS['ts'],
                                   "Поток №" + str(progList[0] + 1),
                                   False,
                                   False,
                                   progList[0],
                                   json.dumps(progList)])

        for prog in progList[1]:
            citer = self.append(piter, [self.TREE_ICONS['program'],
                                        prog[2],
                                        False,
                                        False,
                                        prog[3],
                                        json.dumps(prog)])
            pids = prog[4]

            for pid in pids:
                self.append(citer, [self.TREE_ICONS[pid[1].split('-')[0]],
                                    "PID " + pid[0] + ", " + pid[1],
                                    False,
                                    False,
                                    prog[0],
                                    json.dumps(pid)])

    # extract stream ids from model
    def get_stream_ids(self):
        stream_ids = []

        for rows in self:
            stream_ids.append(row[4])

        return stream_ids
