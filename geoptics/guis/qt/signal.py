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


"""Signal for non-QObjects."""


import logging
logger = logging.getLogger(__name__)   # noqa: E402
import weakref


# -------------------------------------------------------------------------
#                             Signals
# -------------------------------------------------------------------------


class Signal:
	"""Only QObject can send signals.
	
	We need this trick for GraphicsItems
	taken from
	http://stackoverflow.com/questions/21101500/custom-pyqtsignal-implementation
	
	see also http://abstractfactory.io/blog/dynamic-signals-in-pyqt/
	
	a priori the only problem is that it can't be used across threads
	
	Note:
		Contrary to pyqtSignal,
		a new Signal instance must be created for each object instance,
		otherwise signals would be mixed up between instances.
		
		Hence the correct place is in the ``__init__`` function:
		
		.. code-block:: python
		
			def __init__(self):
				self.signal_name = Signal()
	"""
	
	def __init__(self):
		# Do not use a weakref.WeakValueDictionary
		# because with the latter
		# keys would be deleted upon garbage collection
		# preventing correct iteration over keys
		# Besides, raising an error for missing subscriber is
		# good to catch bugs early
		self.__subscribers = {}
		
	def emit(self, *args, **kwargs):
		"""Emit signal.
		
		This calls all connected slots with the emit arguments.
		"""
		
		for ref in self.__subscribers.keys():
			subs = ref()
			if subs is None:
				raise ReferenceError(
				     "{} is not available anymore.\n"
				     "Signals should be disconnected before deletion".format(
				                                       self.__subscribers[ref])
				)
			else:
				subs(*args, **kwargs)
		
	def connect(self, func):
		"""Connect a function (a "slot") to this signal."""
		
		# use a weak reference,
		# otherwise some objects were not deleted with their c++ counterpart
		# => crash
		ref = weakref.WeakMethod(func)
		self.__subscribers[ref] = func.__repr__()
		
	def disconnect(self, func):
		"""Remove a slot from this signal."""
		
		try:
			self.__subscribers.remove(func)
		except ValueError:
			logger.warning("function {} not removed from signal {}".format(
			                                                       func, self))
