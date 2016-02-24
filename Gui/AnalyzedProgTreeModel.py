import json
from gi.repository import Gtk

class AnalyzedProgTreeModel(Gtk.TreeStore):
	def __init__(self):
		# stream id, icon name, prog name, is selected, is partly selected, prog info
		Gtk.TreeStore.__init__(self, int, str, str, bool, bool, str)

		self.TREE_ICONS = {
				3 : "applications-multimedia",
				1 : "video-x-generic",
				2 : "audio-x-generic",}

	def clear_all_programs(self):
		self.clear()

	def get_selected_programs(self):
		pass

	# show new program list received from backend
	def add_new_programs(self, progList):
		self.clear_all_programs()
		# fill the model
		streams = []
		for prog in progList:
			# get prog params
			stream = prog[0]
			for id in streams:
				if id == stream:
					break
			else:
				streams.append(stream)
		for stream in streams:
			piter = self.append(None, [stream, "view-grid-symbolic", "Поток №" + str(stream + 1), False, False, ""])
			for prog in progList:
				if stream == prog[0]:
					citer = self.append(piter, [ prog[0], self.TREE_ICONS[prog[3]], prog[2], False, False, json.dumps(prog) ] )

		print(streams)
