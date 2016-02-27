# write message to log
from datetime import datetime
import os

# log event types
TYPE_INFO = 0
TYPE_WARNING = 1
TYPE_ERROR = 2

class Log():
    def __init__(self, filename):
        self.filename = filename
        # create new file or rewrite old file with same name
        f = open(self.filename, 'w')

    # write message to log file
    def write_log_message(self, msg, from_new_line=False, event_type=TYPE_INFO):

        # continue writing to a file
        f = open(self.filename, 'a')

        # setting log event type ('info' by default)
        if event_type == TYPE_INFO:
            type_str = "[info] "
        elif event_type == TYPE_WARNING:
            type_str = "[warning] "
        elif event_type == TYPE_ERROR:
            type_str = "[error] "
        else:
            type_str = "[unknown] "

        # getting event time
        time = datetime.now().strftime('[%Y-%m-%d %H:%M:%S] ')

        # writing log message to a file
        # is file is not empty and 'start from new line' flag is set,
        # write the message with one blank line above
        if from_new_line and (os.stat('log.txt').st_size != 0):
            f.write("\n" + time + type_str + msg + "\n")
        else:
            f.write(time + type_str + msg + "\n")

        f.close()

    # write submessage to log file
    def write_log_message_submessage(self, msg, from_new_line=False):

        # continue writing to a file
        f = open('log.txt', 'a')

        # writing log submessage to a file
        # is file is not empty and 'start from new line' flag is set,
        # write the message with one blank line above
        if from_new_line and (os.stat('log.txt').st_size != 0):
            f.write("\n" + "\t" + msg + "\n")
        else:
            f.write("\t" + msg + "\n")

        f.close()

