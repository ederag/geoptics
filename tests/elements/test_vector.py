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

"""test the vector module."""

import pytest

from geoptics.elements.vector import Point, Vector


@pytest.fixture()
def point():
	"""Return a generic Point."""
	return Point(10, 20)


@pytest.fixture()
def vector():
	"""Return a generic Vector."""
	return Vector(30, 60)


class TestConfig:
	def test_point(self, point):
		point_config = point.config
		assert 'x' in point_config
		assert 'y' in point_config

	def test_vector(self, vector):
		vector_config = vector.config
		assert 'x' in vector_config
		assert 'y' in vector_config
