#!/usr/bin/python3

from gi.repository import Gtk, Gio

import constants
import basedialog

btn_txt = [">", ">>", "<", "<<"]

TREE_ICONS_SYM = {"ts" : "view-grid-symbolic",
							"program" : "applications-multimedia-symbolic",
							"0" : "video-x-generic-symbolic",
							"1" : "audio-x-generic-symbolic",}

prglist = "0:*:2010:11 РЕН-ТВ:РТРС:2:2011:0:h264:0:2012:1:aac:0:1234:0:*:2020:12 Спас:РТРС:2:2021:0:h264:0:2022:1:aac:0:1234:1	"

TREE_ICONS = {"ts" : "view-grid-symbolic",
							"program" : "applications-multimedia",
							"0" : "video-x-generic",
							"1" : "audio-x-generic",}

PROG_PARAMS = {"number" : 0, "prog_name" : 1, "prov_name" : 2, "pids_num" : 3}
PID_PARAMS = {}

class ProgSelectDlg(basedialog.BaseDialog):

	def __init__(self, parent):
		basedialog.BaseDialog.__init__(self, "Выбор программ для анализа", parent)
		self.set_default_size(500,0)

		#get dialog box
		mainBox = self.get_content_area()

		#adding a button box
		buttonBox = Gtk.ButtonBox()
		buttonBox.set_halign(Gtk.Align.CENTER)
		buttonBox.set_valign(Gtk.Align.CENTER)
		buttonBox.set_orientation(Gtk.Orientation.VERTICAL)
		buttonBox.set_layout(Gtk.ButtonBoxStyle.EXPAND)
		for i in range(4):
			buttonBox.add(Gtk.Button(label=btn_txt[i]))

		#packing elements to dialog
		box = Gtk.Box(vexpand=True, hexpand=True,
									halign=Gtk.Align.FILL, valign=Gtk.Align.FILL)
		box.set_spacing(constants.DEF_COL_SPACING)
		progList = ProgList()
		box.add(progList)

		#add box container to mainBox
		mainBox.add(box)

		self.show_all()

	def on_btn_clicked_apply(self, widget):
		basedialog.BaseDialog.on_btn_clicked_apply(self, widget)

	def get_prog_list(self):
		return "assumed that prog list will be here in the nearest future"

class ProgList(Gtk.TreeView):

	def __init__(self):
		Gtk.TreeView.__init__(self)
		self.set_hexpand(True)
		self.set_vexpand(True)
		self.set_halign(Gtk.Align.FILL)
		self.set_valign(Gtk.Align.FILL)
		self.set_grid_lines(Gtk.TreeViewGridLines.BOTH)
		self.set_show_expanders(True)
		self.set_enable_tree_lines(True)

		#data stored in treeview
		#icon, name, is_analyzed
		store = Gtk.TreeStore(str, str, bool)
		#set the model
		self.set_model(store)

		self.show_prog_list(prglist)

		#the cellrenderer for the first column - icon
		renderer_icon = Gtk.CellRendererPixbuf()
		renderer_icon.set_alignment(0.5, 0.5)

		#the cellrenderer for the first column - text
		renderer_text = Gtk.CellRendererText()
		#renderer_text.set_alignment(0.5, 0.5)

		#the cellrenderer for the second column - toogle
		renderer_check = Gtk.CellRendererToggle()
		renderer_check.set_alignment(0.5, 0.5)

		#create first column
		column_prog = Gtk.TreeViewColumn("Найденные программы")
		column_prog.set_alignment(0.5)
		column_prog.set_expand(True)
		column_prog.pack_start(renderer_icon, False)
		column_prog.pack_start(renderer_text, True)
		column_prog.add_attribute(renderer_icon, "icon-name", 0)
		column_prog.add_attribute(renderer_text, "text", 1)
		#append first column
		self.append_column(column_prog)

		#create second column
		column_check = Gtk.TreeViewColumn("Анализировать?", renderer_check, active=2)
		column_check.set_alignment(0.5)
		column_check.set_expand(False)
		#column_check.pack_start(renderer_check, False)
		#append second column
		self.append_column(column_check)

		self.show_all()

	def show_prog_list(self, progList):
		#get tree model
		store = self.get_model()
		store.clear()

		progs = progList.split(':*:')

		#stream id
			#num
			#name
			#provider
			#pids num
				#pid
				#pid type
				#codec name
				#to be analyzed
			#xid
			#to be analyzed

		#fill the model
		piter = store.append(None, [TREE_ICONS["ts"], "Поток №"+str(int(progs[0])+1), False])
		for i, prog in enumerate(progs[1:]):

			#get prog params
			progParams = prog.split(':')
			progName = progParams[PROG_PARAMS['prog_name']]
			provName = progParams[PROG_PARAMS['prov_name']]
			pidsNum = int(progParams[PROG_PARAMS["pids_num"]])
			progAnalyzed = bool(progParams[4 + 4 + 1])

			ppiter = store.append(piter, [TREE_ICONS["program"], (progName + " (" + provName + ")"), progAnalyzed])
			for j in range(pidsNum):
				pid = progParams[4 + j*4]
				pidType = progParams[5 + j*4]
				codecName = progParams[6 + j*4]
				pidAnalyzed = bool(progParams[7 + j*4])
				print(pid)
				store.append(ppiter, [TREE_ICONS[pidType], "PID " + pid + ", " + codecName , pidAnalyzed])

		#open all program rows
		for row in range(len(store)):
			path = Gtk.TreePath(row)
			self.expand_row(path, False)

	def pack_prog_list_to_string(self):
		pass

