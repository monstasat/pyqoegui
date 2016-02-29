import json
import configparser

from gi.repository import Gio


class Config():
    def __init__(self):
        pass

    def write_ini(self, config):
        with open('config.ini', 'a') as configfile:
            config.write(configfile)

    def save_prog_list(self, progList):
        config = configparser.ConfigParser()
        config['prog_list'] = {'analyzed': json.dumps(progList)}
        self.write_ini(config)

    def load_prog_list(self):
        try:
            config = configparser.ConfigParser()
            config.read('config.ini')
            progList = config['prog_list']['analyzed']
        except:
            progList = '[]'

        return json.loads(progList)

    def get_dark_theme(self):
        pass

    def set_dark_theme(self, dark_theme):
        print(dark_theme)
        config = configparser.ConfigParser()
        print(config.sections())
        for section in config.sections():
            if section == 'gui':
                break
        else:
            config['gui'] = {'dark_theme': dark_theme}

        key = config['gui']
        key['dark_theme'] = str(dark_theme)
        self.write_ini(config)

