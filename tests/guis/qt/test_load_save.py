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

import logging
logger = logging.getLogger(__name__)   # noqa: E402

from geoptics.guis.qt.debug import check_source_rays_consistency


def test_load_fine(gui):
	filename = "tests/polycurve+beam+single_ray.geoptics"
	gui.load_file(filename)
	scene = gui.scene
	assert len(scene.regions) == 1
	assert len(scene.sources) == 2


def test_load_wrong(gui):
	"""Load a wrong file (missing "Scene")."""
	
	# load a working scene first
	test_load_fine(gui)
	config_orig = gui.scene.config
	
	# now load a wrong one (missing "e" in "Scen")
	filename = "tests/scene_faulty.geoptics"
	gui.load_file(filename)
	
	# a rollback should have occurred
	assert gui.scene.config == config_orig
	
	for source in gui.scene.sources:
		check_source_rays_consistency(source)


def test_import(gui):
	"""Import from file."""
	filename = "tests/polycurve+beam+single_ray.geoptics"
	scene = gui.scene
	gui.load_file(filename, reset_scene=False)
	assert len(scene.regions) == 1
	assert len(scene.sources) == 2
	gui.load_file(filename, reset_scene=False)
	assert len(scene.regions) == 2
	assert len(scene.sources) == 4
	
	# now import a single item
	# a region
	filename = "tests/region_polycurve_1.geoptics"
	gui.load_file(filename, reset_scene=False)
	assert len(scene.regions) == 3
	assert len(scene.sources) == 4
	# a source
	filename = "tests/source_beam_1.geoptics"
	gui.load_file(filename, reset_scene=False)
	assert len(scene.regions) == 3
	assert len(scene.sources) == 5
