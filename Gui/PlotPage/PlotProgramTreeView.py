from gi.repository import Gtk

class PlotProgramTreeView(Gtk.TreeView):
	def __init__(self, store):
		Gtk.TreeView.__init__(self)

		sel = self.get_selection()
		sel.set_mode(Gtk.SelectionMode.NONE)

		# remember store
		self.store = store
		# set store for view
		self.set_model(self.store)

		# the cellrenderer for the first column - icon
		renderer_icon = Gtk.CellRendererPixbuf()
		renderer_icon.set_alignment(0.5, 0.5)

		# the cellrenderer for the first column - text
		renderer_text = Gtk.CellRendererText()

		# the cellrenderer for the second column - toogle
		renderer_check = Gtk.CellRendererToggle()
		renderer_check.set_alignment(0.5, 0.5)
		renderer_check.connect('toggled', self.on_toggled)

		# create first column
		column_prog = Gtk.TreeViewColumn("Анализируемые программы")
		column_prog.set_alignment(0.5)
		column_prog.set_expand(True)
		column_prog.pack_start(renderer_icon, False)
		column_prog.pack_start(renderer_text, True)
		column_prog.add_attribute(renderer_icon, "icon-name", 1)
		column_prog.add_attribute(renderer_text, "text", 2)
		# append first column
		self.append_column(column_prog)

		# create second column
		column_check = Gtk.TreeViewColumn("Отображать?")
		column_check.set_alignment(0.5)
		column_check.set_expand(False)
		column_check.pack_start(renderer_check, False)
		column_check.add_attribute(renderer_check, "active", 3)
		column_check.add_attribute(renderer_check, "inconsistent", 4)
		# append second column
		self.append_column(column_check)

	def on_toggled(self, widget, path):
		# the boolean value of the selected row
		current_value = self.store[path][3]
		# change the boolean value of the selected row in the model
		self.store[path][3] = not current_value
		# new current value!
		current_value = not current_value

		# if length of the path is 1 (that is, if we are selecting a stream)
		if len(path) == 1:
			# get the iter associated with the stream path
			streamIter = self.store.get_iter(path)
			# inconsistent state is not valid when selecting a stream
			self.store[streamIter][4] = False
			# get the iter associated with its first child (program)
			progIter = self.store.iter_children(streamIter)
			# while there are programs, change the state of their boolean value
			while progIter is not None:
				self.store[progIter][3] = current_value
				# inconsistent state is not valid when selecting a stream
				self.store[progIter][4] = False
				progIter = self.store.iter_next(progIter)

		#if length of the path is 3 (that is, if we are selecting a program)
		elif len(path) == 3:
			# get the iter associated with the program path
			progIter = self.store.get_iter(path)

			#set stream check button state
			self.set_check_parent_button_state(progIter)

	# call to set parent check button state (if pid - set program state, if program - set stream state)
	def set_check_parent_button_state(self, citer):
		# set parent check button state dependent on children choosen
		# if all children are choosen - parent is choosen
		# if some children are choosen - parent is in inconsistent state
		# if no children are choosen - parent is also not choosen

		piter = self.store.iter_parent(citer)

		citer = self.store.iter_children(piter)
		# check if all the children are selected, or only some are selected
		all_selected = True
		some_selected = False
		while citer is not None:
			# if at least one program is not selected, set all_selected flag to false
			if self.store[citer][3] == False:
				all_selected = False
			# if at least one program is selected, set some_selected flag to true
			else:
				some_selected = True
			citer = self.store.iter_next(citer)

		# if all programs are selected, the stream as well is selected
		# if some programs are selected , the stream is partly selected (inconsistent)
		# if no programs selected, the stream as well is not selected
		self.store[piter][3] = all_selected
		if all_selected is False:
			self.store[piter][4] = some_selected
