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

from geoptics.guis.qt import main as gui
#from geoptics.elements.regions import Polycurve
from geoptics.elements.line import Line
from geoptics.elements.vector import Vector, Point

from geoptics.guis.qt import regions
from geoptics.guis.qt import sources


if __name__ == "__main__":
	gui = gui.Gui()
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

	# refractive index for rp1
	n = 1.5

	# rp1
	rp1 = regions.Polycurve(n=n, scene=scene)
	m1 = Point(70, 60)
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

	#rp1.translate(Vector(0, 100))

	#rp2 = regions.Polycurve(n, scene=scene)
	#rp2.start(Point(121.0, 38.0))
	#rp2.add_line(Point(121.0, 168.0))
	#rp2.add_line(Point(161.0, 168.0))
	#rp2.add_line(Point(161.0, 38.0))
	#rp2.close()

	# tracé d'un rayon
	p0 = Point(10, 20)
	u0 = Vector(108, 50)
	s0 = 3
	n0 = 1.0
	source1 = sources.SingleRay(line0=Line(p0, u0), s0=s0, scene=scene)
	gui.print_(source1)

	p1 = Point(10, 50)
	u1 = Vector(108, 100)
	source2 = sources.Beam(line_start=Line(p0, u0),
	                       line_end=Line(p1, u1),
	                       s_start=100, s_end=100,
	                       N_inter=5,
	                       scene=scene)
	source2.translate(dy=40)

	scene.propagate()

	# launch the gui
	gui.start()
