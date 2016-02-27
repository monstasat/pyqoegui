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

    def clear_all_programs(self):
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
    def show_prog_list(self, progList):

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
            piter = self.append(None, [self.TREE_ICONS["ts"],
                                       "Поток №"+str(stream_id + 1),
                                       False,
                                       False,
                                       stream_id,
                                       json.dumps(progList)])
        for prog in stream_info:

            # get prog params
            # prog[0] - progID,
            # prog[1] - prog name,
            # prog[2] - prov_name,
            # prog[3] - pids num
            pidsNum = int(prog[3])

            ppiter = self.append(piter, [self.TREE_ICONS["program"],
                                         (prog[1] + " (" + prog[2] + ")"),
                                         False,
                                         False,
                                         stream_id,
                                         json.dumps(prog)])

            pids_info = prog[4]
            for pid in pids_info:
                # get pid params
                # pid[0] - pid, pid[1] - pid type, pid[2] - codec type string
                strPidType = pid[2].split('-')[0]

                self.append(ppiter, [self.TREE_ICONS[strPidType],
                                     "PID " + pid[0] + ", " + pid[2],
                                     False,
                                     False,
                                     stream_id,
                                     json.dumps(pid)])

        # return program number
        return len(stream_info)

