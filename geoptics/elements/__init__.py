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


"""Package containing :term:`elements`.

The physical scene is two-dimensional.

First, it has an infinite background region (air by default),
and possibly contains several regions of different materials.
Regions are defined in the  :mod:`~geoptics.elements.regions` submodule.

Second, sources emit rays of light.
Rays must have a source,
from the :mod:`~geoptics.elements.sources` submodule.

Rays propagation takes place
in the :mod:`~geoptics.elements.rays` submodule.


The elements can be used alone, and form a consistent framework.
But if a graphical representation is desired, the current preferred procedure
is to start from the :mod:`~geoptics.guis.qt` package.


Elements glossary
~~~~~~~~~~~~~~~~~

.. glossary::
	
	element
	elements
		Object living in a :term:`scene`.
		It can be a physical element like a source or a region,
		or geometrical objects such as segments or arcs.
	
	index
	optical index
	refractive index
		Number characteristic of the propagation of light in a material.
		Currently only transparent materials are handled, so the index is real.
		For instance, silica glass has an index close to 1.5
		in the visible range.
	
	line
	lines
		Shorthand for half-line, defined by a starting Point and
		a Vector direction.
	
	scene
		Physical area where elements live.
	
	z_value
	z_values
		The z_value determines the "altitude" of an element.
		Elements with a higher :term:`z_value` are drawn on top.
		Elements with lower :term:`z_value` can be hidden
		by elements with a higher :term:`z_value`.

Submodules imports
~~~~~~~~~~~~~~~~~~

The python standard syntax to import submodules is

>>> from geoptics.elements.scene import Scene
>>> from geoptics.elements.sources import Beam
>>> scene = Scene()
>>> beam = Beam(scene=scene)


To make guis modules more readable, another route is provided by |geoptics|:

>>> from geoptics import elements
>>> scene = elements.scene.Scene()
>>> beam = elements.sources.Beam(scene=scene)

This is mostly useful in guis modules to easily distinguish
the elements ``Beam`` from the local gui ``Beam``
(since the element name starts with ``elements.``).
In user scripts, this is not useful, and the previous way is preferred.
"""


import os
from importlib import import_module


# import all modules in this subpackage directory
# This allows the other route explained in "Submodules imports" above.
for filename in os.listdir(os.path.dirname(__file__)):
	if filename[-3:] == ".py" and filename != "__init__.py":
		module_name = filename[:-3]
		import_module(".{}".format(module_name), "geoptics.elements")
