class TranslateMessages():
	def __init__(self):
		pass

	def translate_prog_string_to_prog_list(self, progList):
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
				# if prog name and provider name are not determined
				if (i == 1) and (progParams[i] == "(null)"):
					progParams[i] = "Неизвестное имя"
				if (i == 2) and (progParams[i] == "(null)"):
					progParams[i] = "Неизвестный провайдер"
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

	def translate_prog_list_to_compared_prog_list(self, progList, gsProgList):
		# new prog list after comparison
		compared_list = []

		# iterating over streams in saved prog list
		for stream in progList:
			compared_stream = []
			# in case if received stream exists in saved prog list
			if stream[0] == gsProgList[0]:

				compared_stream.append(stream[0])
				progs = stream[1]
				compared_progs = []
				for gsProg in gsProgList[1]:
					compared_prog = []

					progNum = len(progs)
					# search for the same program
					i = 0

					while progNum != 0:
						# if found selected program in received list
						if gsProg[0] == progs[i][0]:

							pids = progs[i][4]
							compared_pids = []
							for gsPid in gsProg[4]:

								pidsNum = len(pids)
								# search for the same pid
								j = 0
								while pidsNum != 0:
									# if found selected pid in received list
									if (gsPid[0] == pids[j][0]) and (gsPid[2] == pids[j][2]):
									# same pid found!
										compared_pids.append(pids[j])
										break
									pidsNum = pidsNum - 1
									j = j + 1

							# if equivalent program was found, exit from while
							compared_prog.append(progs[i][0])
							compared_prog.append(progs[i][1])
							compared_prog.append(progs[i][2])
							compared_prog.append(progs[i][3])
							compared_prog.append(compared_pids)
							compared_progs.append(compared_prog)
							break
						progNum = progNum - 1
						i = i + 1
				compared_stream.append(compared_progs)

				# exit from for loop because we've found the stream
				break

		compared_list.append(compared_stream)

		return compared_list

	def translate_prog_list_to_prog_names(self, progList):

		progNames = []
		for stream in progList:
			progs = stream[1]
			for prog in progs:
				progNames.append(prog[1])

		return progNames

	def translate_prog_list_to_stream_ids(self, progList):

		stream_ids = []
		for stream in progList:
			stream_ids.append(stream[0])

		return stream_ids

