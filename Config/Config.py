import json
import configparser

from gi.repository import Gio


class Config():
    def __init__(self):
        self.config = configparser.ConfigParser()
        try:
            f = open('config.ini', 'r')
        except:
            self.config['DEFAULT'] = {'prog_list': '[]',
                                      'dark_theme': 'False',
                                      'table_revealer': 'False',
                                      'language': 'ru',
                                      'plot_info': '[]',
                                      'analysis_settings': '[]'}

            self.config['user'] = {}
            self.write_ini()

    def write_ini(self):
        with open('config.ini', 'w') as configfile:
            self.config.write(configfile)

    def set_prog_list(self, progList):
        print(progList)
        self.config['user']['prog_list'] = json.dumps(progList)
        self.write_ini()

    def get_prog_list(self):
        self.config.read('config.ini')
        progList = self.config['user'].get('prog_list', '[]')

        return json.loads(progList)

    def get_dark_theme(self):
        self.config.read('config.ini')
        dark_theme = self.config['user'].getboolean('dark_theme')
        return bool(dark_theme)

    def set_dark_theme(self, dark_theme):
        self.config['user']['dark_theme'] = str(bool(dark_theme))
        self.write_ini()

    def set_table_revealer(self, table_revealer):
        self.config['user']['table_revealer'] = str(bool(table_revealer))
        self.write_ini()

    def get_table_revealer(self):
        self.config.read('config.ini')
        table_revealer = self.config['user'].getboolean('table_revealer')
        return bool(table_revealer)

    def set_plot_info(self, plot_info):
        for plot in plot_info:
            plot[0][1] = plot[0][1].replace('%', '%%')
        self.config['user']['plot_info'] = json.dumps(plot_info)
        self.write_ini()

    def get_plot_info(self):
        self.config.read('config.ini')
        plot_info = self.config['user'].get('plot_info', '[]')

        return json.loads(plot_info)

    def set_analysis_settings(self, analysis_settings):
        for setting in analysis_settings:
            setting[0] = setting[0].replace('%', '%%')
        self.config['user']['analysis_settings'] = json.dumps(analysis_settings)
        self.write_ini()

    def get_analysis_settings(self):
        self.config.read('config.ini')
        analysis_settings = self.config['user'].get('analysis_settings', '[]')

        return json.loads(analysis_settings)
