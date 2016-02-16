# write message to log
from datetime import datetime
import os

# log event types
TYPE_INFO = 0
TYPE_WARNING = 1
TYPE_ERROR = 2

class Log():
    def __init__(self):
        pass

	def write_log_message(msg, from_new_string=False, event_type=TYPE_INFO):
		f = open('log.txt', 'a')

		if event_type == TYPE_INFO:
			type_str = "[info] "
		elif event_type == TYPE_WARNING:
			type_str = "[warning] "
		elif event_type == TYPE_ERROR:
			type_str = "[error] "
		else:
			type_str = "[unknown] "

		time = datetime.now().strftime('[%Y-%m-%d %H:%M:%S] ')
		if from_new_string and (os.stat('log.txt').st_size != 0):
			f.write("\n" + time + type_str + msg + "\n")
		else:
			f.write(time + type_str + msg + "\n")

		f.close()

	# write submessage to log
	def write_log_message_submessage(msg, from_new_string=False):
		f = open('log.txt', 'a')
		if from_new_string and (os.stat('log.txt').st_size != 0):
			f.write("\n" + "\t" + msg + "\n")
		else:
			f.write("\t" + msg + "\n")

		f.close()

