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
from constants import create_icon_from_name

#class for viewing current program status (such as artifacts/loudndess) in a table
class ProgramTable(Gtk.TreeView):

	#table heading array
	table_heading = []

	#associates status code with a cell color
	clrs = {'1' : '#80FF80', '2': '#FFFF80', '3': '#FF7878', '0' : 'FFFFFF'}

	#associates status code with a cell text (temporary)
	stattxt = {'1' : "", '2' : "Опасно", '3' : "Брак"}

	test = ([1, '#FFFFFF', constants.prog_names[0], '#FFFFFF', '%g'%(-22.9), '#FFFFFF', stattxt["1"], clrs['1'], stattxt["1"], clrs['1'], stattxt["1"], clrs['1'], stattxt["1"], clrs['1'], stattxt["1"], clrs['1'], stattxt["1"], clrs['1'], stattxt["1"], clrs['1']],
			[2, '#FFFFFF', constants.prog_names[1], '#FFFFFF', '%g'%(-20.4), '#FFFFFF', stattxt["1"], clrs['1'], stattxt["1"], clrs['1'], stattxt["2"], clrs['2'], stattxt["1"], clrs['1'], stattxt["1"], clrs['1'], stattxt["1"], clrs['1'], stattxt["1"], clrs['1']],
			[3, '#FFFFFF', constants.prog_names[2], '#FFFFFF', '%g'%(-21.2), '#FFFFFF', stattxt["1"], clrs['1'], stattxt["1"], clrs['1'], stattxt["2"], clrs['2'], stattxt["1"], clrs['1'], stattxt["1"], clrs['1'], stattxt["1"], clrs['1'], stattxt["1"], clrs['1']],
			[4, '#FFFFFF', constants.prog_names[3], '#FFFFFF', '%g'%(-19.1), '#FFFFFF', stattxt["1"], clrs['1'], stattxt["1"], clrs['1'], stattxt["2"], clrs['2'], stattxt["1"], clrs['1'], stattxt["1"], clrs['1'], stattxt["1"], clrs['1'], stattxt["1"], clrs['1']],
			[5, '#FFFFFF', constants.prog_names[4], '#FFFFFF', '%g'%(-22.4), '#FFFFFF', stattxt["1"], clrs['1'], stattxt["1"], clrs['1'], stattxt["3"], clrs['3'], stattxt["1"], clrs['1'], stattxt["1"], clrs['1'], stattxt["1"], clrs['1'], stattxt["1"], clrs['1']],
			[6, '#FFFFFF', constants.prog_names[5], '#FFFFFF', '%g'%(-12.4), '#FFFFFF', stattxt["1"], clrs['1'], stattxt["1"], clrs['1'], stattxt["2"], clrs['2'], stattxt["1"], clrs['1'], stattxt["1"], clrs['1'], stattxt["1"], clrs['1'], stattxt["1"], clrs['1']],
			[7, '#FFFFFF', constants.prog_names[6], '#FFFFFF', '%g'%(-32.5), '#FFFFFF', stattxt["1"], clrs['1'], stattxt["1"], clrs['1'], stattxt["2"], clrs['2'], stattxt["1"], clrs['1'], stattxt["1"], clrs['1'], stattxt["1"], clrs['1'], stattxt["1"], clrs['1']],
			[8, '#FFFFFF', constants.prog_names[7], '#FFFFFF', '%g'%(-18.8), '#FFFFFF', stattxt["1"], clrs['1'], stattxt["1"], clrs['1'], stattxt["2"], clrs['2'], stattxt["1"], clrs['1'], stattxt["1"], clrs['1'], stattxt["1"], clrs['1'], stattxt["1"], clrs['1']],
			[9, '#FFFFFF', constants.prog_names[8], '#FFFFFF', '%g'%(-22.6), '#FFFFFF', stattxt["1"], clrs['1'], stattxt["1"], clrs['1'], stattxt["2"], clrs['2'], stattxt["1"], clrs['1'], stattxt["1"], clrs['1'], stattxt["1"], clrs['1'], stattxt["1"], clrs['1']],
			[10, '#FFFFFF',constants.prog_names[9], '#FFFFFF', '%g'%(-20.7), '#FFFFFF', stattxt["1"], clrs['1'], stattxt["1"], clrs['1'], stattxt["2"], clrs['2'], stattxt["1"], clrs['1'], stattxt["1"], clrs['1'], stattxt["1"], clrs['1'], stattxt["1"], clrs['1']],
			[11, '#FFFFFF', constants.prog_names[1], '#FFFFFF', '%g'%(-20.4), '#FFFFFF', stattxt["1"], clrs['1'], stattxt["1"], clrs['1'], stattxt["2"], clrs['2'], stattxt["1"], clrs['1'], stattxt["1"], clrs['1'], stattxt["1"], clrs['1'], stattxt["1"], clrs['1']],
			[12, '#FFFFFF', constants.prog_names[2], '#FFFFFF', '%g'%(-21.2), '#FFFFFF', stattxt["1"], clrs['1'], stattxt["1"], clrs['1'], stattxt["2"], clrs['2'], stattxt["1"], clrs['1'], stattxt["1"], clrs['1'], stattxt["1"], clrs['1'], stattxt["1"], clrs['1']],
			[13, '#FFFFFF', constants.prog_names[3], '#FFFFFF', '%g'%(-19.1), '#FFFFFF', stattxt["1"], clrs['1'], stattxt["1"], clrs['1'], stattxt["2"], clrs['2'], stattxt["1"], clrs['1'], stattxt["1"], clrs['1'], stattxt["1"], clrs['1'], stattxt["1"], clrs['1']],
			[14, '#FFFFFF', constants.prog_names[4], '#FFFFFF', '%g'%(-22.4), '#FFFFFF', stattxt["1"], clrs['1'], stattxt["1"], clrs['1'], stattxt["3"], clrs['3'], stattxt["1"], clrs['1'], stattxt["1"], clrs['1'], stattxt["1"], clrs['1'], stattxt["1"], clrs['1']],
			[15, '#FFFFFF', constants.prog_names[5], '#FFFFFF', '%g'%(-12.4), '#FFFFFF', stattxt["1"], clrs['1'], stattxt["1"], clrs['1'], stattxt["2"], clrs['2'], stattxt["1"], clrs['1'], stattxt["1"], clrs['1'], stattxt["1"], clrs['1'], stattxt["1"], clrs['1']],
			[16, '#FFFFFF', constants.prog_names[6], '#FFFFFF', '%g'%(-32.5), '#FFFFFF', stattxt["1"], clrs['1'], stattxt["1"], clrs['1'], stattxt["2"], clrs['2'], stattxt["1"], clrs['1'], stattxt["1"], clrs['1'], stattxt["1"], clrs['1'], stattxt["1"], clrs['1']],
			[17, '#FFFFFF', constants.prog_names[7], '#FFFFFF', '%g'%(-18.8), '#FFFFFF', stattxt["1"], clrs['1'], stattxt["1"], clrs['1'], stattxt["2"], clrs['2'], stattxt["1"], clrs['1'], stattxt["1"], clrs['1'], stattxt["1"], clrs['1'], stattxt["1"], clrs['1']],
			[18, '#FFFFFF', constants.prog_names[8], '#FFFFFF', '%g'%(-22.6), '#FFFFFF', stattxt["1"], clrs['1'], stattxt["1"], clrs['1'], stattxt["2"], clrs['2'], stattxt["1"], clrs['1'], stattxt["1"], clrs['1'], stattxt["1"], clrs['1'], stattxt["1"], clrs['1']],
			[19, '#FFFFFF', constants.prog_names[9], '#FFFFFF', '%g'%(-20.7), '#FFFFFF', stattxt["1"], clrs['1'], stattxt["1"], clrs['1'], stattxt["2"], clrs['2'], stattxt["1"], clrs['1'], stattxt["1"], clrs['1'], stattxt["1"], clrs['1'], stattxt["1"], clrs['1']],
			[20, '#FFFFFF', constants.prog_names[9], '#FFFFFF', '%g'%(-20.7), '#FFFFFF', stattxt["1"], clrs['1'], stattxt["1"], clrs['1'], stattxt["2"], clrs['2'], stattxt["1"], clrs['1'], stattxt["1"], clrs['1'], stattxt["1"], clrs['1'], stattxt["1"], clrs['1']])

	def __init__(self, progNum):
		Gtk.TreeView.__init__(self)

		#our table should be horizontally expandable
		self.set_hexpand(True)
		self.set_halign(Gtk.Align.FILL)

		#our table should be attached to the bottom of main app window
		self.set_vexpand(False)
		self.set_valign(Gtk.Align.END)

		#table should be with horizontal and vertical lines that divide cells
		self.set_grid_lines(Gtk.TreeViewGridLines.BOTH)

		#attaching list store to tree view widget
		# list sore : 				n; name; lufs;  vl;   bf; frz; blck; al; sil; loud
		self.store = Gtk.ListStore(int, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str)
		self.set_model(self.store)

		#constructing columns and cells of the table
		for i in range(0, 20, 2):

			#i - index of cell in list store describing cell text
			#color - index of cell in list store describing background color
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
				#setting parameters for artifact columns
				if i > 4:
					#setting column text color - black
					renderer.set_property("foreground", "black")
					column = Gtk.TreeViewColumn(constants.heading_labels[int(i/2)], renderer, text=i, background=color)

					#all artifact columns should have the same width
					column.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
					column.set_fixed_width(100)
				#setting parameters for the rest columns
				else:
					column = Gtk.TreeViewColumn(constants.heading_labels[int(i/2)], renderer, text=i)

			#all columns besides first are expandable
			if i > 0:
				column.set_expand(1)

			#placing column name in the center
			column.set_alignment(0.5)
			#adding column to treeview
			self.append_column(column)

	def add_rows(self, progNum, rowsData):
		store = self.get_model()
		store.clear()
		for i in range(progNum):
			treeiter = store.append(rowsData[i])
		print("rows added: " + str(progNum))

	def add_single_row(self, rowNum, rowData):
		store = self.get_model()
		store.append(rowData, rowNum)

