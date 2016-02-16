from gi.repository import Gio

class Client():

	def __init__(self):
		pass

	def send_message(self, msg, destination):
		client = Gio.SocketClient.new()
		connection = client.connect_to_host("localhost", destination, None)
		istream = connection.get_input_stream()
		ostream = connection.get_output_stream()

		# send message
		ostream.write(msg)

		# close connection
		connection.close(None)
