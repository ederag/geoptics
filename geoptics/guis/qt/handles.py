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


"""Handles to control elements in the :mod:`.guis.qt` backend.

Currently handles are always naturally related to another Qt item.
This item should be the handle parent.
Allowing handles without any parent (``parent=None``) is *not* implemented yet.

.. note::
	
	:class:`PointHandle` derive from a Qt class,
	and are living in the Qt realm only.
	
	They are not aware of the underlying elements.
	Hence the Qt :meth:`self.scene()` should be used,
	instead of `self.scene` -- mind the ``()``.
	
	This simplifies the calls, when :class:`PointHandle` are created with given
	``parent=``. The Qt scene() is inherited from parent,
	hence no need to add the ``scene=`` keyword.
	
	This is not the case for :class:`LineHandle` that are python objects
"""

import weakref

from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtGui import QPen, QVector2D
from PyQt5.QtWidgets import (
	QGraphicsEllipseItem,
	QGraphicsItem,
	QGraphicsLineItem,
)

from .signal import Signal


# -------------------------------------------------------------------------
#                             Handles
# -------------------------------------------------------------------------


class PointHandle(QGraphicsEllipseItem):
	"""Handle to control a "point".
	
	Args:
		relative (bool):
			- False (default): positions are absolute and in **scene coordinates**
			- True: positions are relative to the parent, and in **view coordinates**
			
	
	Note:
		Beware that a call to :meth:`setPos()` will emit `signal_moved`.
		Hence, call :meth:`setPos()` first,
		and only then connect to `signal_moved`.
	"""
	
	def __init__(self, tag=None, zvalue=1000, relative=False, **kwargs):
		QGraphicsEllipseItem.__init__(self, **kwargs)
		
		#: Signal to be emitted when the PointHandle is moved.
		#:
		#: **slot args:** (`dx`, `dy`),
		#: where `dx` and `dy` are displacements along *x* and *y*,
		#: in scene coordinates.
		self.signal_moved = Signal()
		
		#: Signal emitted when an `ItemSelectedChange` occurs.
		#:
		#: **slot args:** (:obj:`boolean`)
		self.signal_selected_change = Signal()
		
		self.relative = relative
		self.setFlag(QGraphicsItem.ItemIsMovable, True)
		self.setFlag(QGraphicsItem.ItemIsSelectable, True)
		# needed to handle move event
		self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
		if not relative:
			self.setFlag(QGraphicsItem.ItemSendsScenePositionChanges, True)
		# keep same size when zooming
		# then we need to map position from scene to device in itemChange
		self.setFlag(QGraphicsItem.ItemIgnoresTransformations, True)
		# zvalue should be higher than rays,
		# otherwise the ray takes focus before its handle
		self.setZValue(zvalue)
		# radius (in pixels)
		r = 4
		# circle is centered on (0, 0) in item coordinates
		self.setRect(-r, -r, 2 * r, 2 * r)
		self.position_before_move = None
		#: ignore :term:`move restrictions` ?
		#: Initially True so that the first move, to the initial position, is free
		#: The user is responsible for setting it back to False,
		#: to honor the scene setting
		self.ignore_move_restrictions = True
		
	def reset_move(self):
		"""Store the initial position, for :term:`move restrictions`."""
		self.position_before_move = self.pos()
		
	def setPos(self, *args):
		"""Overload QGraphicsEllipseItem."""
		
		parent_item = self.parentItem()
		if (
		    (parent_item is None) or not
		    (QGraphicsItem.ItemIgnoresTransformations and parent_item.flags())
		   ):
		     
			# no parent, or parent has not the ItemIgnoresTransformations flag
			# so args are in scene coordinates
			# but since the flag ItemIgnoresTransformations is set,
			# setPos should receive device (i.e. view) coordinates
			view_pos = self.mapFromScene(*args)
			QGraphicsEllipseItem.setPos(self, view_pos)
		else:
			# parent has the ItemIgnoresTransformations flag
			# hence, by convention adopted here,
			# args are already in view coordinates
			# (relative to the parent of course)
			QGraphicsEllipseItem.setPos(self, *args)
		
	def itemChange(self, change, value):
		"""Overload QGraphicsEllipseItem."""
		
		# noqa see file:///usr/share/doc/packages/python-qt4-devel/doc/html/qgraphicsitem.html#itemChange
		# they add && scene() to the condition. To check
		# the example shows also how to keep the item in the scene area
		if (change == QGraphicsItem.ItemPositionChange):
			new_pos = value
			old_pos = self.pos()
			if self.position_before_move is None:
				# beginning move => keep the original position
				self.position_before_move = old_pos
			# total displacement since the beginning of the move
			total_dx = new_pos.x() - self.position_before_move.x()
			total_dy = new_pos.y() - self.position_before_move.y()
			if (
				(not self.ignore_move_restrictions)
				and self.scene().move_restrictions_on
			   ):
				if abs(total_dx) >= abs(total_dy):
					# move along x only
					new_pos.setY(self.position_before_move.y())
				else:
					# move along y only
					new_pos.setX(self.position_before_move.x())
			# displacement for this elementary move
			current_dx = new_pos.x() - old_pos.x()
			current_dy = new_pos.y() - old_pos.y()
			#print "dx = ", current_dx, "dy = ", current_dy
			# move
			if self.relative:
				self.signal_moved.emit(current_dx, current_dy)
			self.scene().move_id += 1
			value = old_pos + QPointF(current_dx, current_dy)
		elif change == QGraphicsItem.ItemScenePositionHasChanged:
			new_pos = value
			#print "abs: ", new_pos
			self.signal_moved.emit(new_pos.x(), new_pos.y())
		# don't do that here, ItemSceneChange is not raised for children...
		#elif change == QGraphicsItem.ItemSceneChange:
		#	print "scene change"
		#	old_scene = self.scene()
		#	new_scene = value
		#	if old_scene:
		#		old_scene.signal_reset_move.disconnect(self.reset_move)
		#	new_scene.signal_reset_move.connect(self.reset_move)
		elif change == QGraphicsItem.ItemSelectedChange:
			self.signal_selected_change.emit(value)
		# forward event
		return QGraphicsItem.itemChange(self, change, value)


# note: - making it a QGraphicsItemGroup would always move the whole thing
#       - It used to be a QGraphicsItem with ItemHasNoContents flag
#         but this required to reimplement shape and boundingrect,
#         and a weakref machinery on the caller side
class LineHandle(object):
	"""Handle to control a "line".
	
	That is, control a point and a vector from that point.
		
	Args:
		line (~geoptics.elements.line.Line)
		parent (QGraphicsItem):
			the parent for all items composing this handle
	"""
	
	def __init__(self, line, parent=None, zvalue=1000, **kwargs):
		
		#: signal emitted when either end of the LineHandle has been moved.
		#:
		#: **slot args:** (:py:class:`~geoptics.elements.line.Line`)
		self.signal_moved = Signal()
		
		# a copy of the line this handle is representing
		self.line = line.copy()
		
		if parent is None:
			raise NotImplementedError(
				"parent can not be None.\n"
				"Please use the Qt item (e.g. _GPolycurve)\n"
				"that is related to this handle,\n"
				"or file an issue with a sufficiently clear motivation.")
		
		# handle for the starting point of the line
		self._h_p0_wr = weakref.ref(PointHandle(parent=parent))
		self.h_p0.setPos(self.line.p.x, self.line.p.y)
		self.h_p0.ignore_move_restrictions = False
		# connect to signal_moved only here,
		# otherwise setPos() would emit signal_moved
		# which would call
		# update_line() which needs the yet undefined self.line_item
		self.h_p0.signal_moved.connect(self.p0_moved)
		
		# self.h_p0.scene() returns the Qt object (_GScene)
		view = self.h_p0.scene().active_view
		if view:
			u_view_x, u_view_y = view.map_vector_from_scene(self.line.u.x,
			                                                self.line.u.y)
		else:
			# no active view (probably inside a test) => no transformation
			u_view_x = self.line.u.x
			u_view_y = self.line.u.y
		# use QVector2D to have normalize
		self.u_view = QVector2D(u_view_x, u_view_y)
		# length of 50 pixels to start with
		self.u_view.normalize()
		self.u_view *= 50
		#m = self.scene.active_view.matrix()
		#print "m11", m.m11(), "m21", m.m21()
		#print "m12", m.m12(), "m22", m.m22()
		#print "dx", m.dx(), "dy", m.dy()
		
		# create the handle for the end of the vector, h_u
		# parent is the starting point handle h_p0,
		# so that when h_p0 is moved the end point follows
		# hence no relative move and signal_moved is not emitted by h_u
		# use weakref since the object has a Qt parent,
		# to avoid circular references
		self._h_u_wr = weakref.ref(PointHandle(relative=True, parent=self.h_p0))
		# relative to the parent
		self.h_u.setPos(self.u_view.toPointF())
		# connect to signal_moved only here,
		# otherwise setPos() would emit signal_moved
		# which would call update_line()
		# which needs the yet undefined self.line_item
		self.h_u.signal_moved.connect(self.u_moved)
		
		# use weakref since the object has a Qt parent,
		# to avoid circular references
		self._line_item_wr = weakref.ref(QGraphicsLineItem(parent=self.h_p0))
		self.line_item.setPen(QPen(Qt.black, 0, Qt.DotLine))
		
		self.update_line()
		
		self.setZValue(zvalue)
	
	@property
	def h_p0(self):
		"""Handle for the starting point of the line."""
		return self._h_p0_wr()
	
	@property
	def h_u(self):
		"""Handle for the end of the u vector."""
		return self._h_u_wr()
	
	@property
	def line_item(self):
		"""Line item, joining the point and the end of the u vector."""
		
		return self._line_item_wr()
	
	def update_line(self):
		"""Update the line item."""
		
		self.line_item.setLine(0, 0, self.u_view.x(), self.u_view.y())
		
	def p0_moved(self, x, y):
		"""React to change of the point position.
		
		Args:
			x (float):
			y (float): new position of the point.
		"""
		
		self.line.p.x = x
		self.line.p.y = y
		self.update_line()
		self.signal_moved.emit(self.line)
	
	def u_moved(self, dx, dy):
		"""React to change of the vector end position.
		
		Args:
			dx (float):
			dy (float): displacements of the vector end, in view coordinates.
		"""
		
		du_view = QPointF(dx, dy)
		self.u_view += QVector2D(du_view)
		self.update_line()
		
		view = self.h_p0.scene().active_view
		if view:
			u_scene_x, u_scene_y = view.map_vector_to_scene(self.u_view.x(),
			                                                self.u_view.y())
		else:
			# no active view (probably inside a test) => no transformation
			u_scene_x = self.u_view.x()
			u_scene_y = self.u_view.y()
		
		self.line.u.x = u_scene_x
		self.line.u.y = u_scene_y
		self.line.u.normalize()
		self.signal_moved.emit(self.line)
			
	def reset_move(self):
		"""Store the initial position, for :term:`move restrictions`."""
		self.h_p0.reset_move()
		self.h_u.reset_move()
	
	def setVisible(self, visible: bool):
		"""Set visibility."""
		
		# h_u and line_item are children of h_p0, no need to set them
		self.h_p0.setVisible(visible)
		
	def setZValue(self, zvalue):
		"""Set the :term:`z_value`.
		
		The zvalue can be that of the item to be controlled.
		The Qt items composing the LineHandle will be set to :term:`z_values`
		1 or 2 above, to ensure their visibility.
		"""
		
		self.line_item.setZValue(zvalue + 1)
		self.h_p0.setZValue(zvalue + 2)
		self.h_u.setZValue(zvalue + 2)
