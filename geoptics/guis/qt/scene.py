# -*- coding: utf-8 -*-

# Copyright (C) 2014 ederag <edera@gmx.fr>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GeOptics; see the file LICENSE.txt.  If not, see
# <http://www.gnu.org/licenses/>.

"""Scene to be used with the Qt gui."""

import logging
logger = logging.getLogger(__name__)   # noqa: E402
import weakref

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QGraphicsScene, QUndoStack

from geoptics import elements
from geoptics.shared.tools import find_classes

from . import rays
from . import regions
from . import sources
from .counterpart import g_counterpart
from .handles import PointHandle


@g_counterpart
class _GScene(QGraphicsScene):
	"""The graphical class corresponding to :class:`.Scene`.
	
	Args:
		element (:class:`.Scene`): The corresponding element
		
	.. seealso::
		More informations on the relationships between Scene and _GScene
		can be found in the :ref:`guis.qt architecture` section.
	"""
	
	signal_set_all_selected = pyqtSignal(bool)
	signal_reset_move = pyqtSignal()
	signal_mouse_position_changed = pyqtSignal(float, float)
	signal_element_moved = pyqtSignal()
	signal_remove_selected_items = pyqtSignal()
	#: Signal emitted when selected items should be removed
	#: **slot args:** ()
	
	# note: @g_counterpart will add a keyword argument, "element"
	def __init__(self, **kwargs):
		QGraphicsScene.__init__(self, **kwargs)
		
		# view linked to this scene, currently under mouse
		self.active_view = None
		# incremented for each move
		self.move_id = 0
		self._last_checked_move_id = 0
		self.signal_remove_selected_items.connect(self.remove_selected_items)
		
		self.move_restrictions_on = False
		"""Whether objects moves should be restricted.
		
		.. glossary::
			move restrictions
				Some displacements can be restricted to certain directions.
				If ``move_restrictions_on`` is True, then the displacements are
				constrained to be along the `x` or `y` direction.
				The actual direction (`x` or `y`) should be the closest
				to the mouse displacement.
				For instance, if the mouse movement is mainly horizontal,
				then a :class:`~.qt.handles.PointHandle` would move along `x` only.
				
				This requires to store the initial position, at the beginning
				of the displacement. This is done by :meth:`reset_move` slots.
		"""
		
		# http://www.informit.com/articles/article.aspx?p=1187104&seqNum=3
		# recommends to set the parent
		# "so that PyQt is able to clean it up at the right time
		#  when the dialog box is destroyed"
		# but then there is a cycle => possible crashes on exit ?
		self.undo_stack = QUndoStack(parent=self)
		
	@property
	def active_view(self):
		"""Get current active view."""
		if self._active_view_wr:
			return self._active_view_wr()
	
	@active_view.setter
	def active_view(self, view):
		logger.debug("setting active_view to {}".format(view))
		if view:
			self._active_view_wr = weakref.ref(view)
		else:
			self._active_view_wr = None
		
	def addItem(self, item):
		"""Overload QGraphicsScene method."""
		
		# If the "scene=" keyword were passed on to constructors,
		# Then the _G object ItemSceneChange would _not_ be called (Qt 4.8.6).
		if item in self.items():
			raise ValueError("{} is already in {}\n"
			                 "never use the 'scene=' keyword for _G objects,\n"
			                 "only the _GScene.additem() method"
			                 .format(item.e, self)
			                 )
		else:
			QGraphicsScene.addItem(self, item)
	
	def mousePressEvent(self, event):
		"""Overload QGraphicsScene method."""
		
		if event.button() == Qt.RightButton:
			# block the right mouse press event so that selection is not cleared
			# before the context menu is shown (not yet implemented)
			event.accept()
		else:
			QGraphicsScene.mousePressEvent(self, event)  # forward event
	
	def mouseReleaseEvent(self, event):
		"""Overload QGraphicsScene method."""
		
		self.element_moved = False
		QGraphicsScene.mouseReleaseEvent(self, event)  # forward event
	
	def mouseMoveEvent(self, event):
		"""Overload QGraphicsScene method."""
		
		pos = event.scenePos()
		self.signal_mouse_position_changed.emit(pos.x(), pos.y())
		QGraphicsScene.mouseMoveEvent(self, event)
		if self.move_id != self._last_checked_move_id:
			#logger.debug("move_id = {}".format(self.move_id))
			self._last_checked_move_id = self.move_id
			self.signal_element_moved.emit()
	
	def keyPressEvent(self, event):
		"""Handle key pressed events.
		
		- ``Delete``: remove selected items
		- ``ESC``: deselect all
		"""
		
		key = event.key()
		if key == Qt.Key_Delete:  # SUPPR
			self.signal_remove_selected_items.emit()
		elif (key == Qt.Key_Escape):  # ESC
			self.signal_set_all_selected.emit(False)
	
	# the following does not work. Actually sceneRect is never called
	#def sceneRect(self):
		# # use a boundingRect twice as large as the default tight boundingRect
		# # so that anypoint of the tight boundingRect
		# # can be used as the view center by moving the scrollbars
		#rect = self.itemsBoundingRect()
		#print rect
		#ax, ay, aaw, aah = rect.getRect()
		#rect.setRect(ax - aaw / 2.0, ay - aah / 2.0, aaw * 2, aah * 2)
		#return rect
	
	def remove(self, item):
		"""Remove item from both Qt and elements scene."""
		
		logger.info("removing {}".format(item.e))
		self.removeItem(item)
		# remove the element after its Qt counterpart,
		# otherwise garbage collection might destroy the Qt item => crash ?
		elements.scene.Scene.remove(self.e, item.e)
	
	def remove_selected_items(self):
		"""Remove selected items from scene."""
		
		for item in self.items():
			if (
			   item.isSelected() and
			   # Rays and PointHandles are removed by their parent
			   not isinstance(item, (PointHandle, rays._GRay))
			   ):
				# workaround children remaining visible (Qt 4.8.6)
				# item.prepareGeometryChange()  # does not work either
				item.setVisible(False)
				self.remove(item)
		self.e.propagate()
		# Nothing of these worked, sometimes children remained visible,
		# until another object is drawn over:
		#self.invalidate(self.sceneRect(), QGraphicsScene.AllLayers)
		#self.update()
		#self.changed.emit([self.sceneRect()])


class Scene(elements.scene.Scene):
	"""The Scene that should be instanciated by user, in the guis.qt backend."""
	
	def __init__(self, **kwargs):
		elements.scene.Scene.__init__(self)
		# The scene Qt part has no parent => owned by self (python part)
		self.g = _GScene(element=self, **kwargs)
		#: correspondance between names in config data, and classes
		self.class_map = {'Rays': find_classes(rays),
		                  'Sources': find_classes(sources),
		                  'Regions': find_classes(regions)}
		self.g.signal_element_moved.connect(self.propagate)
	
	def add(self, other, tag=None):
		"""Add an element to the scene.
		
		Args:
			other (dict or element): the element to be added, either as a
				config dictionnary, or directly as an object such as
				:class:`.guis.qt.sources.Beam` or
				:class:`.guis.qt.regions.Polycurve`
		"""
		elements.scene.Scene.add(self, other)
		if not isinstance(other, dict):
			# other is not a config. Thus it must be an element
			self.g.addItem(other.g)
	
	def remove(self, element):
		"""Remove the element from scene."""
		self.g.remove(element.g)
