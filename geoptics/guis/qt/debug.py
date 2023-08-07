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


"""Various utilities used to debug the :mod:`guis.qt` backend."""


import gc

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen
from PyQt5.QtWidgets import QGraphicsPathItem, QGraphicsRectItem

from geoptics.guis.qt.handles import PointHandle


# This one is from lejlot,
# http://stackoverflow.com/a/19066146/3565696
def get(id_: int):
	"""Return the object having a given id_."""
	for obj in gc.get_objects():
		if id(obj) == id_:
			return obj


# This one fails for some object, because the gc.get_referrers()
# does not always return a list of dicts...
# need to look at its source
def referrers(obj):
	"""Find referrers to an object."""
	
	# there is only one object => only one dict in the list
	d = gc.get_referrers(obj)[0]
	return [key for key, value in d if value is obj]


def show_shape(item):
	"""Highlight the shape of item."""
	
	sh = QGraphicsPathItem()
	path = item.shape()
	# The shape path was returned in the item's coordinates
	# FIXME: translate is not enough when itemIgnoresTranformation
	path.translate(item.scenePos())
	sh.setPath(path)
	pen = QPen(Qt.magenta, 1.5, Qt.DashLine)
	pen.setCosmetic(True)  # thickness does not scale
	sh.setPen(pen)
	item.scene().addItem(sh)
	return sh

#sh1 = show_shape(source1.g)


def show_bounding_rect(item, local=False):
	"""Highlight the boundingRect of item."""
	
	if local:
		rect = item.boundingRect()
	else:
		rect = item.sceneBoundingRect()
	br = QGraphicsRectItem(rect)
	pen = QPen(Qt.lightGray, 1.5, Qt.DashLine)
	pen.setCosmetic(True)  # thickness does not scale
	br.setPen(pen)
	item.scene().addItem(br)
	return br


def show_children(item):
	"""Show all children of an item."""
	
	def show_children_idx(item, indent="", idx=0):
		children_flat = []
		for item in item.childItems():
			print("{}: {}{}".format(idx, indent, item))
			idx += 1
			if item in children_flat:
				raise ValueError("duplicate child")
			else:
				children_flat.append(item)
			(new_children_flat, idx) = show_children_idx(item, indent + "    ",
			                                             idx)
			children_flat += new_children_flat
		return (children_flat, idx)
	(children_flat, _) = show_children_idx(item)
	return children_flat

#ch = show_children(source1.g)


def check_source_rays_consistency(source):
	"""Check that the source has no missing or orphan rays in the scene."""
	
	# all ray elements should have a their .g in scene
	g_scene_items = source.scene.g.items()
	for ray in source.rays:
		assert ray.g in g_scene_items
	# all source.g children should have a .e that belongs to the source element
	for item in source.g.childItems():
		if not isinstance(item, PointHandle):
			assert item.e is not None
			assert item.e in source.rays, ("{} corresponding element "
			                               "not found".format(item))
