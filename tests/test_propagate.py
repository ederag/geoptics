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


def test_propagate_nothing(scene):
	"""Test the totally empty scene case."""
	scene.propagate()


def test_propagate_one_ray(scene, source_singleray_1):
	"""Test the no intersection (no region at all) case."""
	scene.propagate()


def test_propagate(scene, region_polycurve_1, source_singleray_1):
	"""Test ray propagation."""
	scene.propagate()
	ray = source_singleray_1.rays[0]
	assert len(ray.parts) == 4
	# last part should be outside
	assert ray.parts[-1].n == scene.background.n
