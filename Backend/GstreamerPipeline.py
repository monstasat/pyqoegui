import subprocess
from struct import pack

from gi.repository import Gio, GObject

from Backend import State


class GstreamerPipeline():
    def __init__(self, stream_id):
        self.stream_id = stream_id
        self.proc = None
        self.state = State.TERMINATED

        self.polling_flag = False

    def execute(self):
        # terminate previously executed process if any
        self.terminate()

        # execute new process
        ip = "224.1.2." + str(2 + self.stream_id)
        # this is for testing purposes
        #ip = "127.0.0.1"
        stream = str(self.stream_id)
        port = str(1234)
        print("executing pipeline")
        print("ip: ", ip)
        print("stream: ", stream)
        print("port: ", port)
        out = open("backend_log", "w")
        err = open("backend_err_log", "w")
        self.proc = subprocess.Popen(
                            ["ats3-backend",
                             "--stream", stream,
                             "--ip", ip,
                             "--port", port],
                            stdout=out, stderr=err)

        if self.proc is not None:
            self.state = State.IDLE
            self.polling_flag = True
            GObject.timeout_add(1000, self.poll_pipeline)

    def poll_pipeline(self):
        if self.state != State.TERMINATED:
            if self.proc is not None:
                # poll process
                res = self.proc.poll()
                # if process is terminated, restart
                if res is not None:
                    self.terminate()
                    self.execute()

        return self.polling_flag

    def terminate(self):
        if self.proc is not None:
            self.proc.terminate()
            self.proc.communicate()
            self.proc = None
            self.state = State.TERMINATED
        self.polling_flag = False
        print("terminating pipeline")

    def apply_new_program_list(self, prog_list):
        print("applying new prog list for pipeline")
        # constants to construct prog list message
        STREAM_DIVIDER = 0xABBA0000
        PROG_DIVIDER = 0xACDC0000
        HEADER = 0xDEADBEEF

        msg = pack("II", HEADER, STREAM_DIVIDER)

        for prog in prog_list[1]:
            prg = pack('IIII',
                       prog_list[0], PROG_DIVIDER, int(prog[0]), prog[4])
            msg = b''.join([msg, prg])
            for pid in prog[5]:
                msg = b''.join([msg, pack('I', int(pid[0]))])

        msg = b''.join([msg, pack('I', HEADER)])

        # send message to gstreamer pipeline
        self.send_message_to_pipeline(msg, 1500 + int(self.stream_id))
        self.state = State.RUNNING

    def change_volume(self, prog_id, pid, value):
        HEADER = 0x0EFA1922
        msg = pack("IIIII", HEADER, prog_id, pid, value, HEADER)
        self.send_message_to_pipeline(msg, 1500 + int(self.stream_id))

    # apply new analysis parameters
    def change_analysis_params(self, black_pixel, diff_level):
        HEADER = 0xCDDA1307
        BLACK_PIX = 0xBA1306BA
        PIXEL_DIFF = 0xDA0476AD

        msg = pack("IIII", HEADER, BLACK_PIX, black_pixel, HEADER)
        self.send_message_to_pipeline(msg, 1500 + int(self.stream_id))

        msg = pack("IIII", HEADER, PIXEL_DIFF, diff_level, HEADER)
        self.send_message_to_pipeline(msg, 1500 + int(self.stream_id))

    def send_message_to_pipeline(self, msg, destination):
        # open connection with gstreamer pipeline
        # if pipeline is not terminated
        if self.state is not State.TERMINATED:
            client = Gio.SocketClient.new()
            connection = client.connect_to_host("localhost", destination, None)
            # send message
            connection.get_output_stream().write(msg)
            # close connection
            connection.close(None)

