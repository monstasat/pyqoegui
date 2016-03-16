import sys
import psutil

from gi.repository import Gio, GObject

from Backend.Backend import Backend
from Backend import State
from Gui.Gui import Gui
from Usb.Usb import Usb
from Control.TranslateMessages import TranslateMessages
from Control.ErrorDetector.VideoErrorDetector import VideoErrorDetector
from Control.ErrorDetector.AudioErrorDetector import AudioErrorDetector
from Control.ProgramListControl import ProgramListControl
from Control import CustomMessages
from Config.Config import Config
from Log import Log
from Control.DVBTunerControl import DVBTunerControl
from Control import AnalysisSettingsIndexes as ai
from Control import TunerSettingsIndexes as ti


class Control(GObject.GObject):

    def __init__(self, app):

        # create log writer
        self.log = Log("log.txt")
        # create config
        self.config = Config()
        # create message translator
        self.msg_translator = TranslateMessages()

        # write message to log
        self.log.write_log_message("application launched", True)

        # create program list from current streams
        self.sprogs_control = ProgramListControl([])
        # create program list currently selected by user
        self.aprogs_control = ProgramListControl(self.config.get_prog_list())
        # create list with analysis settings
        self.analysis_settings = self.config.get_analysis_settings()
        if len(self.analysis_settings) < len(ai.DEFAULT_VALUES):
            self.analysis_settings  = ai.DEFAULT_VALUES
        # create tuner settings list
        self.tuner_settings = self.config.get_tuner_settings()
        if len(self.tuner_settings) < len(ti.DEFAULT_VALUES):
            self.tuner_settings  = ti.DEFAULT_VALUES

        # create tv tuner control
        self.rf_tuner = DVBTunerControl(self.tuner_settings)
        # execute server for receiving messages from gstreamer pipeline
        self.start_server(1600)

        # create backend
        self.backend = Backend(streams=1)
        # create gui
        fullscreen = app.args.fullscreen
        self.gui = Gui(app,
                       app.args.width,
                       app.args.height,
                       fullscreen,
                       self.analyzed_progs,
                       self.analysis_settings,
                       self.tuner_settings,
                       self.config.get_color_theme(),
                       self.config.get_table_revealer(),
                       self.config.get_plot_info())

        self.usb = Usb(self.analyzed_progs,
                       self.analysis_settings,
                       self.tuner_settings)

        # create video error detector
        self.video_error_detector = VideoErrorDetector(
                                        self.analyzed_progs,
                                        self.analysis_settings,
                                        self.gui)
        # create audio error detector
        self.audio_error_detector = AudioErrorDetector(
                                        self.analyzed_progs,
                                        self.analysis_settings,
                                        self.gui)

        # connect to gui signals
        self.gui.connect(CustomMessages.NEW_SETTINS_PROG_LIST,
                         self.on_new_analyzed_prog_list)
        self.gui.connect(CustomMessages.ANALYSIS_SETTINGS_CHANGED,
                         self.on_new_analysis_settings)
        self.gui.connect(CustomMessages.TUNER_SETTINGS_CHANGED,
                         self.on_new_tuner_settings)
        self.gui.connect(CustomMessages.ACTION_START_ANALYSIS,
                         self.on_start)
        self.gui.connect(CustomMessages.ACTION_STOP_ANALYSIS,
                         self.on_stop)
        self.gui.connect(CustomMessages.VOLUME_CHANGED,
                         self.on_volume_changed)
        self.gui.connect(CustomMessages.COLOR_THEME,
                         self.on_gui_color_theme_changed)
        self.gui.connect(CustomMessages.PROG_TABLE_REVEALER,
                         self.on_gui_table_revealer)
        self.gui.connect(CustomMessages.PLOT_PAGE_CHANGED,
                         self.on_gui_plot_page_changed)

        # connect to usb signals
        self.usb.connect(CustomMessages.NEW_SETTINS_PROG_LIST,
                         self.on_new_analyzed_prog_list)
        self.usb.connect(CustomMessages.ANALYSIS_SETTINGS_CHANGED,
                         self.on_new_analysis_settings)
        self.usb.connect(CustomMessages.TUNER_SETTINGS_CHANGED,
                         self.on_new_tuner_settings)
        self.usb.connect(CustomMessages.ACTION_START_ANALYSIS,
                         self.on_start)
        self.usb.connect(CustomMessages.ACTION_STOP_ANALYSIS,
                         self.on_stop)
        self.usb.connect(CustomMessages.REMOTE_CLIENTS_NUM_CHANGED,
                         self.on_remote_clients_num_changed)

        # connect to tuner signals
        self.rf_tuner.connect(CustomMessages.NEW_TUNER_STATUS,
                              self.on_new_tuner_status)
        self.rf_tuner.connect(CustomMessages.NEW_TUNER_MEASURED_DATA,
                              self.on_new_tuner_measured_data)
        self.rf_tuner.connect(CustomMessages.NEW_TUNER_PARAMS,
                              self.on_new_tuner_params)

        # set gui for analyzed programs
        self.gui.update_analyzed_prog_list(self.analyzed_progs)
        # set usb for analyzed programs
        self.usb.update_analyzed_prog_list(self.analyzed_progs)

        # write log message
        msg = "initial number of selected programs: %d" % \
                                        self.aprogs_control.get_prog_num()
        self.log.write_log_message(msg)

        # initially set drawing black background
        # for corresponding renderers to True
        for stream in self.analyzed_progs:
            self.gui.update_rendering_mode(True, stream[0])

        self.gui.window.queue_draw()

        GObject.timeout_add(1000, self.on_get_cpu_load)

        # start analysis on app startup
        self.start_analysis()

    @property
    def stream_progs(self):
        return self.sprogs_control.prog_list

    @property
    def analyzed_progs(self):
        return self.aprogs_control.prog_list

    @stream_progs.setter
    def stream_progs(self, value):
        self.sprogs_control.prog_list = value

    @analyzed_progs.setter
    def analyzed_progs(self, value):
        self.aprogs_control.prog_list = value

    # when app closes, we need to take some actions
    def __destroy__(self):
        # terminate all gstreamer pipelines
        self.backend.terminate_all_pipelines()
        # disconnect from tuner
        self.rf_tuner.disconnect()
        self.rf_tuner.thread_active = False

        # write message to log
        self.log.write_log_message("application closed")

    # start server
    def start_server(self, port):
        # server for recieving messages from gstreamer pipeline
        server = Gio.SocketService.new()
        server.add_inet_port(port, None)
        # x - data to be passed to callback
        server.connect("incoming", self.message_from_pipeline_callback)
        server.start()

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

        # clear stream prog list
        self.stream_progs.clear()

        # update stream prog list in Gui and Usb
        self.gui.update_stream_prog_list([])
        self.usb.update_stream_prog_list([])

        # set volume on all renderers to null
        self.gui.mute_all_renderers()

        # set drawing black background for all renderers to True
        for stream in self.analyzed_progs:
            self.gui.update_rendering_mode(True, stream[0])
        # force redrawing of gui
        self.gui.window.queue_draw()

    def on_get_cpu_load(self):
        load = psutil.cpu_percent(interval=0)
        self.gui.update_cpu_load(load)
        self.usb.update_cpu_load(load)
        return True

    # Interaction with Gui and Usb
    # Common methods for Gui and USb

    # new analyzed prog list received
    def on_new_analyzed_prog_list(self, source):
        # get selected program list from message source
        self.analyzed_progs = source.get_analyzed_prog_list()

        # Configure Gui and Usb according to new analyzed prog list
        # update gui according to new program list
        self.gui.update_analyzed_prog_list(self.analyzed_progs)
        # update usb according to new program list
        self.usb.update_analyzed_prog_list(self.analyzed_progs)

        # Configure error detectors according to new analyzed prog list
        # pass new prog list to error detectors
        self.video_error_detector.set_programs_list(
                                        self.analyzed_progs)
        self.audio_error_detector.set_programs_list(
                                        self.analyzed_progs)

        # Configure backend according to new analyzed prog list
        # we need to restart gstreamer pipelines with ids that were selected
        # so we need to extract these ids from program list
        stream_ids = []
        # iterating over stream rows
        for stream in self.analyzed_progs:
            stream_ids.append(stream[0])
        # restart pipelines with selected ids
        for pipeline_id in stream_ids:
            self.backend.restart_pipeline(pipeline_id)

        # Save analyzed prog list in Config
        self.config.set_prog_list(self.analyzed_progs)

        # write message to log
        self.log.write_log_message("new programs selected for analysis " + \
                                   "(source: %s)" % source.interface_name)

    # new analysis settings received
    def on_new_analysis_settings(self, source):
        # get new analysis settings from message source
        self.analysis_settings = source.get_analysis_settings()

        # Configure Gui and Usb according to new analysis settings
        self.gui.update_analysis_settings(self.analysis_settings)
        self.usb.update_analysis_settings(self.analysis_settings)

        # Configure error detectors according to new analysis settings
        self.video_error_detector.set_analysis_settings(self.analysis_settings)
        self.audio_error_detector.set_analysis_settings(self.analysis_settings)

        # Configure backend according to new analysis settings
        self.send_analysis_params_to_backend()

        # Save analysis settings in Config
        self.config.set_analysis_settings(self.analysis_settings)

        # write message to log
        self.log.write_log_message("new analysis settings selected " + \
                                   "(source: %s)" % source.interface_name)

    # new tuner settings received
    def on_new_tuner_settings(self, source):
        # get new tuner settings from message source
        self.tuner_settings = source.get_tuner_settings()

        # Configure Gui and Usb according to new analysis settings
        self.gui.update_tuner_settings(self.tuner_settings)
        self.usb.update_tuner_settings(self.tuner_settings)

        # Configure dvb tuner according to new tuner settings
        self.rf_tuner.apply_settings(self.tuner_settings)

        # FIXME: is it necessary? check this
        # Configure backend according to new tuner settings
        self.backend.start_all_pipelines()

        # Save tuner settings in Config
        self.config.set_tuner_settings(self.tuner_settings)

        # write message to log
        self.log.write_log_message("new tuner settings selected " + \
                                   "(source: %s)" % source.interface_name)

    # Interaction with Gui and Usb
    # Methods specific for Gui

    # Gui sent a message about start button clicked
    def on_start(self, source):
        self.start_analysis()

        # write message to log
        self.log.write_log_message("analysis started" + \
                                   "(source: %s)" % source.interface_name)

    # Gui sent a message about stop button clicked
    def on_stop(self, source):
        self.stop_analysis()

        # write message to log
        self.log.write_log_message("analysis stopped" + \
                                   "(source: %s)" % source.interface_name)

    # Gui sent a message about volume level changed
    def on_volume_changed(self, source, stream_id, prog_id, pid, value):
        # tell backend to change volume in corresponding pipeline
        self.backend.change_volume(stream_id, prog_id, pid, value)

    # Gui sent a message about color theme changed
    def on_gui_color_theme_changed(self, source, color_theme):
        # save new color theme in Config
        self.config.set_color_theme(color_theme)

    # Gui sent a message about program table hidden/revealed
    def on_gui_table_revealer(self, source, table_state):
        # save program table state in Config
        self.config.set_table_revealer(table_state)

    # Gui sent a message about plot was added/deleted
    def on_gui_plot_page_changed(self, source):
        # get current plot info from Gui
        plot_info = self.gui.get_plot_info()
        # save current plot info in Config
        self.config.set_plot_info(plot_info)

    # Interaction with Gui and Usb
    # Methods specific for Usb

    def on_remote_clients_num_changed(self, source, clients_num):
        self.gui.update_remote_clients_num(clients_num)

    # Methods for interaction with dvb tuner control

    # Tuner control sent a message with new status
    def on_new_tuner_status(self, source, status, hw_errors, temperature):
        self.gui.update_tuner_status(status, hw_errors, temperature)
        self.usb.update_tuner_status(status, hw_errors, temperature)

    # Tuner control sent a message with new measured data
    def on_new_tuner_measured_data(self,
                                   source,
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

        self.gui.update_tuner_measured_data(measured_data)
        self.usb.update_tuner_measured_data(measured_data)

    # Tuner control sent a message with new tuner params
    def on_new_tuner_params(self, source, status, modulation, params):
        self.gui.update_tuner_params(status, modulation, params)
        self.usb.update_tuner_params(status, modulation, params)

    # Methods for interaction with backend

    # Set new analysis settings to backend
    def send_analysis_params_to_backend(self):
        # get black pixel value from analysis settings
        black_pixel_val = int(self.analysis_settings[ai.BLACK_PIXEL][2])
        # get pixel difference value from analysis settings
        pixel_diff = int(self.analysis_settings[ai.PIXEL_DIFF][2])

        # apply parameters to gstreamer pipelines
        self.backend.change_analysis_params(black_pixel_val, pixel_diff)

    # Backend sent a message that one of streams has ended
    def end_of_stream_received(self, stream_id):
        # update stream prog list
        self.sprogs_control.add_one_stream([stream_id, []])

        # update stream program list in Gui and Usb
        self.gui.update_stream_prog_list(self.stream_progs)
        self.usb.update_stream_prog_list(self.stream_progs)

        # getting state of gstreamer pipeline with corresponding stream id
        state = self.backend.get_pipeline_state(stream_id)

        # if current state is RUNNING
        # (this means that pipeline currently decoding some programs)
        # we need to restart this pipeline
        if state is State.RUNNING:
            # add event to log
            msg = "end of stream (id = %d) received" % stream_id
            self.log.write_log_message(msg)
            self.backend.restart_pipeline(stream_id)

        # set drawing black background for corresponding renderers to True
        self.gui.update_rendering_mode(True, stream_id)
        # force redrawing of gui
        self.gui.window.queue_draw()

    # Handling messages from backend
    def message_from_pipeline_callback(self, obj, conn, source):
        istream = conn.get_input_stream()
        ostream = conn.get_output_stream()
        buffer = istream.read_bytes(1000)
        data = buffer.get_data()

        # decode string back to unicode
        wstr = data.decode('utf-8', 'ignore')

        if len(wstr) > 0:
            # new stream program list received from backend
            if wstr[0] == 'd':
                # translate message from string to list
                prog_list = self.msg_translator.get_prog_list(wstr[1:])

                self.sprogs_control.add_one_stream(prog_list)

                # update stream program list in Gui and Usb
                self.gui.update_stream_prog_list(self.stream_progs)
                self.usb.update_stream_prog_list(self.stream_progs)

                # compare received and current analyzed prog lists
                # (compared list contains only program equal prorams
                # from current and received lists)
                compared_prog_list = self.aprogs_control.get_compared_list(
                    prog_list)

                # apply new prog list to backend
                # get xids from gui
                xids = self.gui.get_renderers_xids()
                # pass prog list and xids to backend
                self.backend.apply_new_program_list(compared_prog_list, xids)

                # apply analysis params to backend
                self.send_analysis_params_to_backend()

                # set drawing black background
                # for corresponding renderers to False
                #TODO: pass not only stream id, but prog id too,
                # to disable drawing in only those renderers, that
                # should be drawn by backend
                self.gui.update_rendering_mode(False, compared_prog_list[0])

                # write event to log
                self.log.write_log_message("new stream prog list received "
                                           "from backend")

            # measured data for video received from backend
            elif wstr[0] == 'v':
                # translate message from string to list
                vparams = self.msg_translator.get_vparams_list(wstr[1:])
                self.video_error_detector.set_data(vparams)

                # update video plot data in gui
                self.gui.update_video_plots_data(vparams)

            # measured data for audio received from backend
            elif wstr[0] == 'a':
                pass

            # end of stream message received from backend
            elif wstr[0] == 'e':
                self.end_of_stream_received(int(wstr[1:]))
                print(wstr)
