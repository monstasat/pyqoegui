from gi.repository import Gio

class Server():

	def __init__(self, port):
		# server for recieving messages from gstreamer pipeline
		x = ["foo"]
		server = Gio.SocketService.new()
		server.add_inet_port(port, None)
		# x - data to be passed to callback
		server.connect("incoming", self.incoming_callback, x)
		server.start()

	def incoming_callback(self, obj, conn, source, data):
		istream = conn.get_input_stream()
		ostream = conn.get_output_stream()
		buffer = istream.read_bytes(1000)
		data[0] = buffer.get_data()

		#decode string back to unicode
		wstr = data[0].decode('utf-8', 'ignore')
		#print("msg of type '" + wstr[0] + "' received!")
		print(wstr)

		if len(wstr) > 0:
			# if received program list
			if wstr[0] == 'd':
				#self.win.progDlg.show_prog_list(wstr[1:])
				self.parse_prog_list(wstr[1:])
				print("prog message received")
			# if received video parameters
			elif wstr[0] == 'v':
				#self.win.
				pass

	def parse_prog_list(self, progList):
		PROG_DIVIDER = ':*:'
		PARAM_DIVIDER = '^:'
		PROG_PARAMS = {"number" : 0, "prog_name" : 1, "prov_name" : 2, "pids_num" : 3}

		stream_params = []

		progs = progList.split(PROG_DIVIDER)

		# get stream id
		stream_id = int(progs[0])
		stream_params.append(stream_id)

		progs_param_list = []
		for prog in progs[1:]:
			prog_params_list = []
			progParams = prog.split(PARAM_DIVIDER)
			for i in range(4):
				prog_params_list.append(progParams[i])

			pids_params_list = []
			# iterating over program pids
			for i in range( int(prog_params_list[3]) ):

				pid_params_list = []
				for j in range(3):
					pid_params_list.append(progParams[4 + j + 3*i])
				pids_params_list.append(pid_params_list)

			prog_params_list.append(pids_params_list)

			progs_param_list.append(prog_params_list)

		stream_params.append(progs_param_list)

		print(stream_params)

		# get prog params



		
