from gi.repository import Gio
import subprocess
from struct import pack
from Backend import State

class GstreamerPipeline():
    def __init__(self, stream_id):
        # backend process id
        self.stream_id = stream_id
        self.proc = None

        # process state
        self.state = State.TERMINATED

        # constants to construct prog list message
        self.BYTE_STREAM_DIVIDER = 0xABBA0000
        self.BYTE_PROG_DIVIDER = 0xACDC0000
        self.HEADER_PROG_LIST = 0xDEADBEEF

    def execute(self):
        # terminate previously executed process if any
        self.terminate()

        # execute new process
        #ip = "224.1.2." + str(2 + self.stream_id)
        # this is for testing purposes
        ip = "127.0.0.1"
        stream = str(self.stream_id)
        port  = str(1234 + self.stream_id)
        print(ip)
        print(stream)
        print(port)
        self.proc = subprocess.Popen(["ats3-backend", "--stream", stream, "--ip", ip, "--port", port])
        if self.proc != None:
            self.state = State.IDLE
        print("executing pipeline")

    def terminate(self):
        if self.proc != None:
            self.proc.terminate()
            self.proc = None
            self.state = State.TERMINATED
        print("terminating pipeline")

    def apply_new_program_list(self, progList):
        print("applying new prog list for pipeline")

        msg_parts = []

        # add message header and divider
        msg_parts.append(pack('I', self.HEADER_PROG_LIST))
        msg_parts.append(pack('I', self.BYTE_STREAM_DIVIDER))

        # read some list params
        stream_id = progList[0]
        progs = progList[1]

        # checking if settings are really for this particular process
        if self.stream_id == stream_id:
            # pack stream id
            msg_parts.append( pack('I', stream_id) )

            for i, prog in enumerate(progs):
                msg_parts.append(pack('I', self.BYTE_PROG_DIVIDER))
                msg_parts.append(pack('I', int(prog[0])))
                msg_parts.append(pack('I', prog[4]))
                pids = prog[5]

                for pid in pids:
                    msg_parts.append(pack('I', int(pid[0])))

            # add message ending
            msg_parts.append(pack('I', self.HEADER_PROG_LIST))
            msg = b"".join(msg_parts)
            # send message to gstreamer pipeline
            self.send_message_to_pipeline(msg, 1500 + int(stream_id))
            self.state = State.RUNNING

    def send_message_to_pipeline(self, msg, destination):
        # open connection with gstreamer pipeline
        client = Gio.SocketClient.new()
        connection = client.connect_to_host("localhost", destination, None)
        istream = connection.get_input_stream()
        ostream = connection.get_output_stream()
        # send message
        ostream.write(msg)
        # close connection
        connection.close(None)
