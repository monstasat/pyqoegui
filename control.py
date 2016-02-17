#!/usr/bin/python3
from gi.repository import Gtk, Gio
from struct import pack
# localhost address of gstreamer pipeline
GS_PIPELINE_PORT = 1500

class Control():
	def __init__(self):
		# dividers for byte array with program parameters
		self.BYTE_STREAM_DIVIDER = 0xABBA0000
		self.BYTE_PROG_DIVIDER = 0xACDC0000
		# message headers
		self.HEADER_PROG_LIST = 0xDEADBEEF

	# function that transforms prog list string to byte array
	def prog_string_to_byte(self, progList, xids):
		msg_parts = []

		print(xids)
		# add message header
		msg_parts.append(pack('I', self.HEADER_PROG_LIST))
		# iterate over stream strings
		for stream in progList:
			msg_parts.append(pack('I', self.BYTE_STREAM_DIVIDER))

			progs = stream[1]
			msg_parts.append( pack('I', stream[0]) )
			for i, prog in enumerate(progs):
				msg_parts.append(pack('I', self.BYTE_PROG_DIVIDER))
				msg_parts.append(pack('I', int(prog[0])))
				msg_parts.append(pack('I', xids[i]))
				pids = prog[4]

				for pid in pids:
					msg_parts.append(pack('I', int(pid[0])))

		# add message ending
		msg_parts.append(pack('I', self.HEADER_PROG_LIST))
		print(msg_parts)
		msg = b"".join(msg_parts)
		# return resulting bytearray
		return msg
