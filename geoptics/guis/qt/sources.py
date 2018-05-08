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


"""Sources of light rays for the :mod:`.guis.qt` backend."""


from PyQt5.QtGui import QPainterPath
from PyQt5.QtWidgets import QGraphicsItem

from geoptics import elements

from .counterpart import g_counterpart
from .handles import LineHandle


# note: making it a QGraphicsItemGroup would always move the whole thing
@g_counterpart
class _GSource(QGraphicsItem):
	"""The corresponding graphical class to sources.
	
	Args:
		element (Source): a source element belonging to
			:mod:`.guis.qt.sources`,
			such as :class:`.guis.qt.sources.Beam`.
	"""
	
	# note: @g_counterpart will add a keyword argument, "element"
	def __init__(self, zvalue=100, **kwargs):
		QGraphicsItem.__init__(self, **kwargs)
		
		# no need to implement paint()
		# but still need to implement boundingRect()
		self.setFlag(QGraphicsItem.ItemHasNoContents)
		
		self.rays = None
		
		self._selected = False
		
		self.setZValue(zvalue)
		
	def itemChange(self, change, value):
		"""Overload QGraphicsItem method."""
		
		if change == QGraphicsItem.ItemSceneChange:
			old_scene = self.scene()
			new_scene = value
			if old_scene:
				old_scene.signal_set_all_selected.disconnect(self.setSelected)
				old_scene.signal_reset_move.disconnect(self.reset_move)
			if new_scene:
				new_scene.signal_set_all_selected.connect(self.setSelected)
				new_scene.signal_reset_move.connect(self.reset_move)
		# forward event
		return QGraphicsItem.itemChange(self, change, value)
		
	def boundingRect(self):
		"""Overload QGraphicsItem method."""
		
		return self.childrenBoundingRect()
	
	def shape(self):
		"""Overload QGraphicsItem method."""
		
		# otherwise the shape is the children boundingRect !
		# and since itemAt uses shape,
		# the item was found, instead of the background
		path = QPainterPath()
		for ray in self.e.rays:
			path.addPath(ray.g.shape())
		return path


# -------------------------------------------------------------------------
#                             SingleRay
# -------------------------------------------------------------------------


class _GSingleRay(_GSource):
	"""The graphical class corresponding to :class:`.SingleRay`.
	
	Args:
		element (:class:`.SingleRay`): the corresponding element.
	"""
	
	def __init__(self, element=None, zvalue=100, **kwargs):
		_GSource.__init__(self, element=element, zvalue=100, **kwargs)
		self.line_handle = None
		
	def change_line_0(self, line):
		self.e.rays[0].change_line_0(line)
		
	def reset_move(self):
		if self.line_handle:
			self.line_handle.reset_move()
		
	def setSelected(self, selected):
		"""Overload QGraphicsItem."""
		
		# override base method, without calling it
		# otherwise the selection of pointHandle
		# deselected the ray and vice-versa
		# (multiple selection seems impossible without holding ctrl)
		if selected:
			if self.line_handle is None:
				l0 = self.e.rays[0].parts[0].line
				self.line_handle = LineHandle(l0, parent=self)
				self.line_handle.signal_moved.connect(self.change_line_0)
			self.line_handle.setVisible(True)
			self.line_handle.h_p0.setSelected(True)
		else:
			if self.line_handle:
				self.line_handle.setVisible(False)
				self.line_handle.h_p0.setSelected(False)
		self._selected = selected
		
	def isSelected(self):
		"""Overload QGraphicsItem."""
		
		return self._selected


class SingleRay(elements.sources.SingleRay):
	"""Single ray source.
	
	This is the SingleRay that should be instanciated by user,
	in the :mod:`.guis.qt` backend.
	"""
	
	def __init__(self, line0=None, s0=None,
		               scene=None, tag=None,
		               zvalue=100, **kwargs):
		# do not pass the scene here
		self.g = _GSingleRay(element=self, zvalue=zvalue, **kwargs)
		# The element __init__ method will call self.scene.add,
		# which will need self.g
		elements.sources.SingleRay.__init__(self, line0=line0, s0=s0,
		                                    scene=scene, tag=tag)


# -------------------------------------------------------------------------
#                             Beam
# -------------------------------------------------------------------------


class _GBeam(_GSource):
	"""The graphical class corresponding to :class:`.Beam`.
	
	Args:
		element (class:`.Beam`): the corresponding element.
	"""
	
	def __init__(self, element=None, zvalue=100, **kwargs):
		_GSource.__init__(self, element=element, zvalue=zvalue, **kwargs)
		self.line_handles = {'start': None, 'end': None}
	
	def change_line_start(self, line):
		self.e.set(line_start=line)
		
	def change_line_end(self, line):
		self.e.set(line_end=line)
		
	def reset_move(self):
		for name, handle in self.line_handles.items():
			if handle:
				handle.reset_move()
		
	def setSelected(self, selected):
		"""Overload QGraphicsItem."""
		
		# override base method, without calling it
		# otherwise the selection of pointHandle
		# deselected the ray and vice-versa
		# (multiple selection seems impossible without holding ctrl)
		if selected:
			for name, handle in self.line_handles.items():
				if handle:
					handle.setVisible(True)
				else:
					if name == 'start':
						idx = 0
						change_line = self.change_line_start
					elif name == 'end':
						idx = -1
						change_line = self.change_line_end
					line0 = self.e.rays[idx].parts[0].line
					new_handle = LineHandle(line0, parent=self)
					new_handle.signal_moved.connect(change_line)
					self.line_handles[name] = new_handle
				self.line_handles[name].h_p0.setSelected(True)
		else:
			for name, handle in self.line_handles.items():
				if handle:
					handle.setVisible(False)
					handle.h_p0.setSelected(False)
		self._selected = selected
		
	def isSelected(self):
		"""Overload QGraphicsItem."""
		
		return self._selected


class Beam(elements.sources.Beam):
	"""Beam source.
	
	This is the Beam that should be instanciated by user,
	in the :mod:`.guis.qt` backend.
	"""
	
	def __init__(self,
	             line_start=None, s_start=None,
	             line_end=None, s_end=None,
	             N_inter=0, scene=None, tag=None,
	             zvalue=100, **kwargs):
		# do not pass the scene here
		self.g = _GBeam(element=self, zvalue=zvalue, **kwargs)
		# The element __init__ method will call self.scene.add,
		# which will need self.g
		elements.sources.Beam.__init__(self,
		                               line_start=line_start, s_start=s_start,
		                               line_end=line_end, s_end=s_end,
		                               N_inter=N_inter,
		                               scene=scene, tag=tag)
