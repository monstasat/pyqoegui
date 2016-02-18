from Backend.GstreamerPipeline import GstreamerPipeline
from Backend import State

class Backend():
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
		self.start_pipeline(stream_id)

	# execute selected pipeline
	def start_pipeline(self, stream_id):
		if self.is_pipeline(stream_id) is True:
			print("restart pipeline")
			self.gs_pipelines[stream_id].terminate()
			self.gs_pipelines[stream_id].execute()

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

	def get_pipeline_state(self, stream_id):
		if self.is_pipeline(stream_id) is True:
			return self.gs_pipelines[stream_id].state
		else:
			return State.NONEXISTENT


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
				xid_iter = xid_iter + progNum
			
