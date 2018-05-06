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


from PyQt5.QtWidgets import QGraphicsRectItem

import pytest

from geoptics.elements.line import Line
from geoptics.elements.vector import Point, Vector
from geoptics.guis.qt.handles import LineHandle


@pytest.fixture
def parent_item(scene):
	item = QGraphicsRectItem()
	scene.g.addItem(item)
	return item


def test_create_line_handle(scene, parent_item):
	p = Point(10, 20)
	u = Vector(30, 60)
	line0 = Line(p, u)
	# The initial position should be free, even with move restrictions on
	scene.g.move_restrictions_on = True
	lh = LineHandle(line0, parent=parent_item)
	assert lh.h_p0.pos().x() == 10
	assert lh.h_p0.pos().y() == 20
