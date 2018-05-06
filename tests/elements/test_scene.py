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


# config is tested in test_command_line.TestConfig
# no need to test it here again

def test_add_config(scene, region_polycurve_1, source_singleray_1,
	                                                            source_beam_1):
	# this scene contains one region and two sources
	config = scene.config
	scene.add(config)
	# the number of regions and sources should be doubled
	assert len(scene.regions) == 2
	assert len(scene.sources) == 4
