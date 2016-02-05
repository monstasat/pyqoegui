#!/usr/bin/python
from gi.repository import Gtk

#maximum number of analyzed programs
MAX_ANALYZED_PROG_NUM = 10
#number of video/audio parameters measured
PARAMETERS_NUM = 7
#table rows number
ROWS_NUM = 1 + MAX_ANALYZED_PROG_NUM
COLS_NUM = 3 + PARAMETERS_NUM

import constants

#def map_color(param):
#	return clrs[param]

#class for viewing current program status (such as artifacts/loudndess) in a table
class ProgramTable(Gtk.TreeView):

	table_heading = []

	clrs = {'1' : '#80FF80', '2': '#FFFF80', '3': '#FF7878', '0' : 'FFFFFF'}
	stattxt = {'0' : "", '2' : "Опасно", '3' : "Брак"}
	print("ok")
	test = ([1, '#FFFFFF', constants.prog_names[0], '#FFFFFF', '%g'%(-22.9), '#FFFFFF', stattxt["0"], clrs['1'], stattxt["0"], clrs['1'], stattxt["0"], clrs['1'], stattxt["0"], clrs['1'], stattxt["0"], clrs['1'], stattxt["0"], clrs['1'], stattxt["0"], clrs['1']],
			[3, '#FFFFFF', constants.prog_names[1], '#FFFFFF', '%g'%(-20.4), '#FFFFFF', stattxt["0"], clrs['1'], stattxt["0"], clrs['1'], stattxt["2"], clrs['2'], stattxt["0"], clrs['1'], stattxt["0"], clrs['1'], stattxt["0"], clrs['1'], stattxt["0"], clrs['1']],
			[2, '#FFFFFF', constants.prog_names[2], '#FFFFFF', '%g'%(-21.2), '#FFFFFF', stattxt["0"], clrs['1'], stattxt["0"], clrs['1'], stattxt["2"], clrs['2'], stattxt["0"], clrs['1'], stattxt["0"], clrs['1'], stattxt["0"], clrs['1'], stattxt["0"], clrs['1']],
			[4, '#FFFFFF', constants.prog_names[3], '#FFFFFF', '%g'%(-19.1), '#FFFFFF', stattxt["0"], clrs['1'], stattxt["0"], clrs['1'], stattxt["2"], clrs['2'], stattxt["0"], clrs['1'], stattxt["0"], clrs['1'], stattxt["0"], clrs['1'], stattxt["0"], clrs['1']],
			[5, '#FFFFFF', constants.prog_names[4], '#FFFFFF', '%g'%(-22.4), '#FFFFFF', stattxt["0"], clrs['1'], stattxt["0"], clrs['1'], stattxt["3"], clrs['3'], stattxt["0"], clrs['1'], stattxt["0"], clrs['1'], stattxt["0"], clrs['1'], stattxt["0"], clrs['1']],
			[6, '#FFFFFF', constants.prog_names[5], '#FFFFFF', '%g'%(-12.4), '#FFFFFF', stattxt["0"], clrs['1'], stattxt["0"], clrs['1'], stattxt["2"], clrs['2'], stattxt["0"], clrs['1'], stattxt["0"], clrs['1'], stattxt["0"], clrs['1'], stattxt["0"], clrs['1']],
			[7, '#FFFFFF', constants.prog_names[6], '#FFFFFF', '%g'%(-32.5), '#FFFFFF', stattxt["0"], clrs['1'], stattxt["0"], clrs['1'], stattxt["2"], clrs['2'], stattxt["0"], clrs['1'], stattxt["0"], clrs['1'], stattxt["0"], clrs['1'], stattxt["0"], clrs['1']],
			[8, '#FFFFFF', constants.prog_names[7], '#FFFFFF', '%g'%(-18.8), '#FFFFFF', stattxt["0"], clrs['1'], stattxt["0"], clrs['1'], stattxt["2"], clrs['2'], stattxt["0"], clrs['1'], stattxt["0"], clrs['1'], stattxt["0"], clrs['1'], stattxt["0"], clrs['1']],
			[9, '#FFFFFF', constants.prog_names[8], '#FFFFFF', '%g'%(-22.6), '#FFFFFF', stattxt["0"], clrs['1'], stattxt["0"], clrs['1'], stattxt["2"], clrs['2'], stattxt["0"], clrs['1'], stattxt["0"], clrs['1'], stattxt["0"], clrs['1'], stattxt["0"], clrs['1']],
			[10, '#FFFFFF',constants.prog_names[9], '#FFFFFF', '%g'%(-20.7), '#FFFFFF', stattxt["0"], clrs['1'], stattxt["0"], clrs['1'], stattxt["2"], clrs['2'], stattxt["0"], clrs['1'], stattxt["0"], clrs['1'], stattxt["0"], clrs['1'], stattxt["0"], clrs['1']])
	print("not ok")
	def __init__(self):
		Gtk.TreeView.__init__(self)
		self.set_hexpand_set(True)
		self.set_hexpand(True)
		self.set_halign(Gtk.Align.FILL)
		self.set_valign(Gtk.Align.END)
		self.set_grid_lines(3)
		# list sore : 				n; name; lufs;  vl;   bf; frz; blck; al; sil; loud
		self.store = Gtk.ListStore(int, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str)
		print("success")
		print(enumerate(constants.heading_labels))
		self.set_model(self.store)
		for i in self.test:
			treeiter = self.store.append(list(i))

		for i in range(0, 20, 2):
			color = i + 1
			#3rd column is a progress bar for lufs levels
			if i == 4:
				renderer = Gtk.CellRendererProgress()
				renderer.props.inverted = True
				column = Gtk.TreeViewColumn(constants.heading_labels[int(i/2)], renderer, text=i)
			#other colums are text labels
			else:
				renderer = Gtk.CellRendererText()
				renderer.set_alignment(0.5, 0.5)
				column = Gtk.TreeViewColumn(constants.heading_labels[int(i/2)], renderer, text=i, background=color)
			if i > 0:
				column.set_expand(1)
			self.append_column(column)



