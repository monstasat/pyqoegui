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
				self.win.progDlg.show_prog_list(wstr[1:])
				print("prog message received")
			# if received video parameters
			elif wstr[0] == 'v':
				#self.win.
				pass
