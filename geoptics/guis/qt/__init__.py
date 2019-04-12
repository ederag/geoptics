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


"""Qt backend.

Interface with IPython
^^^^^^^^^^^^^^^^^^^^^^

And at the `ipython3`  prompt, ``%gui qt5`` has to be issued,
otherwise the command line is stuck until the window is closed.

So, starting from a shell:

.. code-block:: bash

	ipython3

And from the ipython command line:

.. code-block:: python

	%load_ext autoreload
	%autoreload 2      # for debugging purposes, reload modules if changed
	%gui qt5            # mandatory, before %run, otherwise blocked
	%run t_geo         # runs the t_geo.py script


sip API
^^^^^^^
In python3, ``sip.setapi('QVariant', 2)`` is default, so that
any Qt method that returns a :class:`QVariant` will return a python type
instead.

This means that no ``new_pos = value.ToPoint()`` are needed anymore.
Just use ``new_pos = value`` directly.

Do not use ``QString``, this is deprecated.
we use ``sip.setapi('QString', 2)``

cf. http://stackoverflow.com/a/22184911/3565696

Beware that with ``sip.setapi('QVariant', 2)``,
there is a caveat when using :class:`QSettings`.
in a nutshell, we *must* use the ``type=`` keyword argument
for :py:meth:`value()`

cf. `Support for QSettings
<http://pyqt.sourceforge.net/Docs/PyQt5/pyqt_qsettings.html>`_
    

.. _guis.qt architecture:

Architecture
^^^^^^^^^^^^

.. figure:: figures/UML_Polycurve.svg
	
	elements/gui relationships

When working with a `guis.qt.scene.Scene`,
either on the command line or from the gui,
only the gui class `qt.regions.Polycurve` instance exist.
There is no pure `elements.regions.Polycurve` instance at all.

The gui class `qt.regions.Polycurve`
inherits from `elements.regions.Polycurve`.
Methods that could lead to round trips are overloaded,
and just call a method of `qt.regions._GPolycurve` with the same name,
prefixed with `g_`. At this point, everything looks like a direct
modification to the Qt part only.

All `qt.regions._GPolycurve` methods act on the Qt items,
eventually triggering a call to the corresponding
`elements.regions.Polycurve` method,
never to `qt.regions.Polycurve` methods.

Here is an example of such a call:
`elements.regions.Polycurve.translate(self.e, ...)`.
In this call, `self` is the `_GPolycurve`,
`self.e` is a property yielding
the corresponding `qt.regions.Polycurve` instance.



Advantages of such a layout are

-	Imperative style programming.
	Commands are excuted immediately, and only once.
-	There are no round trips (element => gui => element => ...)
-	It is possible to exploit fully the QGraphicsView framework
	for items selection and movement.
	It is is actually what settled this choice in the beginning.

	Changing to a model-observer pattern or model-view-controller
	would involve a rewrite of the items displacement.
	For instance the gui would take only the mouse movements,
	and transmit them to the controller.

Some disadvantages of the current layout are

-	need for Scene.class_map (explained later).
	But maybe this could fit well with plugins.
-	foreseen issues for multithreaded operations.
	But the display is currently quite fast,
	with room for optimisations;
	multithreads are perhaps not worth the trouble.
  
Whether advantages dominate is not clear at the moment, but here it is.
Forks are welcome.
"""

try:
	# new location for sip
	# https://www.riverbankcomputing.com/static/Docs/PyQt5/incompatibilities.html#pyqt-v5-11
	from PyQt5 import sip
except ImportError:
	import sip

sip.setapi('QVariant', 2)
# this one is not used yet
# but it will ensure that QString are not used (deprecated)
sip.setapi('QString', 2)
