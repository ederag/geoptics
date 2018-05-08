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


"""Graphical counterpart to elements.

.. seealso::
	
	The purpose is described in the :ref:`guis.qt architecture` section.
"""


import logging
logger = logging.getLogger(__name__)   # noqa: E402
import weakref
from functools import wraps
from inspect import getmembers, getmodule


# from https://stackoverflow.com/a/682242/3565696
def g_counterpart(original_class):
	"""Enhance a graphical class to be a counterpart to an element.
	
	Add ``element`` to the __init__ keyword arguments.
	Add the ``.e`` property to access the element.
	
	Note:
		This function is intended to be used as a decorator.
		Decorators should be commutative.
		Hence element is a keyword - not positional - argument.
	"""
	
	# make copy of original __init__, so we can call it without recursion
	orig_init = original_class.__init__
	
	@wraps(orig_init)
	def __init__(self, *args, element=None, **kws):
		# Explicitly avoid cyclic dependency
		# between graphical item and python element.
		self._e_wr = weakref.ref(element)
		# self.e can now be used to get this element
		# (read only property, defined below)
		
		# call the original __init__
		orig_init(self, *args, **kws)
	
	@property
	def e(self):  # noqa: D401
		"""The corresponding element."""
		return self._e_wr()
	
	original_class.__init__ = __init__
	original_class.e = e
	return original_class


# ---------------------------------------------------------------------------
#                                  GOverload
# ---------------------------------------------------------------------------


def _g_overload(cls, names):
	"""Add overloading methods.
	
	Args:
		cls (class): the class to add methods to
		names (list of str):
			names of the methods of element that should be
			overloaded with wrappers to g_<name> methods
	
	Returns:
		The modified class
	
	"""
	
	# look for the corresponding _G class in the same module as cls
	module = getmodule(cls)
	# can not use getmembers(module, isclass)
	# because sphinx autodoc_mock_imports are not classes any longer
	module_classes = dict(getmembers(module))
	g_cls_name = "_G{}".format(cls.__name__)
	try:
		g_cls = module_classes[g_cls_name]
	except KeyError:
		raise KeyError("could not find the {} counterpart '{}' in "
		               "module {} "
		               "holding {}".format(cls, g_cls_name, module, module_classes))
	
	for name in names:
		# the g_<name> method of the _G<cls> class
		g_func = getattr(g_cls, "g_{}".format(name))
		
		# store g_func in a keyword default value,
		# otherwise the last g_func is used
		# wraps here is not compatible with sphinx autodoc_mock_imports
		#@wraps(g_func)
		def func(self, *args, g_func=g_func, **kwargs):
			return g_func(self.g, *args, **kwargs)
		
		# look for the method (in element) which we are overloading,
		# to provide a link to its documentation
		method = dict(getmembers(cls))[name]
		e_module = getmodule(method).__name__
		qualname = method.__qualname__
		
		func.__doc__ = """ Same as :py:class:`{e_module}.{qualname}`
		                   
		                   Overloaded to call ``{g_name}.g_{name}(self.g, ...)``
		               """.format(e_module=e_module, qualname=qualname,
		                          g_name=g_cls.__name__, name=name)
		
		setattr(cls, name, func)
		#logger.debug("overloaded {}.{} with {}".format(cls, name, func))
	
	return cls


class GOverload():
	"""Decorator factory.
	
	Used to make the interface class ``cls``
	(which inherits from `element`)
	call ``_G<cls>`` methods instead.
	
	Args:
		*names: names (`str`) of methods to be overloaded
	
	Returns:
		decorator, which effectively replaces each call to
		``<cls>.<name>(self, ...)`` with ``_G<cls>.g_<name>(self.g, ...)``
	
	Note:
		``_G<cls>`` must be in the same module as ``<cls>``
	
	Example:
		.. code-block:: python
			
			# in guis.qt.regions
			class _GPolycurve(...):
				...
				def g_translate(...):
					...
			
			
			@GOverload("start", "add_line", "add_arc", "close", "translate")
			class Polycurve(elements.regions.Polycurve):
				...
			
			
			# in ipython, create a region with qt gui interface
			r = guis.gt.sources.Polycurve(...)
			
			# the following will call
			# guis.gt.sources._GPolycurve.g_translate(r.g, ...)
			# instead of the normaly inherited
			# elements.regions.Polycurve.translate(self, ...)
			r.translate(...)
	
	"""
	
	def __init__(self, *names):
		self.names = names
	
	def __call__(self, cls):
		"""Overload the cls methods with wrappers to graphical methods."""
		return _g_overload(cls, self.names)
