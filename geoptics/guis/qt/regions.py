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


"""Regions for the :mod:`.guis.qt` backend."""


import logging
logger = logging.getLogger(__name__)   # noqa: E402
from math import pi

from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtGui import (
	QColor,
	QPainterPath,
	QPen,
)
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsPathItem

from geoptics import elements

from .counterpart import GOverload, g_counterpart


# ---------------------------------------------------------------------------
#                                  Region
# ---------------------------------------------------------------------------

@g_counterpart
class _GPolycurve(QGraphicsPathItem):
	"""Graphical class corresponding to :class:`.Polycurve`.
	
	.. note::
		
		_G* objects are living in the Qt realm only.
		
		They are not aware of the underlying elements.
		Hence the Qt :meth:`self.scene()` should be used,
		instead of :meth:`self.scene` -- mind the ``()``.
	
	.. note::
		when about to change the `pos()` of this item,
		e.g. before a :meth:`setPos()` of a :meth:`translate()`,
		first issue a :meth:`reset_move()`
	"""
	
	# note: @g_counterpart will add a keyword argument, "element"
	def __init__(self, **kwargs):
		QGraphicsPathItem.__init__(self, **kwargs)
		
		# pen
		pen = QPen(Qt.black, 1.5, Qt.SolidLine)
		pen.setCosmetic(True)  # thickness independent os scale
		self.setPen(pen)
		self.setBrush(QColor("lightYellow"))
		#self.setBrush(QColor("Magenta").darker(120))
		
		# move handling
		self.setFlag(QGraphicsItem.ItemIsMovable, True)
		self.setFlag(QGraphicsItem.ItemIsSelectable, True)
		# needed to handle move event
		self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
		self.setAcceptHoverEvents(True)
	
	def g_add_arc(self, M_next, tangent):
		elements.regions.Polycurve.add_arc(self.e, M_next, tangent)
		arc = self.e.curves[-1]
		C = arc.C
		w = h = 2 * arc.r
		span = arc.theta2 - arc.theta1
		# span is defined modulo 2pi.
		if span < 0 and arc.ccw:
			# in the scene coordinates, ccw mean positive span
			span = 2 * pi + span
		if span > 0 and not arc.ccw:
			span = span - 2 * pi
		
		# the graphicsview has an indirect coordinates system => angles are opposite
		# this should be changed when working in scene coordinates
		qt_theta1 = -arc.theta1 * 180.0 / pi
		qt_span = -span * 180.0 / pi
		
		path = self.path()
		# Qt paths are relative to the first point of the region
		M0 = self.e.M[0]
		path.arcTo(C.x - M0.x - arc.r, C.y - M0.y - arc.r,
		           w, h, qt_theta1, qt_span)
		self.setPath(path)
	
	def g_add_line(self, M_next):
		elements.regions.Polycurve.add_line(self.e, M_next)
		# we can not do self.setPath( self.path().lineTo(M_next.x, M_next.y) )
		path = self.path()
		# Qt paths are relative to the first point of the region
		M0 = self.e.M[0]
		path.lineTo(M_next.x - M0.x, M_next.y - M0.y)
		self.setPath(path)
	
	def g_close(self):
		elements.regions.Polycurve.close(self.e)
		path = self.path()
		path.closeSubpath()
		self.setPath(path)
	
	def g_start(self, M_start):
		elements.regions.Polycurve.start(self.e, M_start)
		path = QPainterPath()
		path.setFillRule(Qt.WindingFill)
		# set starting point
		# Qt paths are relative to the first point of the region
		path.moveTo(0, 0)
		self.setPath(path)
		# about to move the _G item
		self.reset_move()
		self.setPos(M_start.x, M_start.y)
	
	def g_translate(self, v=None, dx=0, dy=0):
		if v:
			dx = v.x
			dy = v.y
		# about to move the _G item
		self.reset_move()
		# moveBy is inherited from QGraphicsPathItem
		self.moveBy(dx, dy)
	
	def itemChange(self, change, value):
		"""Overload QGraphicsPathItem."""
		
		# noqa see file:///usr/share/doc/packages/python-qt4-devel/doc/html/qgraphicsitem.html#itemChange
		# they add && scene() to the condition. To check
		# the example shows also how to keep the item in the scene area
		if change == QGraphicsItem.ItemSelectedChange:
			# reset, since not in a move
			self.position_before_move = None
		elif change == QGraphicsItem.ItemPositionChange:
			#print "pos changed to: ", value
			new_pos = value
			old_pos = self.pos()
			if self.position_before_move is None:
				# beginning move => keep the original position
				self.position_before_move = old_pos
			# total displacement since the beginning of the move
			total_dx = new_pos.x() - self.position_before_move.x()
			total_dy = new_pos.y() - self.position_before_move.y()
			if self.scene().move_restrictions_on:
				if abs(total_dx) >= abs(total_dy):
					# move along x only
					new_pos.setY(self.position_before_move.y())
				else:
					# move along y only
					new_pos.setX(self.position_before_move.x())
			# displacement for this elementary move
			current_dx = new_pos.x() - old_pos.x()
			current_dy = new_pos.y() - old_pos.y()
			#print "dx = ", current_dx, "dy = ", current_dy, self
			# move
			# the Qt item will be translated by Qt, based on "value"
			# the listener will move the element
			elements.regions.Polycurve.translate(self.e, dx=current_dx,
			                                             dy=current_dy)
			
			self.scene().move_id += 1
			value = old_pos + QPointF(current_dx, current_dy)
		elif change == QGraphicsItem.ItemSceneChange:
			old_scene = self.scene()
			new_scene = value
			if old_scene:
				old_scene.signal_set_all_selected.disconnect(self.setSelected)
				old_scene.signal_reset_move.disconnect(self.reset_move)
			if new_scene:
				new_scene.signal_set_all_selected.connect(self.setSelected)
				new_scene.signal_reset_move.connect(self.reset_move)
		# forward event
		return QGraphicsPathItem.itemChange(self, change, value)
	
	def hoverEnterEvent(self, event):
		"""Overload QGraphicsPathItem."""
		
		self.setOpacity(0.8)
		
	def hoverLeaveEvent(self, event):
		"""Overload QGraphicsPathItem."""
		
		self.setOpacity(1.0)
		
	#def hoverMoveEvent(self, event):
		# noqa see http://pyqt.sourceforge.net/Docs/PyQt5/api/qgraphicsscenehoverevent.html
		#pos = event.pos()
		#lastPos = event.lastPos()
		#delta_pos = pos - lastPos
		#print delta_pos
		#self.move(delta_pos.x, delta_pos.y)
	
	def reset_move(self):
		"""Reset the move machinery.
		
		Should be called at the beginning of a new move.
		Store the initial position. This is important to be able to constraint
		moves along a particular direction (move restrictions on).
		"""
		
		self.position_before_move = self.pos()
	
	# workaround Qt bug fixed in feb2016:
	# inserting a python method because
	# disconnect does not work on non-slot Qt methods
	# https://www.riverbankcomputing.com/pipermail/pyqt/2016-February/037000.html
	def setSelected(self, selected):
		"""Overload QGraphicsItem."""
		QGraphicsPathItem.setSelected(self, selected)


@GOverload("start", "add_line", "add_arc", "close", "translate")
class Polycurve(elements.regions.Polycurve):
	"""Define a region inside curves (for instance line segments).
	
	Args:
		scene (~qt.scene.Scene): to belong to.
	"""
	
	def __init__(self, n=None, scene=None, tag=None, zvalue=0, **kwargs):
		# do not pass the scene here
		self.g = _GPolycurve(element=self, **kwargs)
		# The element __init__ method will call self.scene.add,
		# which will need self.g
		elements.regions.Polycurve.__init__(self, n=n, scene=scene, tag=tag)
		
		# higher zvalue means above
		# regions should be below rays
		# the default zvalue is OK
		self.g.setZValue(zvalue)
