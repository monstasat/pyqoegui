import subprocess
from struct import pack

from gi.repository import Gio

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

        self.HEADER_SOUND = 0x0EFA1922

        self.HEADER_VIDEO_PARAMS = 0xCDDA1307
        self.TYPE_BLACK_PIX = 0xBA1306BA
        self.TYPE_PIXEL_DIFF = 0xDA0476AD

    def execute(self):
        # terminate previously executed process if any
        self.terminate()

        # execute new process
        ip = "224.1.2." + str(2 + self.stream_id)
        # this is for testing purposes
        #ip = "127.0.0.1"
        stream = str(self.stream_id)
        port = str(1234)
        print(ip)
        print(stream)
        print(port)
        self.proc = subprocess.Popen(
                            ["ats3-backend",
                             "--stream",
                             stream,
                             "--ip",
                             ip,
                             "--port",
                             port]
                                    )
        if self.proc is not None:
            self.state = State.IDLE
        print("executing pipeline")

    def terminate(self):
        if self.proc is not None:
            self.proc.terminate()
            self.proc.communicate()
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
            msg_parts.append(pack('I', stream_id))

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
            self.send_message_to_pipeline(msg, 1500 + int(self.stream_id))
            self.state = State.RUNNING

    def send_message_to_pipeline(self, msg, destination):
        # open connection with gstreamer pipeline
        # if pipeline is not terminated
        if self.state is not State.TERMINATED:
            client = Gio.SocketClient.new()
            connection = client.connect_to_host("localhost", destination, None)
            istream = connection.get_input_stream()
            ostream = connection.get_output_stream()
            # send message
            ostream.write(msg)
            # close connection
            connection.close(None)

    def change_volume(self, prog_id, pid, value):
        msg_parts = []

        # add message header
        msg_parts.append(pack('I', self.HEADER_SOUND))

        # add message parameters
        msg_parts.append(pack('I', prog_id))
        msg_parts.append(pack('I', pid))
        msg_parts.append(pack('I', value))

        # add message ending
        msg_parts.append(pack('I', self.HEADER_SOUND))
        msg = b"".join(msg_parts)

        # send message to gstreamer pipeline
        self.send_message_to_pipeline(msg, 1500 + int(self.stream_id))

    # apply new analysis parameters
    def change_analysis_params(self, black_pixel, diff_level):

        msg_parts = []

        # add message header
        msg_parts.append(pack('I', self.HEADER_VIDEO_PARAMS))
        # add param type and param
        msg_parts.append(pack('I', self.TYPE_BLACK_PIX))
        msg_parts.append(pack('I', black_pixel))
        # add message ending
        msg_parts.append(pack('I', self.HEADER_VIDEO_PARAMS))
        msg = b"".join(msg_parts)

        # send message to gstreamer pipeline
        self.send_message_to_pipeline(msg, 1500 + int(self.stream_id))

        msg_parts = []

        # add message header
        msg_parts.append(pack('I', self.HEADER_VIDEO_PARAMS))
        # add param type and param
        msg_parts.append(pack('I', self.TYPE_PIXEL_DIFF))
        msg_parts.append(pack('I', diff_level))
        # add message ending
        msg_parts.append(pack('I', self.HEADER_VIDEO_PARAMS))
        msg = b"".join(msg_parts)

        # send message to gstreamer pipeline
        self.send_message_to_pipeline(msg, 1500 + int(self.stream_id))

