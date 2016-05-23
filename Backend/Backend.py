from Backend.GstreamerPipeline import GstreamerPipeline
from Backend import State


class Backend():
    def __init__(self, streams=1, port=1600):

        self.gs_pipelines = []
        # create gs pipeline instances
        for stream_id in range(streams):
            self.gs_pipelines.append(GstreamerPipeline(stream_id))

    # check if stream id parameter is valid
    def is_pipeline(self, stream_id):
        return not (stream_id + 1) > len(self.gs_pipelines)

    # restart selected pipeline
    def restart_pipeline(self, stream_id):
        self.start_pipeline(stream_id)

    # execute selected pipeline
    def start_pipeline(self, stream_id):
        if self.is_pipeline(stream_id) is True:
            self.gs_pipelines[stream_id].execute()

    # terminate selected pipeline
    def terminate_pipeline(self, stream_id):
        if self.is_pipeline(stream_id) is True:
            self.gs_pipelines[stream_id].terminate()

    # execute all pipelines
    def start_all_pipelines(self):
        list(map(lambda x: x.execute(), self.gs_pipelines))

    # terminate all pipelines
    def terminate_all_pipelines(self):
        list(map(lambda x: x.terminate(), self.gs_pipelines))

    def get_pipeline_state(self, stream_id):
        if self.is_pipeline(stream_id) is True:
            return self.gs_pipelines[stream_id].state
        else:
            return State.NONEXISTENT

    # apply new program list
    def apply_new_program_list(self, prog_list, xids):
        # combine received prog list and xids
        combined_list = self.combine_prog_list_with_xids(prog_list, xids)

        # if stream with sent number exist and program num is not null
        if self.is_pipeline(combined_list[0]) is True:
            # determine number of programs in this stream
            # to get necessary number of xids
            self.gs_pipelines[combined_list[0]].apply_new_program_list(
                combined_list)

    # combines prog list with renderers xids
    def combine_prog_list_with_xids(self, prog_list, xids):
        stream_id = prog_list[0]
        progs = prog_list[1]
        combined_progs = []
        for prog in progs:
            i = 0
            while i != len(xids):
                prog_id = int(prog[0])
                if (stream_id == xids[i][0]) and (prog_id == xids[i][1]):
                    prog.insert(4, xids[i][2])
                    combined_progs.append(prog)
                i += 1

        return [stream_id, combined_progs]

    # change renderer volume
    def change_volume(self, stream_id, prog_id, pid, value):
        if (self.is_pipeline(stream_id) is True):
            self.gs_pipelines[stream_id].change_volume(prog_id, pid, value)

    # apply new analysis parameters
    def change_analysis_params(self, black_pixel, diff_level, mark_blocks):
        for pipeline in self.gs_pipelines:
            pipeline.change_analysis_params(black_pixel,
                                            diff_level,
                                            mark_blocks)

