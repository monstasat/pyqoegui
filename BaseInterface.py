from gi.repository import GObject

from Control import CustomMessages


class BaseInterface(GObject.GObject):

    __gsignals__ = {
        CustomMessages.NEW_SETTINS_PROG_LIST: (GObject.SIGNAL_RUN_FIRST,
                                               None, ()),
        CustomMessages.ANALYSIS_SETTINGS_CHANGED: (GObject.SIGNAL_RUN_FIRST,
                                               None, ()),
        CustomMessages.TUNER_SETTINGS_CHANGED: (GObject.SIGNAL_RUN_FIRST,
                                               None, ())}

    def __init__(self,
                 analyzed_progs_list,
                 analysis_settings_list,
                 tuner_settings_list):

        GObject.GObject.__init__(self)

        # create analysis settings list
        self.analysis_settings = analysis_settings_list
        # create tuner settings list
        self.tuner_settings = tuner_settings_list


    # Methods for interaction with Control
    # Common methods for Gui and Usb

    # called by Control to update stream prog list
    def update_stream_prog_list(self, prog_list, all_streams=False):
        if all_streams is True:
            self.stream_progs_model.add_all_streams(prog_list)
        else:
            self.stream_progs_model.add_one_stream(prog_list)

    # called by Control to update analyzed prog list
    def update_analyzed_prog_list(self, prog_list):
        # apply prog list to analyzed progs model
        self.analyzed_progs_model.add_all_streams(prog_list)
        # add new programs to gui
        self.cur_results_page.on_prog_list_changed(prog_list)
        # determine wether table revealer button should be visible
        self.manage_table_revealer_button_visibility()

    # called by Control to update analysis settings
    def update_analysis_settings(self, analysis_settings):
        # save settings
        self.analysis_settings = analysis_settings

    # called by Control to update tuner settings
    def update_tuner_settings(self, tuner_settings):
        # save settings
        self.tuner_settings = tuner_settings

    # called by Control to update tuner parameters
    def update_tuner_params(self, status, modulation, params):
        if self.tunerDlg.get_visible() is True:
            self.tunerDlg.set_new_tuner_params(status, modulation, params)

    # called by Control to update tuner measured data
    def update_tuner_measured_data(self, measured_data):
        if self.tunerDlg.get_visible() is True:
            self.tunerDlg.set_new_measured_data(measured_data)

    # called by Error Detector to update video status
    def update_video_status(self, results):
        self.cur_results_page.prgtbl.update_video(results)

    # called by Error Detector to update audio status
    def update_audio_status(self, results):
        self.cur_results_page.prgtbl.update_audio(results)

    # Control asks to return analyzed prog list
    def get_analyzed_prog_list(self):
        return self.stream_progs_model.get_selected_list()

    # Control asks to return analysis settings
    def get_analysis_settings(self):
        return self.analysisSetDlg.store.get_settings_list()

    # Control asks to return tuner settings
    def get_tuner_settings(self):
        return self.tunerDlg.store.get_settings_list()
