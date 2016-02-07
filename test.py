#A grid of video renderers
class Renderer(Gtk.FlowBox):
	def __init__(self, progNum):
		Gtk.Grid.__init__(self)

		##should be horizontally expandable and fill all available space
		self.set_hexpand_set(True)
		self.set_hexpand(True)
		self.set_halign(Gtk.Align.FILL)
		self.set_valign(Gtk.Align.FILL)

		#set selection mode to None
		self.set_selection_mode(0)

		#set rows and cols homogeneous
		self.set_homogeneous(True)

		#set some space between renderers
		self.set_column_spacing(constants.DEF_SPACING)

		#add renderers
		self.draw_renderers(progNum)

	#draw necessary number of renderers
	def draw_renderers(self, progNum):
     		#set max children per line
		if progNum > 3:
			self.set_max_children_per_line(progNum/2)
		renderers = []
		for i in range(progNum):
			renderers.append(RendererOne(i))
			self.insert(renderers[i], -1)
