# -*- coding: utf-8 -*-

# Copyright (C) 2016 ederag <edera@gmx.fr>
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

import pytest

from geoptics.elements.arc import Arc
from geoptics.elements.line import Line
from geoptics.elements.vector import Point, Vector


@pytest.fixture()
def arc():
	"""Return a generic Arc."""
	M1 = Point(10, 20)
	M2 = Point(50, 30)
	tangent = Vector(10, 20)
	return Arc(M1, M2, tangent)


def test_config(arc):
	arc_config = arc.config
	assert arc_config['Class'] == 'Arc'
	assert 'M1' in arc_config
	assert 'M2' in arc_config
	assert 'tangent' in arc_config


def test_orientations():
	# left to right, arc above segment
	arc = Arc(Point(10, 20), Point(50, 30), Vector(10, 20))
	assert arc.ccw is False
	line = Line(Point(30, 10), Vector(10, 30))
	intersections = arc.intersection(line, sign_of_s=1)
	assert len(intersections) == 1
	
	# right to left, arc above segment
	arc = Arc(Point(50, 30), Point(10, 20), Vector(-10, 20))
	assert arc.ccw is True
	line = Line(Point(30, 10), Vector(10, 30))
	intersections = arc.intersection(line, sign_of_s=1)
	assert len(intersections) == 1
	
	# left to right, arc below segment
	arc = Arc(Point(10, 20), Point(50, 30), Vector(10, -20))
	assert arc.ccw is True
	line = Line(Point(30, 10), Vector(10, -30))
	intersections = arc.intersection(line, sign_of_s=1)
	assert len(intersections) == 1
	
	# right to left, arc below segment
	arc = Arc(Point(50, 30), Point(10, 20), Vector(-10, -20))
	assert arc.ccw is False
	line = Line(Point(30, 20), Vector(10, -30))
	intersections = arc.intersection(line, sign_of_s=1)
	assert len(intersections) == 1
