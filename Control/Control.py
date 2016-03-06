import time

from gi.repository import Gtk, Gio

from Backend.Backend import Backend
from Backend import State
from Gui.MainWindow import MainWindow
# from Usb.Usb import Usb
from Control.TranslateMessages import TranslateMessages
from Control.ErrorDetector import ErrorDetector
from Control import CustomMessages
from Control.ErrorTypesModel import ErrorTypesModel
from Control.ProgramTreeModel import ProgramTreeModel
from Control.TunerSettingsModel import TunerSettingsModel
from Config.Config import Config
from Log import Log
from Control.RfExchange import RfExchange


class Control():

    def __init__(self, app):

        # create log writer
        self.log = Log("log.txt")
        # create config
        self.config = Config()
        # create message translator
        self.msg_translator = TranslateMessages()
        # create error detector
        self.error_detector = ErrorDetector()

        # create program tree model for programs in stream
        self.stream_progs = ProgramTreeModel()
        # create program tree model for analyzed programs
        self.analyzed_progs = ProgramTreeModel()
        # append list of analyzed programs from config to model
        self.analyzed_progs.add_all_streams(self.config.get_prog_list())
        # create error types model
        self.error_model = ErrorTypesModel()
        # append list of analysis settings from config to model
        self.error_model.set_settings(self.config.get_analysis_settings())
        # create tuner settings model
        self.tuner_model = TunerSettingsModel()
        # append list of analysis settings from config to model
        self.tuner_model.set_settings(self.config.get_tuner_settings())

        # create tv tuner control
        self.rf_tuner = RfExchange(self.tuner_model.get_settings_list())
        # execute server for receiving messages from gstreamer pipeline
        self.start_server(1600)

        # create backend
        self.backend = Backend(streams=1)
        # create gui
        self.gui = MainWindow(app,
                              self.stream_progs,
                              self.analyzed_progs,
                              self.error_model,
                              self.tuner_model,
                              self.config.get_dark_theme(),
                              self.config.get_table_revealer(),
                              self.config.get_plot_info())
        # self.usb = Usb()

        # connect to gui signals
        self.gui.connect(CustomMessages.NEW_SETTINS_PROG_LIST,
                         self.on_new_prog_settings_from_gui
                         )
        self.gui.connect(CustomMessages.ACTION_START_ANALYSIS,
                         self.on_start_from_gui
                         )
        self.gui.connect(CustomMessages.ACTION_STOP_ANALYSIS,
                         self.on_stop_from_gui
                         )
        self.gui.connect(CustomMessages.VOLUME_CHANGED,
                         self.on_volume_changed
                         )
        self.gui.connect(CustomMessages.COLOR_THEME,
                         self.on_gui_color_theme_changed)

        self.gui.connect(CustomMessages.PROG_TABLE_REVEALER,
                         self.on_gui_table_revealer)

        self.gui.connect(CustomMessages.PLOT_PAGE_CHANGED,
                         self.on_gui_plot_page_changed)

        self.gui.connect(CustomMessages.ANALYSIS_SETTINGS_CHANGED,
                         self.on_analysis_settings_changed)

        self.gui.connect(CustomMessages.TUNER_SETTINGS_CHANGED,
                         self.on_tuner_settings_changed)

        # connect to tuner signals
        self.rf_tuner.connect(CustomMessages.NEW_TUNER_STATUS,
                              self.on_new_tuner_status)

        self.rf_tuner.connect(CustomMessages.NEW_TUNER_MEASURED_DATA,
                              self.on_new_tuner_measured_data)

        self.rf_tuner.connect(CustomMessages.NEW_TUNER_PARAMS,
                              self.on_new_tuner_params)

        # connect to usb signals
        # --

        # start analysis on app startup
        self.start_analysis()

        # set gui for analyzed programs
        self.apply_prog_list_to_gui()

        # initially set drawing black background
        # for corresponding renderers to True
        for stream in self.analyzed_progs.get_list():
            self.gui.set_draw_mode_for_renderers(True, stream[0])

        self.gui.queue_draw()

    def start_analysis(self):
        # execute all gstreamer pipelines
        self.backend.start_all_pipelines()
        self.gui.toolbar.change_start_icon()

        # set volume on all renderers to null
        self.gui.mute_all_renderers()

    def stop_analysis(self):
        # execute all gstreamer pipelines
        self.backend.terminate_all_pipelines()
        self.gui.toolbar.change_start_icon()
        self.stream_progs.clear_model()

        # set volume on all renderers to null
        self.gui.mute_all_renderers()

        # set drawing black background for all renderers to True
        for stream in self.analyzed_progs.get_list():
            self.gui.set_draw_mode_for_renderers(True, stream[0])
        # force redrawing of gui
        self.gui.queue_draw()

    # start server
    def start_server(self, port):
        # server for recieving messages from gstreamer pipeline
        server = Gio.SocketService.new()
        server.add_inet_port(port, None)
        # x - data to be passed to callback
        server.connect("incoming", self.message_from_pipeline_callback)
        server.start()

    def message_from_pipeline_callback(self, obj, conn, source):
        istream = conn.get_input_stream()
        ostream = conn.get_output_stream()
        buffer = istream.read_bytes(1000)
        data = buffer.get_data()

        # decode string back to unicode
        wstr = data.decode('utf-8', 'ignore')

        if len(wstr) > 0:
            if wstr[0] == 'd':
                # received program list
                # convert program string from pipeline to program list (array)
                progList = self.msg_translator.convert_stream_string_to_list(
                    wstr[1:])

                # append prog list to model
                self.stream_progs.add_one_stream(progList)

                # compare received and current analyzed prog lists
                compared_prog_list = self.analyzed_progs.get_compared_list(
                    progList)

                # apply compared program list to backend
                # (compared list contains only program equal prorams
                # from current and received lists)
                self.apply_prog_list_to_backend(compared_prog_list)

                # apply analysis params to backend
                self.send_analysis_params_to_backend()

                # set drawing black background
                # for corresponding renderers to False
                self.gui.set_draw_mode_for_renderers(False,
                                                     compared_prog_list[0])

            elif wstr[0] == 'v':
                # received video parameters
                # freeze black blockiness av_luma av_diff
                vparams = self.msg_translator.translate_vparams_string_to_list(
                    wstr[1:])
                self.error_detector.set_video_data(vparams)
                self.gui.on_video_measured_data(vparams)

            elif wstr[0] == 'e':
                # received end of stream
                self.on_end_of_stream(int(wstr[1:]))
                print(wstr)

    # make changes in gui according to program list
    def apply_prog_list_to_gui(self):
        # gui only needs program names and ids to redraw
        # so we need to extract them from program list
        guiProgInfo = self.analyzed_progs.get_progs_in_gui_format()

        # set gui for new programs from program list
        self.gui.set_new_programs(guiProgInfo)

    # applying prog list to backend
    def apply_prog_list_to_backend(self, progList):
        # to draw video backend needs xid of drawing areas
        # so we get them from gui
        xids = self.gui.get_renderers_xids()

        # apply new settings to backend
        # (settings consist of program list and xids)
        self.backend.apply_new_program_list(progList, xids)

    # actions when backend send "end of stream" message
    def on_end_of_stream(self, stream_id):
        # refresh program list model
        # delete this stream from model
        # this is done by passing empty prog list to model
        self.stream_progs.add_one_stream([stream_id, []])

        # getting state of gstreamer pipeline with corresponding stream id
        state = self.backend.get_pipeline_state(stream_id)

        # if current state is RUNNING
        # (this means that pipeline currently decoding some programs)
        # we need to restart this pipeline
        if state is State.RUNNING:
            self.backend.restart_pipeline(stream_id)

        # set drawing black background for corresponding renderers to True
        self.gui.set_draw_mode_for_renderers(True, stream_id)
        # force redrawing of gui
        self.gui.queue_draw()

    def send_analysis_params_to_backend(self):
        analysis_settings = self.error_model.get_settings_list()
        black_pixel_val = int(analysis_settings[5][2])
        pixel_diff = int(analysis_settings[9][2])
        self.backend.change_analysis_params(black_pixel_val, pixel_diff)

    # actions when gui send NEW_SETTINS_PROG_LIST message
    def on_new_prog_settings_from_gui(self, param):
        # get selected program list from stream progs model
        selected_progs = self.stream_progs.get_selected_list()

        # append program list to analyzed progs model
        self.analyzed_progs.add_all_streams(selected_progs)

        # redraw gui according to new program list
        self.apply_prog_list_to_gui()

        # we need to restart gstreamer pipelines with ids that were selected
        # so we need to extract these ids from program list
        stream_ids = self.analyzed_progs.get_stream_ids()

        # restart pipelines with selected ids
        for process_id in stream_ids:
            self.backend.restart_pipeline(process_id)

        # save program list in config
        self.config.set_prog_list(selected_progs)

    def on_start_from_gui(self, wnd):
        self.start_analysis()

    def on_stop_from_gui(self, wnd):
        self.stop_analysis()

    def on_volume_changed(self, wnd, stream_id, prog_id, pid, value):
        self.backend.change_volume(stream_id, prog_id, pid, value)

    def on_gui_color_theme_changed(self, wnd, data):
        self.config.set_dark_theme(data)

    def on_gui_table_revealer(self, wnd, data):
        self.config.set_table_revealer(data)

    def on_gui_plot_page_changed(self, wnd):
        plot_info = self.gui.get_plot_info()
        self.config.set_plot_info(plot_info)

    def on_analysis_settings_changed(self, wnd):
        # apply settings to backend
        self.send_analysis_params_to_backend()

        # get analysis settings from model
        analysis_settings = self.error_model.get_settings_list()

        # if analysis settings dialog is visible - update values
        if self.gui.analysisSetDlg.get_visible() is True:
            self.gui.analysisSetDlg.update_values()

        # save analysis settings to config
        self.config.set_analysis_settings(analysis_settings)

    def on_tuner_settings_changed(self, wnd):
        # get tuner settings
        tuner_settings = self.tuner_model.get_settings_list()

        # if tuner dialog is visible - update values
        if self.gui.tunerDlg.get_visible() is True:
            self.gui.tunerDlg.update_values()

        self.rf_tuner.apply_settings(tuner_settings)

        # save settings to config
        self.config.set_tuner_settings(tuner_settings)

    def on_new_tuner_status(self, src, status, hw_errors, temperature):
        #print(status, hw_errors, temperature)
        pass

    def on_new_tuner_measured_data(self,
                                   src,
                                   mer,
                                   mer_updated,
                                   ber1,
                                   ber1_updated,
                                   ber2,
                                   ber2_updated,
                                   ber3,
                                   ber3_updated):

        measured_data = [mer,
                         mer_updated,
                         ber1,
                         ber1_updated,
                         ber2,
                         ber2_updated,
                         ber3,
                         ber3_updated]

        self.gui.on_new_tuner_measured_data(measured_data)

    def on_new_tuner_params(self, src, status, modulation, params):
        #print(status, modulation, params)
        self.gui.on_new_tuner_params(status, modulation, params)

    # when app closes, we need to delete all gstreamer pipelines
    def destroy(self):
        # terminate all gstreamer pipelines
        self.backend.terminate_all_pipelines()
        # disconnect from tuner
        self.rf_tuner.disconnect()
        self.rf_tuner.thread_active = False

