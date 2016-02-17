from gi.repository import Gio
import subprocess, os
from struct import pack

class GstreamerPipeline():
	def __init__(self, stream_id):
		# backend process id
		self.stream_id = stream_id
		self.proc = 0

		# constants to construct prog list message
		self.BYTE_STREAM_DIVIDER = 0xABBA0000
		self.BYTE_PROG_DIVIDER = 0xACDC0000
		self.HEADER_PROG_LIST = 0xDEADBEEF

	def execute(self):
		# terminate previously executed process if any
		self.terminate()

		# execute new process
		self.proc = subprocess.Popen(["ats3-backend"])

	def terminate(self):
		if self.proc != 0:
			self.proc.terminate()
			self.proc = 0

	def apply_new_program_list(self, progList, xids):

		msg_parts = []

		# add message header and divider
		msg_parts.append(pack('I', self.HEADER_PROG_LIST))
		msg_parts.append(pack('I', self.BYTE_STREAM_DIVIDER))

		# read some list params
		stream_id = progList[0]
		progs = progList[1]

		# pack stream id
		msg_parts.append( pack('I', stream_id) )

		for i, prog in enumerate(progs):
			msg_parts.append(pack('I', self.BYTE_PROG_DIVIDER))
			msg_parts.append(pack('I', int(prog[0])))
			msg_parts.append(pack('I', xids[i]))
			pids = prog[4]

			for pid in pids:
				msg_parts.append(pack('I', int(pid[0])))

		# add message ending
		msg_parts.append(pack('I', self.HEADER_PROG_LIST))
		msg = b"".join(msg_parts)

		self.send_message_to_pipeline(msg, 1500 + int(stream_id))

	def send_message_to_pipeline(self, msg, destination):
		client = Gio.SocketClient.new()
		connection = client.connect_to_host("localhost", destination, None)
		istream = connection.get_input_stream()
		ostream = connection.get_output_stream()

		# send message
		ostream.write(msg)

		# close connection
		connection.close(None)
