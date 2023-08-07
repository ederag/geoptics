# -*- coding: utf-8 -*-

# Copyright (C) 2017 ederag <edera@gmx.fr>
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


def test_translate(scene, region_polycurve_1):
	rp = region_polycurve_1
	
	rp.translate(dx=10, dy=20)
	
	# Segment
	assert rp.curves[0].M1.x == 80
	assert rp.curves[0].M1.y == 80
	assert rp.curves[0].M2.x == 80
	assert rp.curves[0].M2.y == 210
	
	# Segment
	assert rp.curves[1].M1.x == 80
	assert rp.curves[1].M1.y == 210
	assert rp.curves[1].M2.x == 120
	assert rp.curves[1].M2.y == 210
	
	# Arc
	assert rp.curves[2].M1.x == 120
	assert rp.curves[2].M1.y == 210
	assert rp.curves[2].M2.x == 120
	assert rp.curves[2].M2.y == 80
	assert rp.curves[2].C.x == -10
	assert rp.curves[2].C.y == 145
	
	# Segment
	assert rp.curves[3].M1.x == 120
	assert rp.curves[3].M1.y == 80
	assert rp.curves[3].M2.x == 80
	assert rp.curves[3].M2.y == 80
