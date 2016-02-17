class TranslateMessages():
	def __init__(self):
		pass

	def translate_prog_message_from_pipeline(self, progList):
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
		return stream_params

	def translate_prog_list_to_prog_names(self, progList):

		progNames = []
		for stream in progList:
			progs = stream[1]
			for prog in progs:
				progNames.append(prog[1])

		return progNames

