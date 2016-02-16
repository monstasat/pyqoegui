#!/usr/bin/python3
from gi.repository import Gtk, Gio
from struct import pack
# localhost address of gstreamer pipeline
GS_PIPELINE_PORT = 1500

		# dividers for byte array with program parameters
		self.BYTE_STREAM_DIVIDER = 0xABBA0000
		self.BYTE_PROG_DIVIDER = 0xACDC0000
		# message headers
		self.HEADER_PROG_LIST = 0xDEADBEEF

import common

class Control():
	def __init__(self):
		pass

	# function that transforms prog list string to byte array
	def prog_string_to_byte(self, progList, xids):
		streams = progList.split(STREAM_DIVIDER)
		msg_parts = []

		# add message header
		msg_parts.append(pack('I', HEADER_PROG_LIST))
		# iterate over stream strings
		for stream in streams[1:]:
			msg_parts.append(pack('I', BYTE_STREAM_DIVIDER))

			progs = stream.split(PROG_DIVIDER)
			msg_parts.append( pack('I', int(progs[0])) )
			for i, prog in enumerate(progs[1:]):
				msg_parts.append(pack('I', BYTE_PROG_DIVIDER))
				params = prog.split(PARAM_DIVIDER)
				params = list(map(int, params))
				params.insert(1, xids[i])
				#msg_parts.append(pack('I'*len(params), *params))
				for param in params:
					msg_parts.append(pack('I', param))

		# add message ending
		msg_parts.append(pack('I', HEADER_PROG_LIST))
		msg = b"".join(msg_parts)
		# return resulting bytearray
		return msg
