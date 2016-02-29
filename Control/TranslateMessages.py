class TranslateMessages():
    def __init__(self):
        pass

# VIDEO PARAMETERS

    def translate_vparams_string_to_list(self, vparams_string):
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

