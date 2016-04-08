import psutil
import os
import re

from gi.repository import Gio, GObject

from BaseInterface import BaseInterface
from Backend.Backend import Backend
from Backend import State
from Control.TranslateMessages import TranslateMessages
from Control.ErrorDetector.ErrorDetector import ErrorDetector
from Control.ProgramListControl import ProgramListControl
from Control.DVBTunerControl import DVBTunerControl
from Control import AnalysisSettingsIndexes as ai
from Control import TunerSettingsIndexes as ti
from Control import CustomMessages
from Config.Config import Config
from Log import Log


class Control(GObject.GObject):

    def __init__(self, app):

        # create log writer
        self.log = Log()
        # create config
        self.config = Config()
        # create message translator
        self.msg_translator = TranslateMessages()

        self.sprogs_control = ProgramListControl([])
        self.aprogs_control = ProgramListControl(self.config.get_prog_list())
        self.analysis_settings = self.config.get_analysis_settings()
        tuner_settings = self.config.get_tuner_settings()
        audio_source = self.config.get_audio_source()

        # create tv tuner control
        self.rf_tuner = DVBTunerControl(tuner_settings)
        # execute server for receiving messages from gstreamer pipeline
        self.server = None
        self.start_server(1600)

        # create backend
        self.backend = Backend(streams=1)

        # create interfaces
        interface_names = ['Gui', 'Usb']
        self.interfaces = list(map(lambda x: BaseInterface.factory(x, app),
                                   interface_names))

        # manage interfaces
        for interface in self.interfaces:
            interface.update_analyzed_prog_list(self.analyzed_progs)
            interface.update_analysis_settings(self.analysis_settings)
            interface.update_tuner_settings(tuner_settings)
            interface.update_audio_source(audio_source)

            interface.connect(CustomMessages.NEW_SETTINS_PROG_LIST,
                              self.on_new_analyzed_prog_list)
            interface.connect(CustomMessages.ANALYSIS_SETTINGS_CHANGED,
                              self.on_new_analysis_settings)
            interface.connect(CustomMessages.TUNER_SETTINGS_CHANGED,
                              self.on_new_tuner_settings)
            interface.connect(CustomMessages.ACTION_START_ANALYSIS,
                              self.on_start)
            interface.connect(CustomMessages.ACTION_STOP_ANALYSIS,
                              self.on_stop)
            interface.connect(CustomMessages.AUDIO_SOURCE_CHANGED,
                              self.on_new_audio_source)

            # if interface is of type 'Gui'
            if self.is_gui(interface) is True:
                interface.set_gui_params(app.args.width,
                                         app.args.height,
                                         app.args.fullscreen,
                                         app.args.debug,
                                         self.config.get_color_theme(),
                                         self.config.get_table_revealer(),
                                         self.config.get_plot_info())
                interface.connect(CustomMessages.VOLUME_CHANGED,
                                  self.on_volume_changed)
                interface.connect(CustomMessages.COLOR_THEME,
                                  self.on_gui_color_theme_changed)
                interface.connect(CustomMessages.PROG_TABLE_REVEALER,
                                  self.on_gui_table_revealer)
                interface.connect(CustomMessages.PLOT_PAGE_CHANGED,
                                  self.on_gui_plot_page_changed)
                interface.window.connect("delete-event", self.on_gui_delete)

                # initially set drawing black background
                # for corresponding renderers to True
                for stream in self.analyzed_progs:
                    interface.update_rendering_mode(True, stream[0])
                interface.window.queue_draw()

            # if interface is of type 'Usb'
            elif self.is_usb(interface) is True:
                if interface.exchange.is_connected is False:
                    print("Usb interface is not connected. "
                          "Deleting interface...")
                    interface.__destroy__()
                    self.interfaces.remove(interface)
                    continue
                interface.connect(CustomMessages.REMOTE_CLIENTS_NUM_CHANGED,
                                  self.on_remote_clients_num_changed)

        if len(self.interfaces) == 0:
            print("There are no interfaces available, terminating...")
            self.__destroy__()
            return

        aset = {'vloss': 2, 'black_cont': 90, 'black_peak': 99,
                'luma_cont': 20, 'luma_peak': 17, 'black_time': 2,
                'freeze_cont': 90, 'freeze_peak': 99,
                'diff_cont': 0.2, 'diff_peak': 0.05, 'freeze_time': 2,
                'blocky_cont': 3, 'blocky_peak': 6, 'blocky_time': 2,
                'aloss': 2,
                'silence_cont': -35, 'silence_peak': -45, 'silence_time': 2,
                'loudness_cont': -21.9, 'loudness_peak': -15, 'loudness_time': 2}

        self.error_detector = ErrorDetector(self.analyzed_progs, aset)

        # connect to tuner signals
        self.rf_tuner.connect(CustomMessages.NEW_TUNER_STATUS,
                              self.on_new_tuner_status)
        self.rf_tuner.connect(CustomMessages.NEW_TUNER_MEASURED_DATA,
                              self.on_new_tuner_measured_data)
        self.rf_tuner.connect(CustomMessages.NEW_TUNER_PARAMS,
                              self.on_new_tuner_params)

        # write log message
        self.log.write_log_message("application launched", True)
        msg = "initial number of selected programs: %d" % \
              self.aprogs_control.get_prog_num()
        self.log.write_log_message(msg)

        GObject.timeout_add(1000, self.on_get_cpu_load)
        GObject.timeout_add(1000, self.get_errors)

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

        list(map(lambda x: x.__destroy__(), self.interfaces))
        self.interfaces.clear()

        # stop server for recieving messages from gstreamer pipeline
        if self.server is not None:
            self.server.stop()

        # disconnect from tuner
        self.rf_tuner.disconnect()
        self.rf_tuner.thread_active = False

        # write message to log
        self.log.write_log_message("application closed")

    def is_gui(self, interface):
        return type(interface).__name__ == 'Gui'

    def is_usb(self, interface):
        return type(interface).__name__ == 'Usb'

    # start server
    def start_server(self, port):
        # server for recieving messages from gstreamer pipeline
        self.server = Gio.SocketService.new()
        self.server.add_inet_port(port, None)
        self.server.connect("incoming", self.message_from_pipeline_callback)
        self.server.start()

    def start_analysis(self):
        self.backend.start_all_pipelines()

        for interface in self.interfaces:
            if self.is_gui(interface) is True:
                interface.toolbar.change_start_icon()

    def stop_analysis(self):
        self.backend.terminate_all_pipelines()
        self.stream_progs.clear()

        list(map(lambda x: x.update_stream_prog_list([]), self.interfaces))

        for interface in self.interfaces:
            if self.is_gui(interface) is True:
                # change toolbar icon
                interface.toolbar.change_start_icon()
                # set drawing black background for all renderers to True
                for stream in self.analyzed_progs:
                    interface.update_rendering_mode(True, stream[0])
                interface.window.queue_draw()

    def on_get_cpu_load(self):
        load = psutil.cpu_percent(interval=0)
        list(map(lambda x: x.update_cpu_load(load), self.interfaces))
        return True

    def get_errors(self):
        err_list = self.error_detector.get_errors()
        #print(err_list, '\n')
        list(map(lambda x: x.update_analysis_results(err_list),
                 self.interfaces))
        return True

    # Interaction with Gui and Usb
    # Common methods for Gui and USb

    # new analyzed prog list received
    def on_new_analyzed_prog_list(self, source):
        # get selected program list from message source
        self.analyzed_progs = source.get_analyzed_prog_list()

        # Configure Gui and Usb according to new analyzed prog list
        list(map(lambda x: x.update_analyzed_prog_list(self.analyzed_progs),
                 self.interfaces))

        # initially mute all renderers
        for interface in self.interfaces:
            if self.is_gui(interface) is True:
                interface.mute_all_renderers()

        # Configure error detectors according to new analyzed prog list
        self.error_detector.set_prog_list(self.analyzed_progs)

        # Configure backend according to new analyzed prog list
        # we need to restart gstreamer pipelines with ids that were selected
        list(map(lambda stream: self.backend.restart_pipeline(stream[0]),
                 self.analyzed_progs))

        # Save analyzed prog list in Config
        self.config.set_prog_list(self.analyzed_progs)

        # write message to log
        msg = "new programs selected for analysis " + \
              "(source: %s)" % type(source).__name__
        self.log.write_log_message(msg)

    # new analysis settings received
    def on_new_analysis_settings(self, source):
        # get new analysis settings from message source
        self.analysis_settings = source.get_analysis_settings()

        # Configure Gui and Usb according to new analysis settings
        list(map(lambda x: x.update_analysis_settings(self.analysis_settings),
                 self.interfaces))

        # Configure error detectors according to new analysis settings
        self.error_detector.set_analysis_settings(self.analysis_settings)

        # Configure backend according to new analysis settings
        self.send_analysis_params_to_backend()

        # Save analysis settings in Config
        self.config.set_analysis_settings(self.analysis_settings)

        # write message to log
        msg = "new analysis settings selected " + \
              "(source: %s)" % type(source).__name__
        self.log.write_log_message(msg)

    # new tuner settings received
    def on_new_tuner_settings(self, source):
        # get new tuner settings from message source
        tuner_settings = source.get_tuner_settings()

        # Configure Gui and Usb according to new analysis settings
        list(map(lambda x: x.update_tuner_settings(tuner_settings),
                 self.interfaces))

        # Configure dvb tuner according to new tuner settings
        self.rf_tuner.apply_settings(tuner_settings)

        # FIXME: is it necessary? check this
        # Configure backend according to new tuner settings
        self.backend.start_all_pipelines()

        # Save tuner settings in Config
        self.config.set_tuner_settings(tuner_settings)

        # write message to log
        msg = "new tuner settings selected " + \
              "(source: %s)" % type(source).__name__
        self.log.write_log_message(msg)

    # new audio source received
    def on_new_audio_source(self, source):
        # get new audio source from message source
        audio_source = source.get_audio_source()

        # Configure Gui and Usb according to new audio source
        list(map(lambda x: x.update_audio_source(audio_source),
                 self.interfaces))

        # Configure audio source
        output = source.audio_outputs[audio_source]
        cmd = "pacmd set-card-profile " + str(output[0]) + \
                  " " + str(output[1])
        os.popen(cmd)
        os.popen("pacmd set-default-sink " + str(output[0]))
        os.popen("pacmd set-default-source " + str(output[0]))

        # list active playing streams
        buf = os.popen("pacmd list-sink-inputs").readlines()
        # switch them to new output
        for line in buf:
            res = re.search("index: \w*", line)
            if res is not None:
                cmd = "pacmd move-sink-input" + \
                      res.group().split(':')[1] + " " + str(output[0])
                os.popen(cmd)

        # Save audio source in Config
        self.config.set_audio_source(audio_source)

    # Interaction with Gui and Usb
    # Methods specific for Gui

    # Gui sent a message about start button clicked
    def on_start(self, source):
        self.start_analysis()
        msg = "analysis started" + "(source: %s)" % type(source).__name__
        self.log.write_log_message(msg)

    # Gui sent a message about stop button clicked
    def on_stop(self, source):
        self.stop_analysis()
        msg = "analysis stopped" + "(source: %s)" % type(source).__name__
        self.log.write_log_message(msg)

    # Gui sent a message about volume level changed
    def on_volume_changed(self, source, stream_id, prog_id, pid, value):
        self.backend.change_volume(stream_id, prog_id, pid, value)

    # Gui sent a message about color theme changed
    def on_gui_color_theme_changed(self, source, color_theme):
        self.config.set_color_theme(color_theme)

    # Gui sent a message about program table hidden/revealed
    def on_gui_table_revealer(self, source, table_state):
        self.config.set_table_revealer(table_state)

    # Gui sent a message about plot was added/deleted
    def on_gui_plot_page_changed(self, source):
        # get current plot info from Gui
        for interface in self.interfaces:
            if self.is_gui(interface) is True:
                plot_info = interface.get_plot_info()
        # save current plot info in Config
        self.config.set_plot_info(plot_info)

    def on_gui_delete(self, source, event):
        self.__destroy__()

    # Interaction with Gui and Usb
    # Methods specific for Usb

    def on_remote_clients_num_changed(self, source, clients_num):
        for interface in self.interfaces:
            if self.is_gui(interface) is True:
                interface.update_remote_clients_num(clients_num)

    # Methods for interaction with dvb tuner control

    # Tuner control sent a message with new status
    def on_new_tuner_status(self, source, status, hw_errors, temperature):
        for interface in self.interfaces:
            interface.update_tuner_status(status, hw_errors, temperature)

    # Tuner control sent a message with new measured data
    def on_new_tuner_measured_data(self, source, mer, mer_updated,
                                   ber1, ber1_updated, ber2, ber2_updated,
                                   ber3, ber3_updated):

        measured_data = [mer, mer_updated, ber1, ber1_updated,
                         ber2, ber2_updated, ber3, ber3_updated]

        list(map(lambda x: x.update_tuner_measured_data(measured_data),
                 self.interfaces))

    # Tuner control sent a message with new tuner params
    def on_new_tuner_params(self, source, status, modulation, params):
        for interface in self.interfaces:
            interface.update_tuner_params(status, modulation, params)

    # Methods for interaction with backend

    # Set new analysis settings to backend
    def send_analysis_params_to_backend(self):
        black_pixel_val = int(self.analysis_settings[ai.BLACK_PIXEL][2])
        pixel_diff = int(self.analysis_settings[ai.PIXEL_DIFF][2])
        self.backend.change_analysis_params(black_pixel_val, pixel_diff)

    # Backend sent a message that one of streams has ended
    def end_of_stream_received(self, stream_id):
        # update stream prog list
        self.sprogs_control.add_one_stream([stream_id, []])

        # if current state of pipeline with corresponding id is RUNNING
        # we need to restart this pipeline
        if self.backend.get_pipeline_state(stream_id) is State.RUNNING:
            msg = "end of stream (id = %d) received" % stream_id
            print(msg)
            self.backend.restart_pipeline(stream_id)
            # add event to log
            self.log.write_log_message(msg)

        for interface in self.interfaces:
            interface.update_stream_prog_list(self.stream_progs)
            if self.is_gui(interface) is True:
                # set drawing black background for renderers
                interface.update_rendering_mode(True, stream_id)
                interface.window.queue_draw()

    # Handling messages from backend
    def message_from_pipeline_callback(self, obj, conn, source):
        istream = conn.get_input_stream()
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
                for interface in self.interfaces:
                    interface.update_stream_prog_list(self.stream_progs)

                # compare received and current analyzed prog lists
                # (compared list contains only program equal prorams
                # from current and received lists)
                compared_prog_list = self.aprogs_control.get_compared_list(
                    prog_list)

                for interface in self.interfaces:
                    if self.is_gui(interface) is True:
                        # get xids from gui
                        xids = interface.get_renderers_xids()

                        # set drawing black background
                        # for corresponding renderers to False
                        # TODO: pass not only stream id, but prog id too,
                        # to disable drawing in only those renderers, that
                        # should be drawn by backend
                        interface.update_rendering_mode(
                                    False, compared_prog_list[0])
                        break
                else:
                    xids = []
                    for prog in compared_prog_list[1]:
                        xids.append([int(compared_prog_list[0]),
                                     int(prog[0]), 0])

                # pass prog list and xids to backend
                self.backend.apply_new_program_list(compared_prog_list, xids)

                # apply analysis params to backend
                self.send_analysis_params_to_backend()

                # write event to log
                self.log.write_log_message("new stream prog list received "
                                           "from backend")

            # measured data for video received from backend
            elif wstr[0] == 'v':
                # translate message from string to list
                vparams = self.msg_translator.get_vparams_list(wstr[1:])
                self.error_detector.eval_video(vparams)
                # update video plot data in gui
                for interface in self.interfaces:
                    if self.is_gui(interface) is True:
                        interface.update_video_plots_data(vparams)

            # measured data for audio received from backend
            elif wstr[0] == 'a':
                # translate message from string to list
                aparams = self.msg_translator.get_aparams_list(wstr[1:])
                self.error_detector.eval_audio(aparams)
                # update lufs levels in program table and plots in gui
                list(map(lambda x: x.update_lufs(aparams), self.interfaces))

            # end of stream message received from backend
            elif wstr[0] == 'e':
                self.end_of_stream_received(int(wstr[1:]))

