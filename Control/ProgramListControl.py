import operator


class ProgramListControl():
    def __init__(self, prog_list=[]):
        self.prog_list = prog_list

    def clear():
        self.prog_list = []

    def get_prog_num(self):
        prog_num = 0
        for stream in self.prog_list:
            prog_num += len(stream[1])
        return prog_num

    def get_pid_num(self):
        pid_num = 0
        for stream in self.prog_list:
            for prog in stream[1]:
                pid_num += len(prog[4])

    # add or replace one stream in a list
    def add_one_stream(self, prog_list):
        stream_id = prog_list[0]

        # check if there is a stream in a model with equal stream id
        # if yes, replace it
        for stream in self.prog_list:
            if stream[0] == stream_id:
                self.prog_list = list(map((
                                    lambda x: x if x != stream else prog_list),
                                    self.prog_list))
                break
        # if no stream with such stream id found,
        else:
            greater = list(filter((lambda x: x[0] > prog_list[0]),
                                  self.prog_list))

            greatest = max(greater,
                           key=operator.itemgetter(0),
                           default=None)

            if greatest is None:
                self.prog_list.append(prog_list)
            else:
                self.prog_list.insert(self.prog_list.index(greatest),
                                      prog_list)

    # FIXME: optimize
    # compare two prog lists and make new list with only equal programs
    def get_compared_list(self, gs_prog_list):
        # new prog list after comparison
        compared_list = []
        # append stream id
        compared_list.append(gs_prog_list[0])

        compared_progs = []
        # iterating over streams in saved prog list
        for stream in self.prog_list:
            # in case if received stream exists in saved prog list
            if stream[0] == gs_prog_list[0]:
                progs = stream[1]

                for gsProg in gs_prog_list[1]:
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

