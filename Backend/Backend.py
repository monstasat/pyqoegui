from gi.repository import Gio, GObject
from Backend.GstreamerPipeline import GstreamerPipeline

class Backend(GObject.GObject):
	def __init__(self, streams=1, port=1600):

		self.gs_pipelines = []
		# create gs pipeline instances
		for stream_id in range(streams):
			self.gs_pipelines.append(GstreamerPipeline(stream_id))

	# check if stream id parameter is valid
	def is_pipeline(self, stream_id):
		if (stream_id + 1) > len(self.gs_pipelines):
			return False
		return True

	# restart selected pipeline
	def restart_pipeline(self, stream_id):
		if self.is_pipeline(stream_id) is True:
			self.terminate_pipeline()
			self.start_pipeline()

	# execute selected pipeline
	def start_pipeline(self, stream_id):
		self.restart_pipeline(stream_id)

	# terminate selected pipeline
	def terminate_pipeline(self, stream_id):
		if self.is_pipeline(stream_id) is True:
			self.gs_pipelines[stream_id].terminate()

	# execute all pipelines
	def start_all_pipelines(self):
		for pipeline in self.gs_pipelines:
			pipeline.execute()

	# terminate all pipelines
	def terminate_all_pipelines(self):
		for pipeline in self.gs_pipelines:
			pipeline.terminate()

	# apply new program list
	def apply_new_program_list(self, progList, xids):
		xid_iter = 0
		# iterating over streams in progList
		for stream in progList:
			# if stream with sent number exist
			if self.is_pipeline(stream[0]) is True:
				# determine number of programs in this stream to get necessary number of xids
				progNum = len(stream[1])
				self.gs_pipelines[stream[0]].apply_new_program_list(stream, xids[xid_iter:xid_iter + progNum])
				print(xids[xid_iter:xid_iter + progNum])
				xid_iter = xid_iter + progNum
			
