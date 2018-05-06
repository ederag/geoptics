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

import gc
import logging
logger = logging.getLogger(__name__)   # noqa: E402

import yaml

from geoptics.elements.line import Line
from geoptics.elements.vector import Point, Vector
from geoptics.guis.qt import regions
from geoptics.guis.qt import scene as qt_scene
from geoptics.guis.qt import sources
from geoptics.guis.qt.view import GraphicsView


def creation(scene, creation_type):
	if creation_type == "direct creation":
		# une region
		m1 = Point(70, 60)
		# refractive index for rp1
		n = 1.5
		rp1 = regions.Polycurve(n=n, scene=scene)
		rp1.start(m1)
		m2 = Point(70, 190)
		rp1.add_line(m2)
		m3 = Point(110, 190)
		rp1.add_line(m3)
		m4 = Point(110, 60)
		tg4 = Vector(10, -20)
		#rp1.add_line(m4)
		rp1.add_arc(m4, tg4)
		rp1.close()
		del rp1
		
		p0 = Point(10, 20)
		u0 = Vector(108, 50)
		s0 = 3
		line0 = Line(p0, u0)
		source1 = sources.SingleRay(line0=line0, s0=s0, scene=scene)
		del line0
		del source1
		gc.collect()
		# !! comment ou this line => no crash !!
		scene.propagate()
	elif creation_type == "scene.load":
		filename = 'tests/shifted_polycurves+single_ray.geoptics'
		with open(filename, 'r') as f:
			config = yaml.safe_load(stream=f)
			logger.debug("config: {}".format(config))
			scene.clear()
			scene_config = config['Scene']
			scene.config = scene_config
			#gui.scene.load(config['Scene'])
			scene.propagate()
	elif creation_type == "load individually":
		filename = 'tests/shifted_polycurves+single_ray.geoptics'
		with open(filename, 'r') as f:
			config = yaml.safe_load(stream=f)
		config_rp1 = config['Scene']['Regions'][0]
		logger.debug("config: {}".format(config_rp1))
		rp1 = regions.Polycurve.from_config(config=config_rp1, scene=scene)
		del rp1
		#gc.collect()
		#qapp.processEvents()
		config_source1 = config['Scene']['Sources'][0]
		logger.debug("{}".format(config_source1['rays'][0]))
		source1 = sources.SingleRay.from_config(  # noqa: F841
		                                        config=config_source1,
		                                        scene=scene)
		logger.debug("{}".format(scene.sources))
		del source1
		gc.collect()
		#qapp.processEvents()
		# !! comment out this line => no crash !!
		scene.propagate()


def deletion(scene, qapp):
	scene.regions[0].g.setSelected(True)
	qapp.processEvents()
	scene.g.signal_remove_selected_items.emit()
	
	scene.sources[0].g.setSelected(True)
	qapp.processEvents()
	scene.g.signal_remove_selected_items.emit()
	# commenting out next line seems to give an instant crash
	#qapp.processEvents()
	logger.debug("before collect")
	# comment out next line => no crash (well, not instantly...)
	gc.collect()
	logger.debug("after collect")
	qapp.processEvents()
	logger.debug("last processEvent")


def test_create_delete(qapp, creation_type):
	"""Test multiple creation and deletions of items."""
	scene = qt_scene.Scene()
	view = GraphicsView()
	view.setScene(scene.g)
	
	# need 3 iterations (2 do not crash)
	for cpt in range(3):
		
		creation(scene, creation_type)
		
		deletion(scene, qapp)
		
		# try to provoque the crash (but not crashing yet)
		# only the create_delete.py, with gui, crashes when
		# the self.e.source.g.prepareGeometryChange()
		# is missing
		view.itemAt(80, 70)
		qapp.processEvents()


if __name__ == "__main__":
	from geoptics.guis.qt import main as gui_main
	gui = gui_main.Gui()
	# don't know why yet, but setting scenerect fixes the combined move bug
	# (sometimes a region and a point handle were not moved by the same amount)
	# https://bugreports.qt.io/browse/QTBUG-45153
	# Side note: why is it working even when scenerect is too small ?
	#gui.scene.g.setSceneRect(0, 0, 20, 20)
	# the bug above seems to not show up on opensuse 13.2
	# So we set a scenerect large enough
	# because for the AnchorUnderMouse to work, there must be movable scrollbars
	# FIXME: the sceneRect update should be automatic
	size = 1e4
	gui.scene.g.setSceneRect(-size / 100, -size / 100, size, size)

	scene = gui.scene

	# need 3 iterations (2 do not crash)
	for cpt in range(3):
		creation(scene, "direct creation")
		deletion(scene, gui_main.app)

	# launch the gui
	gui.start()

	# crashes instantly
