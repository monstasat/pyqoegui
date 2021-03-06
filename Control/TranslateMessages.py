class TranslateMessages():
    def __init__(self):
        pass

# PROG LIST
    # convert stream string to stream list
    def get_prog_list(self, stream_string):
        PROG_DIVIDER = ':*:'
        PARAM_DIVIDER = '^:'
        PROG_PARAMS = {"number": 0,
                       "prog_name": 1,
                       "prov_name": 2,
                       "pids_num": 3}

        stream_params = []

        progs = stream_string.split(PROG_DIVIDER)

        # get stream id
        stream_id = int(progs[0])
        stream_params.append(stream_id)

        progs_param_list = []
        for prog in progs[1:]:
            prog_params_list = []
            progParams = prog.split(PARAM_DIVIDER)
            for i in range(4):
                # if prog name and provider name are not determined
                if (i == 1) and (progParams[i] == "(null)"):
                    progParams[i] = "Без имени (PMT PID: " \
                                    + str(progParams[0]) + ")"
                if (i == 2) and (progParams[i] == "(null)"):
                    progParams[i] = "-"
                prog_params_list.append(progParams[i])

            pids_params_list = []
            # iterating over program pids
            for i in range(int(prog_params_list[3])):

                pid_params_list = []
                for j in range(3):
                    pid_params_list.append(progParams[4 + j + 3*i])
                pids_params_list.append(pid_params_list)

            prog_params_list.append(pids_params_list)

            progs_param_list.append(prog_params_list)

        stream_params.append(progs_param_list)
        return stream_params

# VIDEO PARAMETERS
    def get_vparams_list(self, vparams_string):
        PART_DIVIDER = ':*:'
        PARAM_DIVIDER = ':'

        param_list = []

        # split string to stream params and video params
        str_parts = vparams_string.split(PART_DIVIDER)
        # split stream parameters
        stream_params = str_parts[0].split(PARAM_DIVIDER)
        sparams_int = []
        for param in stream_params:
            sparams_int.append(int(param))

        param_list.append(sparams_int)

        video_params_pack = [[], [], [], [], []]
        for params_single_frame in str_parts[1:]:
            # split params string to separate parameters
            video_params = params_single_frame.split(PARAM_DIVIDER)
            for i, param in enumerate(video_params):
                video_params_pack[i].append(float(param))

        # append parameter list to vparam list
        param_list.append(video_params_pack)

        return param_list

# AUDIO PARAMETERS

    def get_aparams_list(self, aparams_string):
        PART_DIVIDER = ':*:'
        PARAM_DIVIDER = ':'

        param_list = []

        # split string to stream params and video params
        str_parts = aparams_string.split(PART_DIVIDER)
        # split stream parameters
        stream_params = str_parts[0].split(PARAM_DIVIDER)
        sparams_int = []
        for param in stream_params:
            sparams_int.append(int(param))

        param_list.append(sparams_int)

        audio_params_pack = [[], []]
        for params_single_frame in str_parts[1:]:
            # split params string to separate parameters
            audio_params = params_single_frame.split(PARAM_DIVIDER)
            for i, param in enumerate(audio_params):
                lowercase = param.lower()
                if lowercase == "-inf":
                    audio_params_pack[i].append(-70.0)
                elif (lowercase != "nan" and lowercase != "-nan") and \
                        lowercase != "inf":
                    audio_params_pack[i].append(float(param))
                else:
                    print("Bad LUFS values: ", aparams_string)

        # append parameter list to aparam list
        param_list.append(audio_params_pack)

        return param_list

# ADV LOUDNESS

    def get_interval_loudness(self, interval_string):
        PART_DIVIDER = ':*:'
        PARAM_DIVIDER = ':'

        param_list = []

        # split string to stream params and video params
        str_parts = interval_string.split(PART_DIVIDER)
        # split stream parameters
        stream_params = str_parts[0].split(PARAM_DIVIDER)
        sparams_int_list = []
        for param in stream_params:
            sparams_int_list.append(int(param))
        param_list.append(sparams_int_list)

        # split measured params
        measured_params = str_parts[1].split(PARAM_DIVIDER)
        param_list.append([float(measured_params[0]),
                           float(measured_params[1]),
                           int(measured_params[2])])

        return param_list


