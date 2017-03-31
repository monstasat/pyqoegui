import os
import subprocess
import os
from struct import pack

from gi.repository import Gio, GObject

from Backend import State


class GstreamerPipeline():
    def __init__(self, stream_id):
        # corresponding stream id
        self.stream_id = stream_id
        # current backend process
        self.proc = None
        # current backend state
        self.state = State.TERMINATED
        # current polling function id
        self.poll_id = None
        # volume values for analyzed programs
        # (stored in list if volume value is more that null)
        self.volumes = []

    def execute(self):
        # terminate previously executed process if any
        try:
            self.terminate()
        except:
            print("failed terminating process with id ",
                  self.stream_id)

        home = os.environ.get("HOME")
        user_name = os.environ.get("USER")
        log_path = home + '/.var/log/' + user_name + '/analyzer/'
        log_stdout = log_path + "out_log_backend_pipeline_" + str(self.stream_id)
        log_stderr = log_path + "err_log_backend_pipeline_" + str(self.stream_id)

        # create directory if no exist
        if os.path.isdir(log_path) is False:
            os.makedirs(log_path)

        # execute new process
        ip = "224.1.2.2" # + str(2 + self.stream_id)
        # this is for testing purposes
        # ip = "127.0.0.1"
        stream = str(self.stream_id)
        port = str(1234 + self.stream_id)
        # print("executing pipeline. ip: ", ip,
        #       "stream: ", stream, "port: ", port)
        out = open(log_stdout, "w")
        err = open(log_stderr, "w")
        self.proc = subprocess.Popen(
                            ["ats3-backend",
                             "--stream", stream,
                             "--ip", ip,
                             "--port", port],
                            stdout=out, stderr=err)

        self.state = State.IDLE
        self.poll_id = GObject.timeout_add(1000, self.poll_pipeline)

    def poll_pipeline(self):
        if self.state != State.TERMINATED:
            if self.proc is not None:
                # poll process
                res = self.proc.poll()
                # if process is terminated, restart
                if res is not None:
                    self.execute()

        return True

    def terminate(self):
        if self.proc is not None:
            self.proc.terminate()
            self.proc.communicate()
            self.proc = None

        if self.poll_id != None:
            GObject.source_remove(self.poll_id)
            self.poll_id = None
        self.state = State.TERMINATED
        # print("terminating pipeline with id ", self.stream_id)

    def apply_new_program_list(self, prog_list):
        # print("applying new prog list for pipeline with id ",
        #       self.stream_id)
        # constants to construct prog list message
        STREAM_DIVIDER = 0xABBA0000
        PROG_DIVIDER = 0xACDC0000
        HEADER = 0xDEADBEEF

        msg = pack("III", HEADER, STREAM_DIVIDER, prog_list[0])

        for prog in prog_list[1]:
            prg = pack('III', PROG_DIVIDER, int(prog[0]), prog[4])
            msg = b''.join([msg, prg])
            for pid in prog[5]:
                msg = b''.join([msg, pack('I', int(pid[0]))])

        msg = b''.join([msg, pack('I', HEADER)])

        # send message to gstreamer pipeline
        self.send_message_to_pipeline(msg, 1500 + int(self.stream_id))
        self.state = State.RUNNING

        def restore_volume():
            list(map(lambda x: self.change_volume(x[0], x[1], x[2]),
                 self.volumes))

        GObject.timeout_add(1000, restore_volume)

    def change_volume(self, prog_id, pid, value):
        HEADER = 0x0EFA1922
        msg = pack("IIIII", HEADER, prog_id, pid, value, HEADER)
        self.send_message_to_pipeline(msg, 1500 + int(self.stream_id))

        for prog in self.volumes:
            if (prog[0] == prog_id) and (prog[1] == pid):
                if value == 0:
                    self.volumes.remove(prog)
                else:
                    prog[2] = value
                break
        else:
            self.volumes.append([prog_id, pid, value])

    # apply new analysis parameters
    def change_analysis_params(self, black_pixel, diff_level, mark_blocks, ad_timeout):
        HEADER = 0xCDDA1307
        BLACK_PIX = 0xBA1306BA
        PIXEL_DIFF = 0xDA0476AD
        MARK_BLOCKS = 0xCA12AD86
        AD_TIMEOUT = 0x1F2AB83D

        msg = pack("IIII", HEADER, BLACK_PIX, black_pixel, HEADER)
        self.send_message_to_pipeline(msg, 1500 + int(self.stream_id))

        msg = pack("IIII", HEADER, PIXEL_DIFF, diff_level, HEADER)
        self.send_message_to_pipeline(msg, 1500 + int(self.stream_id))

        msg = pack("IIII", HEADER, MARK_BLOCKS, mark_blocks, HEADER)
        self.send_message_to_pipeline(msg, 1500 + int(self.stream_id))

        msg = pack("IIII", HEADER, AD_TIMEOUT, ad_timeout, HEADER)
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

