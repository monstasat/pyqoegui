import json
import configparser
import copy
import os

from gi.repository import Gio

from Control import TunerSettingsIndexes as ti

ANALYSIS_DEFAULT = {'vloss': 2, 'aloss': 2,
                    'black_cont_en': True, 'black_cont': 90,
                    'black_peak_en': True, 'black_peak': 100,
                    'luma_cont_en': True, 'luma_cont': 20,
                    'luma_peak_en': True, 'luma_peak': 17,
                    'black_time': 2, 'black_pixel': 16,
                    'freeze_cont_en': True, 'freeze_cont': 90,
                    'freeze_peak_en': True, 'freeze_peak': 100,
                    'diff_cont_en': True, 'diff_cont': 0.1,
                    'diff_peak_en': True, 'diff_peak': 0.02,
                    'freeze_time': 2, 'pixel_diff': 0,
                    'blocky_cont_en': True, 'blocky_cont': 3,
                    'blocky_peak_en': True, 'blocky_peak': 6,
                    'blocky_time': 1,
                    'silence_cont_en': True, 'silence_cont': -35,
                    'silence_peak_en': True, 'silence_peak': -45,
                    'silence_time': 10,
                    'loudness_cont_en': True, 'loudness_cont': -21.9,
                    'loudness_peak_en': True, 'loudness_peak': -15,
                    'loudness_time': 2}


class Config():
    def __init__(self):
        self.config = configparser.ConfigParser()
        home = os.environ.get("HOME")
        self.dir = home + '/.config/analyzer'
        self.filename = self.dir + '/config.ini'

        # create directory if no exist
        if os.path.isdir(self.dir) is False:
            os.makedirs(self.dir)

        try:
            f = open(self.filename, 'r')
        except:
            self.config['DEFAULT'] = {'prog_list': '[]',
                                      'dark_theme': 'False',
                                      'table_revealer': 'False',
                                      'language': 'ru',
                                      'plot_info': '[]',
                                      'analysis_settings': '[]',
                                      'tuner_settings': '[]',
                                      'audio_source': '0'}

            self.config['user'] = {}
            self.write_ini()

    def write_ini(self):
        with open(self.filename, 'w') as configfile:
            self.config.write(configfile)

    def read_ini(self):
        self.config.read(self.filename)

    def set_prog_list(self, progList):
        self.config['user']['prog_list'] = json.dumps(progList)
        self.write_ini()

    def get_prog_list(self):
        self.read_ini()
        progList = self.config['user'].get('prog_list', '[]')

        return json.loads(progList)

    def get_color_theme(self):
        self.read_ini()
        dark_theme = self.config['user'].getboolean('dark_theme')
        return bool(dark_theme)

    def set_color_theme(self, dark_theme):
        self.config['user']['dark_theme'] = str(bool(dark_theme))
        self.write_ini()

    def set_table_revealer(self, table_revealer):
        self.config['user']['table_revealer'] = str(bool(table_revealer))
        self.write_ini()

    def get_table_revealer(self):
        self.read_ini()
        table_revealer = self.config['user'].getboolean('table_revealer')
        return bool(table_revealer)

    def set_plot_info(self, plot_info):
        info = copy.deepcopy(plot_info)
        for plot in info:
            plot[0][1] = plot[0][1].replace('%', '%%')
        self.config['user']['plot_info'] = json.dumps(info)
        self.write_ini()

    def get_plot_info(self):
        self.read_ini()
        plot_info = self.config['user'].get('plot_info', '[]')

        return json.loads(plot_info)

    def set_analysis_settings(self, analysis_settings):
        settings = copy.deepcopy(analysis_settings)
        for setting in settings:
            setting[0] = setting[0].replace('%', '%%')
        self.config['user']['analysis_settings'] = json.dumps(settings)
        self.write_ini()

    def get_analysis_settings(self):
        self.read_ini()
        analysis_settings = self.config['user'].get('analysis_settings', '[]')
        analysis_settings = json.loads(analysis_settings)

        if len(analysis_settings) < len(ANALYSIS_DEFAULT):
            analysis_settings = ANALYSIS_DEFAULT

        return analysis_settings

    def set_tuner_settings(self, tuner_settings):
        self.config['user']['tuner_settings'] = json.dumps(tuner_settings)
        self.write_ini()

    def get_tuner_settings(self):
        self.read_ini()
        tuner_settings = self.config['user'].get('tuner_settings', '[]')
        tuner_settings = json.loads(tuner_settings)

        if len(tuner_settings) < len(ti.DEFAULT_VALUES):
            tuner_settings = ti.DEFAULT_VALUES

        return tuner_settings

    def set_audio_source(self, source):
        self.config['user']['audio_source'] = str(source)
        self.write_ini()

    def get_audio_source(self):
        self.read_ini()
        return int(self.config['user'].get('audio_source', '0'))

