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

"""View displaying the scene."""

import logging
logger = logging.getLogger(__name__)   # noqa: E402

from PyQt5.QtCore import (
	QRectF,
	Qt,
	pyqtSlot
)
from PyQt5.QtGui import (
	QBrush,
	QColor,
	QPainter,
	QTransform,
)
from PyQt5.QtWidgets import (
	QFrame,
	QGraphicsView,
	QLabel,
	QVBoxLayout,
)


# --------------- GraphicsView Frame (holds view, position indicator, ...)


class PositionIndicator(QLabel):
	"""Displays an x,y position."""
	
	def __init__(self, **kwargs):
		QLabel.__init__(self, **kwargs)
		self.setText("NA, NA")
	
	@pyqtSlot(float, float)
	def on_changed_position(self, x, y):
		"""Update the display to the given ``x``, ``y`` position."""
		self.setText("x = %g, y = %g" % (x, y))


class GraphicsViewFrame(QFrame):
	"""Frame containing the view and related widgets."""
	
	def __init__(self, view=None, **kwargs):
		QFrame.__init__(self, **kwargs)
		#: :class:`.PositionIndicator`
		self.position_indicator = PositionIndicator()
		layout = QVBoxLayout()
		layout.addWidget(self.position_indicator)
		self.setLayout(layout)
		self.view = view
	
	@property
	def view(self):
		""":class:`GraphicsView`."""
		return self._view
	
	@view.setter
	def view(self, view):
		self._view = view
		if view:
			self.layout().addWidget(view)


class GraphicsView(QGraphicsView):
	"""Scene holder."""
	
	def __init__(self, **kwargs):
		QGraphicsView.__init__(self, **kwargs)
		self.setRenderHints(QPainter.Antialiasing)
		self.setBackgroundBrush(QBrush(QColor(Qt.cyan).lighter(150)))
		#self.setBackgroundBrush( QBrush( QColor(Qt.darkGray).darker(200) ) )
		# invert y axis because scene coordinates system is direct,
		# with y up oriented
		self.setTransform(QTransform.fromScale(1.0, -1.0))
		# viewport control (part of the scene displayed)
		self.setViewportUpdateMode(QGraphicsView.BoundingRectViewportUpdate)
		self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
		self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
		# seems that the translate stuff is a bit buggy in Qt
		# https://bugreports.qt-project.org/browse/QTBUG-7328
		# this does not help
		#self.setAlignment(Qt.Alignment(0))
		
		# AnchorUnderMouse works by moving the wiewport around with scrollbars
		# so movable scrollbars are needed,
		# and the scenerect should be large enough
		self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
		self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
		
	def map_vector_from_scene(self, u_scene_x, u_scene_y):
		"""Map a vector given in scene coords to view coords."""
		
		# we can not use transform.inverted() because the translations
		# dx, dy are not relevant for vectors
		t = self.transform()
		# we should not have any shear or rotation
		assert(not t.isRotating() and t.m13() == 0 and t.m23() == 0)
		# scaling factors
		sx = t.m11()
		sy = t.m22()
		return u_scene_x * sx, u_scene_y * sy
		
	def map_vector_to_scene(self, u_view_x, u_view_y):
		"""Map a vector given in view coords to scene coords."""
		
		# we can not use transform.inverted() because the translations
		# dx, dy are not relevant for vectors
		# besides, for such a simple translation/scale transform,
		# direct inversion should be faster
		t = self.transform()
		# we should not have any shear or rotation
		assert(not t.isRotating() and t.m13() == 0 and t.m23() == 0)
		# scaling factors
		sx = t.m11()
		sy = t.m22()
		return u_view_x / sx, u_view_y / sy
		
	def enterEvent(self, event):
		"""Overload QGraphicsView method."""
		self.scene().active_view = self
	
	def mousePressEvent(self, event):
		"""Overload QGraphicsView method."""
		if event.button() == Qt.LeftButton:
			self.scene().signal_reset_move.emit()
			#print "mousePressEvent, item: ", self.itemAt(event.pos()), event.pos()
			item_at = self.itemAt(event.pos())
			if not item_at:
				# clicked outside any item => deselect all
				# note: it is much better to handle it in GraphicsView
				#       than in Scene, because precision is better
				#       otherwise sometimes clicking could deselect,
				#       although the ray appeared "hovered"
				logger.debug("deselect all")
				self.scene().signal_set_all_selected.emit(False)
			else:
				logger.debug("clicked on {}".format(item_at))
			# forward event
			QGraphicsView.mousePressEvent(self, event)
		elif event.button() == Qt.MiddleButton:
			# pan mode
			self._previous_transformation_anchor = self.transformationAnchor()
			self.setTransformationAnchor(QGraphicsView.NoAnchor)
			# This prevents the scrollContentsBy function of re-sending
			# the mouseMove events (and avoid deselections)
			self._previous_interactive_state = self.isInteractive()
			self.setInteractive(False)
			# store position
			self._previous_position = event.pos()
		else:
			# forward event
			QGraphicsView.mousePressEvent(self, event)
	
	def mouseMoveEvent(self, event):
		"""Overload QGraphicsView method."""
		if event.buttons() == Qt.MiddleButton:
			# panning
			delta = event.pos() - self._previous_position
			self.translate(delta.x(), delta.y())
			self._previous_position = event.pos()
		# forwarding
		QGraphicsView.mouseMoveEvent(self, event)
		
	def mouseReleaseEvent(self, event):
		"""Overload QGraphicsView method."""
		if event.button() == Qt.MiddleButton:
			# end of panning
			self.setTransformationAnchor(self._previous_transformation_anchor)
			self.setInteractive(self._previous_interactive_state)
		# forwarding
		QGraphicsView.mouseReleaseEvent(self, event)
	
	def wheelEvent(self, event):
		"""Ctrl+mouse wheel zoom, otherwise pan."""
		if event.modifiers() == Qt.ControlModifier:
			self.scale_view(pow(2.0, event.angleDelta().y() / 240.0))
		else:
			return QGraphicsView.wheelEvent(self, event)
	
	# the following does not work. Actually updateSceneRect is never called,
	# even when setSceneRect() has never been set
	#def updateSceneRect(self, rect):
		#ax, ay, aaw, aah = rect.getRect()
		#new_rect = QRectF(ax - aaw / 2.0, ay - aah / 2.0, aaw * 2, aah * 2)
		#print new_rect
		#QGraphicsView.updateSceneRect(new_rect)
	
	def scale_view(self, scale_factor):
		"""Zoom in or out."""
		
		# taken from elasticnodes.py
		factor = self.transform().scale(scale_factor, scale_factor).mapRect(
		                                            QRectF(0, 0, 1, 1)).width()
		if factor > 0.001 and factor < 1000:
			self.scale(scale_factor, scale_factor)
