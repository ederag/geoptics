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


"""Main module.

This file is called by the command line

.. code::

	python -m geoptics

the geoptics dir must be in the search path
(for instance in current working dir)
note the '-m' switch
cf. http://stackoverflow.com/questions/3411293/using-modules-own-objects-in-main-py  # noqa: E501
"""

import argparse

from geoptics.guis.qt import main as qtgui


# separate main function
# for the console_scripts entry_point in setup.py
def main():
	"""Start gui."""
	parser = argparse.ArgumentParser()
	parser.add_argument("--version", help="geoptics version",
	                    action="store_true")
	args = parser.parse_args()
	if args.version:
	    print("version")
	    return
	
	gui = qtgui.Gui()

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

	# manual stuff could be written here (see t_geo.py)
	# But here we start with an empty scene,
	# so do nothing

	# launch the gui
	gui.start()


if __name__ == "__main__":
	main()
