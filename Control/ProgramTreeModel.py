import json

from gi.repository import Gtk


class ProgramTreeModel(Gtk.TreeStore):
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

    # extract program ids and names from prog list
    def get_progs_in_gui_format(self):
        # get prog list from model
        progList = self.get_list()
        #print("\n" + str(progList))
        guiProgInfo = []

        for stream in progList:
            stream_id = stream[0]
            progs = stream[1]
            for prog in progs:
                prog_info = [stream_id, prog[0], prog[1]]
                pids = prog[4]
                pids_info = []
                prog_type = 0
                for pid in pids:
                    type = pid[2]
                    if type.split('-')[0] == 'video':
                        prog_type = prog_type | 1
                    elif type.split('-')[0] == 'audio':
                        prog_type = prog_type | 2
                    pids_info.append([pid[0], type])
                prog_info.append(prog_type)
                prog_info.append(pids_info)
                guiProgInfo.append(prog_info)

        return guiProgInfo

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

    # add or replace stream in model (stream info is list)
    def add_one_stream(self, progList):

        stream_id = progList[0]

        # check if there is a stream in a model with equal stream id
        # if yes, replace it
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
            self.update_stream_info(progList)

        # return program number
        return len(stream_info)

    # apply new list of streams to model
    def add_all_streams(self, progList):

        self.clear_model()

        for stream in progList:
            self.update_stream_info(stream)

    # append new stream to model
    def update_stream_info(self, progList):
        piter = self.append(None, [self.TREE_ICONS['ts'],
                                   "Поток №" + str(progList[0] + 1),
                                   False,
                                   False,
                                   progList[0],
                                   json.dumps(progList)])

        for prog in progList[1]:
            citer = self.append(piter, [self.TREE_ICONS['program'],
                                        prog[1],
                                        False,
                                        False,
                                        progList[0],
                                        json.dumps(prog)])
            pids = prog[4]

            for pid in pids:
                self.append(citer, [self.TREE_ICONS[pid[2].split('-')[0]],
                                    "PID " + pid[0] + ", " + pid[2],
                                    False,
                                    False,
                                    progList[0],
                                    json.dumps(pid)])

    # extract stream ids from model
    def get_stream_ids(self):
        stream_ids = []
        # iterating over stream rows
        for row in self:
            stream_ids.append(row[4])

        return stream_ids

    # compare two prog lists and make new list with only equal programs
    def get_compared_list(self, gsProgList):
        # get prog list from model
        progList = self.get_list()
        # new prog list after comparison
        compared_list = []
        # append stream id
        compared_list.append(gsProgList[0])

        compared_progs = []
        # iterating over streams in saved prog list
        for stream in progList:
            # in case if received stream exists in saved prog list
            if stream[0] == gsProgList[0]:
                progs = stream[1]

                for gsProg in gsProgList[1]:
                    compared_prog = []

                    progNum = len(progs)
                    # search for the same program
                    i = 0

                    while progNum != 0:
                        # if found selected program in received list
                        if gsProg[0] == progs[i][0]:

                            pids = progs[i][4]
                            compared_pids = []
                            for gsPid in gsProg[4]:

                                pidsNum = len(pids)
                                # search for the same pid
                                j = 0
                                while pidsNum != 0:
                                    # if found selected pid in received list
                                    if (gsPid[0] == pids[j][0]) and \
                                            (gsPid[2] == pids[j][2]):
                                        # same pid found!
                                        compared_pids.append(pids[j])
                                        break
                                    pidsNum = pidsNum - 1
                                    j = j + 1

                            # if equivalent program was found, exit from while
                            compared_prog.append(progs[i][0])
                            compared_prog.append(progs[i][1])
                            compared_prog.append(progs[i][2])
                            compared_prog.append(progs[i][3])
                            compared_prog.append(compared_pids)
                            compared_progs.append(compared_prog)
                            break
                        progNum = progNum - 1
                        i = i + 1

                # exit from for loop because we've found the stream
                break
        compared_list.append(compared_progs)

        return compared_list
