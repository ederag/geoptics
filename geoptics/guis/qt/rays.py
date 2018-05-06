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


"""Rays for the :mod:`.guis.qt` backend."""

import logging
logger = logging.getLogger(__name__)   # noqa: E402
import weakref
from math import isinf

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainterPath, QPainterPathStroker, QPen
from PyQt5.QtWidgets import (
	QGraphicsItem,
	QGraphicsPathItem,
	QStyle,
	QStyleOptionGraphicsItem,
)

from geoptics import elements

from .counterpart import GCounterPart, GOverload


# -------------------------------------------------------------------------
#                             Ray
# -------------------------------------------------------------------------


class _GRay(GCounterPart, QGraphicsPathItem):
	"""The graphical class corresponding to :class:`.Ray`."""
	
	def __init__(self, element=None, **kwargs):
		GCounterPart.__init__(self, element)
		QGraphicsPathItem.__init__(self, **kwargs)
		
		self.setAcceptHoverEvents(True)
		self.setFlag(QGraphicsItem.ItemIsSelectable, True)
		# Rays stay just below the source,
		# without any need to set Z-value explicitly
		# This avoid selection problems (ray is always behind handles)
		self.setFlag(QGraphicsItem.ItemStacksBehindParent, True)
		
		# pen for normal state
		self.pen_normal = QPen(Qt.blue, 1.5, Qt.SolidLine)
		self.pen_normal.setCosmetic(True)  # thickness does not scale
		self.setPen(self.pen_normal)
		# pen for hover state
		self.pen_hover = QPen(Qt.gray, 1.5, Qt.SolidLine)
		self.pen_hover.setCosmetic(True)  # thickness does not scale
		
		# will be used in shape()
		self.stroker = QPainterPathStroker()
		
		self._selected = False
		
	def g_draw(self):
		self.prepareGeometryChange()
		# prevent BSPtree corruption (Qt crash)
		self.e.source.g.prepareGeometryChange()
		path = QPainterPath()
		# begin at the beginning
		p0 = self.e.parts[0].line.p
		path.moveTo(p0.x, p0.y)
		# add lines
		for part in self.e.parts:
			if isinf(part.s):
				# something large, but not inf, for Qt
				# make sure the ray extends more than the whole scene
				scene_rect = self.scene().sceneRect()
				s = 2 * max(scene_rect.width(), scene_rect.height())
			else:
				s = part.s
			path.lineTo(part.line.p.x + part.line.u.x * s,
			            part.line.p.y + part.line.u.y * s)
		
		# update to the new path
		self.setPath(path)
	
	def g_add_part(self, u, s, n=None):
		elements.rays.Ray.add_part(self.e, u, s, n)
		self.g_draw()
	
	def g_change_s(self, part_number, new_s):
		elements.rays.Ray.change_s(self.e, part_number, new_s)
		self.g_draw()
	
	def hoverEnterEvent(self, event):
		"""Overload QGraphicsPathItem method."""
		
		self.setPen(self.pen_hover)
		QGraphicsPathItem.hoverEnterEvent(self, event)
		
	def hoverLeaveEvent(self, event):
		"""Overload QGraphicsPathItem method."""
		
		self.setPen(self.pen_normal)
		QGraphicsPathItem.hoverEnterEvent(self, event)
		
	def itemChange(self, change, value):
		"""Overload QGraphicsPathItem method."""
		
		if (change == QGraphicsItem.ItemSelectedChange):
			# usually setSelected should not be called here, but
			# setSelected has been overriden and does not call the base method
			self.setSelected(value)
			# return False to avoid the deselection of the pointhandle
			# (multiple selection seems impossible without holding ctrl)
			return False
		# forward event
		return QGraphicsPathItem.itemChange(self, change, value)
	
	def paint(self, painter, option, widget=None):
		"""Overload QGraphicsPathItem method."""
		
		new_option = QStyleOptionGraphicsItem(option)
		# suppress the "selected" state
		# this avoids the dashed rectangle surrounding the ray when selected
		new_option.state = QStyle.State_None
		QGraphicsPathItem.paint(self, painter, new_option, widget)
	
	def shape(self):
		"""Overload QGraphicsPathItem method."""
		
		# by default, the shape is the path,
		# but closed, even if the path is a line
		# then sometimes the ray seems hovered, even when mouse is not on it
		# to avoid that, we need to reimplement shape,
		# with a QPainterPathStroker which
		# creates a shape that closely fits the line
		return self.stroker.createStroke(self.path())
	
	def setSelected(self, selected):
		"""Overload QGraphicsPathItem method."""
		
		# override base method, without calling it
		# otherwise the selection of pointHandle
		# deselected the ray and vice-versa
		# (multiple selection seems impossible without holding ctrl)
		# FIXME: should not use the element(.g) here. Find another way.
		self.e.source.g.setSelected(selected)
		self._selected = selected
		
	def isSelected(self):
		"""Overload QGraphicsPathItem method."""
		
		return self._selected


@GOverload("add_part", "change_s", "draw")
class Ray(elements.rays.Ray):
	"""Ray of light.
	
	This is the Ray that should be instanciated,
	in the :mod:`.guis.qt` backend.
	
	.. note::
		Regular users should not use Ray directly,
		but instead use one of the sources in :mod:`.qt.sources`.
	"""
	
	def __init__(self, line0=None, s0=100, source=None, n=None, tag=None,
		                                                 zvalue=100, **kwargs):
		g = _GRay(element=self, **kwargs)
		# rays must be children of the source, in order to
		# - be removed when source is removed from scene
		# - inherit the zvalue of the source
		# - be added to the scene when the source is added
		g.setParentItem(source.g)
		# the _G object has a Qt parent, so will be deleted by the C++ part
		# keep only a weak reference, otherwise there may be deletion races
		self._g_wr = weakref.ref(g)
		elements.rays.Ray.__init__(self, line0, s0, source, n, tag)
		self.source = source
		self.g.g_draw()
		self.set_tag(tag)
	
	def __del__(self):
		"""Cleanup upon deletion."""
		
		# if the deletion comes from the qt side, self.g is None
		if self.g:
			self.source.g.prepareGeometryChange()
			self.g.scene().removeItem(self.g)
	
	@property
	def g(self):
		"""Return the corresponding graphical item."""
		
		return self._g_wr()
