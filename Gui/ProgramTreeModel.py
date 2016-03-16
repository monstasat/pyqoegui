import json

from gi.repository import Gtk


class ProgramTreeModel(Gtk.TreeStore):
    def __init__(self, prog_list=[]):
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

        self.add_all_streams(prog_list)

    def unselect_all(self):
        piter = self.get_iter_first()
        while piter is not None:
            self[piter][2] = False
            self[piter][3] = False
            citer = self.iter_children(piter)
            while citer is not None:
                self[citer][2] = False
                self[citer][3] = False
                citer = self.iter_next(citer)
            piter = self.iter_next(piter)

    def clear_model(self):
        self.clear()

    # get full list of all streams from model
    # no matter selected or not
    def get_list(self):

        streams_params_list = []
        # iteration
        for row in self:
            stream_info = json.loads(row[5])
            streams_params_list.append(stream_info)

        return streams_params_list

    # get currently selected list,
    # including streams, programs, pids
    def get_selected_list(self):

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

    # apply new list of streams to model
    def add_all_streams(self, prog_list):

        self.clear_model()

        for stream in prog_list:
            if len(stream[1]) > 0:
                self.update_stream_info(stream)

    # append new stream to model
    def update_stream_info(self, prog_list):
        piter = self.append(None, [self.TREE_ICONS['ts'],
                                   "Поток №" + str(prog_list[0] + 1),
                                   False,
                                   False,
                                   prog_list[0],
                                   json.dumps(prog_list)])

        for prog in prog_list[1]:
            citer = self.append(piter, [self.TREE_ICONS['program'],
                                        prog[1],
                                        False,
                                        False,
                                        prog_list[0],
                                        json.dumps(prog)])
            pids = prog[4]

            for pid in pids:
                pid_type = pid[2].split('-')[0]
                if (pid_type == 'video') or (pid_type == 'audio'):
                    pid_str = "PID " + str(pid[0]) + ", " + str(pid[2])
                    self.append(citer, [self.TREE_ICONS[pid_type],
                                        pid_str,
                                        False,
                                        False,
                                        prog_list[0],
                                        json.dumps(pid)])

