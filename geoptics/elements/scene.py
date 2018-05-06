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


"""Define a Scene, and hold all the propagation calculations."""


import logging
logger = logging.getLogger(__name__)   # noqa: E402

from geoptics.elements import rays
from geoptics.elements import regions
from geoptics.elements import sources
from geoptics.elements.rays import Ray
from geoptics.elements.regions import Region
from geoptics.elements.sources import Source
from geoptics.shared.tools import find_classes


class Scene(object):
	"""Scene holding all items."""
	
	def __init__(self):
		# FIXME: duplicated code with guis.qt.scene
		# correspondance between names in dumped data and classes
		self.class_map = {'Rays': find_classes(rays),
		                  'Sources': find_classes(sources),
		                  'Regions': find_classes(regions)}
		#: background medium (air by default)
		self.background = regions.Region(n=1.0)
		#: list of all regions, excluding background
		self.regions = []
		#: list of all sources
		self.sources = []

	def add(self, other):
		"""Add an element to the scene.
		
		Args:
			other:  the element to add to the scene.
				The element can be a :class:`~.elements.sources.Source` or
				a :class:`~.elements.regions.Region`.
				
				A :class:`~.elements.rays.Ray` is also accepted,
				for internal use,
				but normal users should only add Sources or Regions.
		
		"""
		if isinstance(other, Ray):
			raise TypeError("Always use a source to create a ray.\n"
			                "For instance, SingleRay()")
		elif isinstance(other, Region):
			if other in self.regions:
				raise ValueError("Region already in scene")
			else:
				self.regions.append(other)
		elif isinstance(other, Source):
			if other in self.sources:
				raise ValueError("Source already in scene")
			else:
				self.sources.append(other)
		elif isinstance(other, dict):
			self._add_config(other)
		else:
			raise NotImplementedError("Trying to add {}".format(type(other)))
	
	def _add_config(self, config):
		"""Add regions and sources from a configuration dictionary."""
		for cls, item_config in self._add_iterator(config):
			# with the "scene=" keyword, this new instance
			# will automatically be added to scene
			cls.from_config(item_config, scene=self)
	
	def _add_iterator(self, config):
		"""Return an iterator over the available items in config."""
		if ('Regions' in config) or ('Sources' in config):
			for category in ('Regions', 'Sources'):
				for item_config in config[category]:
					name = item_config['Class']
					cls = self.class_map[category][name]
					yield cls, item_config
		elif 'Class' in config:
			item_config = config
			name = item_config['Class']
			cls = None
			for category in ('Regions', 'Sources'):
				if name in self.class_map[category]:
					cls = self.class_map[category][name]
			if cls is None:
				logger.error("{} class not found".format(name))
				raise KeyError()
			yield cls, item_config
		else:
			logger.error(("neither 'Regions', 'Sources', nor 'Class'"
			              "found").format(name))
			raise KeyError()
	
	def clear(self):
		"""Remove all regions and sources."""
		
		# do not set empty lists,
		# otherwise guis would not remove items from display
		# working on "reversed" iterators allow to "pop" items
		# starting from the end of the list, avoiding side effects
		# Note: there are unnecessary lookups in self.remove()
		#       should we have a "pop" method too ?
		for region in reversed(self.regions):
			self.remove(region)
		for source in reversed(self.sources):
			self.remove(source)
		logger.debug("scene cleared")
	
	@property
	def config(self):  # noqa: D401
		"""Configuration dictionary."""
		return {'Regions': [region.config for region in self.regions],
		        'Sources': [source.config for source in self.sources],
		        }
	
	@config.setter
	def config(self, config):
		self.clear()
		self._add_config(config)
		logger.debug("config set")
	
	@classmethod
	def from_config(cls, config):
		"""Alternate constructor.
		
		Args:
			config (dict): Configuration dictionary
		
		Returns:
			:class:`.Scene`: new Scene instance
		
		"""
		scene = cls()
		scene.config = config
		return scene
	
	def remove(self, other):
		"""Remove element from scene."""
		if isinstance(other, Ray):
			raise TypeError("scene: Rays should be removed only from their Source")
		elif isinstance(other, Region):
			self.regions.remove(other)
		elif isinstance(other, Source):
			self.sources.remove(other)
		else:
			raise NotImplementedError("Trying to remove {}".format(type(other)))
	
	def propagate(self, rays=None):
		"""Propagate rays from sources, across regions."""
		if rays is None:
			# by default propagate all rays
			rays = [ray for source in self.sources for ray in source.rays]
		for ray in rays:
			ray.propagate(self)
	
	def region_at(self, *args, **kwargs):
		"""Return the region where the given point belongs to.
		
		In case of overlapping `self.regions`, return the first one found.
		
		Args: same as meth:`geoptics.elements.regions.Region.contains`
		
		Returns:
			Region: the region `point` belongs to.
				(or `self.background` if inside no region)
		
		"""
		
		for region in self.regions:
			if region.contains(*args, **kwargs):
				return region
		
		# no match
		return self.background
