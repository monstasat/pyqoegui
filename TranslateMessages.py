class TranslateMessages():
	def __init__(self):
		pass

################################ PROG LIST #####################################

	# add received prog list to common prog list
	def append_prog_list_to_common(self, progList, commonProgList):
		for i, stream in enumerate(commonProgList):
			if stream[0] == progList[0]:
				commonProgList[i] = progList
				break
		else:
			commonProgList.append(progList)

		return commonProgList

	# convert program string to program list
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

	# compare two prog lists and make new list with only equal programs
	def translate_prog_list_to_compared_prog_list(self, progList, gsProgList):
		# new prog list after comparison
		compared_list = []
		# append stream id
		compared_list.append(gsProgList[0])

		compared_progs = []
		# iterating over streams in saved prog list
		for stream in progList:
			# in case if received stream exists in saved prog list
			if stream[0] == gsProgList[0]:
				progs = stream[1]

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

				# exit from for loop because we've found the stream
				break
		compared_list.append(compared_progs)

		return compared_list

	# extract program ids and names from prog list
	def translate_prog_list_to_gui_prog_info(self, progList):

		guiProgInfo = []
		for stream in progList:
			stream_id = stream[0]
			progs = stream[1]
			for prog in progs:
				prog_info = [stream_id, prog[0], prog[1]]
				pids = prog[4]
				pids_info = []
				prog_type = 0
				for pid in pids:
					type = pid[2]
					if type.split('-')[0] == 'video':
						prog_type = prog_type | 1
					elif type.split('-')[0] == 'audio':
						prog_type = prog_type | 2
					pids_info.append([pid[0], type])
				prog_info.append(prog_type)
				prog_info.append(pids_info)
				guiProgInfo.append(prog_info)

		return guiProgInfo

	# extract stream ids from prog list
	def translate_prog_list_to_stream_ids(self, progList):

		stream_ids = []
		for stream in progList:
			stream_ids.append(stream[0])

		return stream_ids

	def combine_prog_list_with_xids(self, progList, xids):
		stream_id = progList[0]
		progs = progList[1]
		combined_stream = []
		combined_stream.append(stream_id)
		combined_progs = []
		for prog in progs:
			i = 0

			while i != len(xids):
								# stream id					# prog id
				if (stream_id == xids[i][0]) and (prog[0] == xids[i][1]):
					prog.insert(4, xids[i][2])
					combined_progs.append(prog)
				i += 1

		combined_stream.append(combined_progs)

		return combined_stream


############################# VIDEO PARAMETERS #################################

	def translate_vparams_string_to_list(self, vparams_string):
		PART_DIVIDER = ':*:'
		PARAM_DIVIDER = ':'

		param_list = []

		# split string to stream params and video params
		str_parts  = vparams_string.split(PART_DIVIDER)
		# split stream parameters
		stream_params = str_parts[0].split(PARAM_DIVIDER)
		sparams_int = []
		for param in stream_params:
			sparams_int.append(int(param))

		param_list.append(sparams_int)


		video_params_pack = [[], [], [], [], []]
		for params_single_frame in str_parts[1:]:
			# split params string to separate parameters
			video_params = params_single_frame.split(PARAM_DIVIDER)
			for i, param in enumerate(video_params):
				video_params_pack[i].append(float(param))

		# append parameter list to vparam list
		param_list.append(video_params_pack)

		return param_list




