import json
from gi.repository import Gio

class Config():
    def __init__(self):
        pass

    def save_prog_list(self, progList):
        f = open("prog.txt", 'w')
        progStr = json.dumps(progList)
        f.write(progStr)

    def load_prog_list(self):
        try:
            f = open("prog.txt", 'r')
            progStr = f.read()
            progList = json.loads(progStr)
        except:
            progList = []

        return progList
