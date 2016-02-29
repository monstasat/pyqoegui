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
                                      'table_revealed': 'True',
                                      'language': 'ru'}
            self.write_ini()

    def write_ini(self):
        with open('config.ini', 'w') as configfile:
            self.config.write(configfile)

    def save_prog_list(self, progList):
        try:
            self.config['user']['prog_list'] = str(dark_theme)
        except:
            self.config['user'] = {'prog_list': json.dumps(progList)}

        self.write_ini()

    def load_prog_list(self):
        self.config.read('config.ini')
        try:
            progList = self.config['user']['prog_list']
        except:
            progList = '[]'

        return json.loads(progList)

    def get_dark_theme(self):
        self.config.read('config.ini')
        try:
            dark_theme = self.config['user'].getboolean('dark_theme')
        except:
            print("no dark_theme section")
            dark_theme = False
        return bool(dark_theme)

    def set_dark_theme(self, dark_theme):
        #self.config['prog_list'] = {'analyzed': str(dark_theme)}
        try:
            self.config['user']['dark_theme'] = str(bool(dark_theme))
        except:
            self.config['user'] = {'dark_theme': str(bool(dark_theme))}
        self.write_ini()

