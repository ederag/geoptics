"""Tkinter interface.

Unmaintained since 2015 (v0.3);
could be revived for display only (no interaction).
"""

from tkinter import *
from tkinter.ttk import *
import tkinter.ttk as ttk
from math import *
from geoptics.elements import vector


class Gui:
	def __init__(self, geo=None):
		self.root = Tk()
		self.setup(self.root)
		self.geo=geo
		self.geo.gui = self
		
	def setup(self, master):
		self.window = master
		
		self.window.title("GeOptics")
		
		self.menu = Menu(self.window)
		self.window.config(menu=self.menu)
		
		self.window.protocol("WM_DELETE_WINDOW", self.exit)
		
		#file menu
		self.filemenu = Menu(self.menu)
		self.menu.add_cascade(label="File", menu=self.filemenu)

		# self.filemenu.add_command(label="New", command=self.callback)
		self.filemenu.add_command(label="Open...", command=self.callback)
		self.filemenu.add_separator()
		self.filemenu.add_command(label="Exit", command=self.exit)
		# Help menu
		self.helpmenu = Menu(self.menu)
		self.menu.add_cascade(label="Help", menu=self.helpmenu)
		self.helpmenu.add_command(label="About...", command=self.callback)

		# self.display = Frame(self.window)
		self.canvas = Canvas(self.window, width = 300, height = 300,  background="cyan")
		self.canvas.pack(expand=1, fill=BOTH)
		# self.canvas.create_line(10, 20, 100, 200)
		
		# bindings
		self.canvas.bind('<ButtonPress-1>', self.down_1)
		self.canvas.bind('<Motion>', self.mouse_move)
		self.canvas.bind('<ButtonRelease-1>', self.up_1)
		
		# objects contained in this canvas hash table (keys are tags)
		self.objects = {}
		
		# tags related to an item
		self.tags = {}
		# which tags are moved currently
		self.current_moving_tag = None
		
		# memorize positions for moves
		self.move_last_x = 0
		self.move_last_y = 0
		
		# index of the last created region (never decreased, even upon deletion)
		self.region_idx = -1
		
		# whether the manipulation of canvas objects is controled by the gui (true) or by command line (false)
		self.is_master = True
	
	def start(self):
		self.root.mainloop()

	def callback(self):
		print("called the callback !")
		
	def down_1(self, event):
		# callback for mouse button 1 pressed
		self.move_last_x = event.x
		self.move_last_y = event.y
		# find the object that has been clicked on
		items = self.canvas.find_overlapping(event.x, event.y, event.x, event.y)
		# find the corresponding tag
		print(items, self.tags)
		if items:
			# keep only the first item
			item = items[0]
			if self.tags.has_key(item):
				self.current_moving_tag = self.tags[item]
			else:
				# we clicked on a non-movable object
				self.current_moving_tag = ''
		else:
			# we clicked in empty area => nothing to move
			self.current_moving_tag = ''
	
	def mouse_move(self, event):
		if self.current_moving_tag:
			# we are moving something
			dx = event.x - self.move_last_x
			dy = event.y - self.move_last_y
			# we could move all at once, but for now it is simpler to do it one by one
			#self.canvas.move(self.current_moving_tag, dx, dy)
			for obj in self.objects[self.current_moving_tag]:
				obj.move(dx, dy)
			self.geo.propagate(self.geo.rays)
			self.move_last_x = event.x
			self.move_last_y = event.y
	
	def up_1(self, event):
		# callback for mouse button 1 released
		if self.current_moving_tag:
			# stop moving
			self.current_moving_tag = ''
		else:
			# find the object that has been clicked on
			# margin (necessary, otherwise sometimes a ray is 'active' but not 'clicked' !)
			m = 1;
			items = self.canvas.find_overlapping(event.x-m, event.y-m, event.x+m, event.y+m)
			print(items)
			if items:
				# keep only the first item
				item = items[0]
				if self.tags.has_key(item):
					for obj in self.objects[ self.tags[item] ]:
						obj.selected(event)
	
	def object_register(self, obj, item, tag):
		# add object to the self.objects hash table, if already there, or create it
		if self.objects.has_key(tag):
			self.objects[tag] += [obj]
		else:
			self.objects[tag] = [obj]
		self.tags[item] = tag
		
	def objects_from_tag(self, tag):
		return self.objects[tag]
	
	
	## methods adding elements to gui. With them, gui module import is not necessary in elements.py
	
	def addFilledPolycurve(self, element, tag=None):
		return FilledPolycurve(element, self, tag=tag)
	
	def addRay(self, element, tag=None):
		return Ray(element, self, tag=tag)
	
	def exit(self):
		self.window.destroy()
		
# --------------------------------------------------------------------------
#                           geometric shape
# --------------------------------------------------------------------------

class Segment:
	def __init__(self, M1, M2, gui):
		self.xi = M1.x
		self.yi = M1.y
		self.xf = M2.x
		self.yf = M2.y
		self.gui = gui

	def draw(self):
		self.gui.canvas.create_line(self.xi, self.yi, self.xf, self.yf)

class Arc:
	def __init__(self, M1, M2, tangent, gui):
		self.M1 = M1.copy()
		self.M2 = M2.copy()
		self.tangent = tangent.copy()
		self.C = self.center()
		self.r = self.radius()
		self.theta1 = element.Vector_M1M2(self.C, self.M1).theta_x()
		self.theta2 = element.Vector_M1M2(self.C, self.M2).theta_x()
		self.gui = gui
	
	def center(self):
		""" return the center """
		Mm = element.Point(( (self.M1.x+self.M2.x)/2, 
		                     (self.M1.y+self.M2.y)/2      )) # middle of the chord
		# print "Mm"
		# Mm.show()
		Vch = element.Vector_M1M2(self.M1, self.M2).normal()# normal to the chord
		# print "Vch"
		# Vch.show()
		Vtg = self.tangent.normal()                    # normal to the tangent
		# print "Vtg"
		# Vtg.show()
		C = ( element.Line(Mm, Vch).intersection(element.Line(self.M1, Vtg)) )[0][0]
		return C
	
	def radius(self):
		return element.Vector_M1M2(self.M1, self.center()).norm()
	
	def draw(self):
		x0 = self.C.x - self.r
		y0 = self.C.y - self.r
		x1 = self.C.x + self.r
		y1 = self.C.y + self.r
		start = self.theta1 * 180. / pi
		extent = (self.theta2 - self.theta1) * 180. / pi
		CM1 = element.Vector_M1M2(self.C, self.M1)
		if (CM1.x * self.tangent.y - CM1.y * self.tangent.x) > 0:
			print("ccw")
			extent = 360+extent
		else:
			print("cw")

		self.gui.canvas.create_arc(x0, y0, x1, y1, style=ARC, 
		                           start=start, extent=extent)
		
		
#class Polycurve():
	#""" combine curves (eventually line segments) 
	    #Polycurve(M1)
			#M1: first point
	#"""		
	#def __init__(self, element, gui):
		#self.M = [element.M[0]]
		#self.curves = []
		#self.gui = gui
	
	#def add_line(self, M_next):
		#self.curves.append( Segment(self.M[-1], M_next, self.gui) )
		#self.M.append(M_next)
		#self.curves[-1].draw()
	
	#def add_arc(self, M_next, tangent):
		#self.curves.append( Arc(self.M[-1], M_next, tangent, self.gui) )
		#self.M.append(M_next)
		#self.curves[-1].draw()
	
	#def close(self):
		#self.curves.append( Segment(self.M[-1], self.M[0], self.gui) )
		#self.curves[-1].draw()
		
# -------------------------------------------------------------------------
#                             Ray
# -------------------------------------------------------------------------

class Ray:
	def __init__(self, element, gui, tag=None): # ray: element
		self.gui = gui
		self.e = element           # element
		self.coords = []
		self.item = None
		self.draw() # this one won't actually draw, just calculate the coords
		# now we can create the item
		self.item = self.gui.canvas.create_line(ttk._flatten(self.coords), fill="darkgreen", activefill="gray")
		self.set_tag(tag)
	
	def set_tag(self, tag):
		self.tag = tag
		self.gui.object_register(self, self.item, self.tag)
	
	def draw(self):
		self.coords = []
		for part in self.e.parts:
			self.coords += (part.line.p.x, 
			                part.line.p.y, 
			                part.line.p.x + part.line.u.x * part.s,
			                part.line.p.y + part.line.u.y * part.s)
		if self.item:
			# if the graphical representation of the ray has already been created
			self.gui.canvas.coords(self.item, ttk._flatten(self.coords))
	
	def add_part(self, e_part):
		self.draw()
	
	def change_s(self, part_number, new_s):
		self.draw()
	
	def selected(self, event):
		print("selected")
		
		
# ---------------------------------------------------------------------------
#                                  Region
# ---------------------------------------------------------------------------


class Region:
	def __init__(self):
		pass
		
class FilledPolycurve(Region):
	""" 
		Note: this should only never be called directly. 
		      call element.FilledPolycurve() instead, which in turn will create gui.FilledPolycurve()
		define a region inside curves (for instance line segments) 
	    Polycurve(M1)
			M1: first point
	"""		
	def __init__(self, element, gui, tag=None):
		self.e = element
		self.gui = gui
		self.gui.region_idx += 1
		# tag identifying this region
		if tag:
			self.tag = tag
		else:
			self.tag = "Region_%d" % self.gui.region_idx
		self.coords = [self.e.M[0].x, self.e.M[0].y, self.e.M[0].x, self.e.M[0].y]
		self.item = self.gui.canvas.create_polygon(self.coords, 
		                                        outline="black", fill="yellow", activefill="white", 
		                                        smooth=True, splinesteps=20, tags=self.tag)
		self.gui.object_register(self, self.item, self.tag)
		
	def add_line(self):
		M_next = self.e.M[-1]
		# duplicate coords to draw a straight line
		self.coords = self.coords + [M_next.x, M_next.y, M_next.x, M_next.y]
		self.gui.canvas.coords(self.item, ttk._flatten(self.coords))
	
	def add_arc(self, M_next, tangent):
		self.curves.append( Arc(self.M[-1], M_next, tangent, self.gui) )
		self.M.append(M_next)
		self.curves[-1].draw()
	
	def move(self, dx, dy):
		# move object on canvas
		self.gui.canvas.move(self.item, dx, dy)
		# translation vector
		v = vector.Vector(dx, dy)
		if self.gui.is_master:
			self.e.translate(v)
	
	#def draw():
