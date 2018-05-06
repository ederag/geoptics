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


"""Sources of light rays.

This is the correct way for a user to generate and control rays.

Currently available sources are:

-	:class:`.SingleRay` for a single ray (surprise !)
-	:class:`.Beam` for a beam of light with evenly spaced rays.
	The :class:`.Beam` is very generic. Rays can be
	diverging, parallel, or focused.
	The source can be extended or point-like.

"""


from geoptics.elements.line import Line


class Source(object):
	"""Source of rays.
	
	Args:
		scene (:class:`~.elements.scene.Scene`)
	"""
	
	def __init__(self, scene=None, tag=None):
		self.scene = scene
		self.tag = tag
		self.ray_class = self.scene.class_map['Rays']['Ray']
		self.scene.add(self)
	
	@property
	def config(self):  # noqa: D401
		"""Configuration dictionary."""
		return {'Class': self.__class__.__name__,
		        'tag': self.tag,
		        'rays': [ray.config for ray in self.rays]
		        }
	
	@classmethod
	def from_config(cls, config, scene=None, tag=None):
		"""Alternate constructor.
		
		Args:
			config (dict): Configuration dictionary
		
		Returns:
			Source: new Source instance
		
		"""
		if tag is None:
			tag = config.get('tag')
		source = cls(scene=scene)
		source.rays = []
		for ray_config in config['rays']:
			ray_cls = source.ray_class
			ray = ray_cls.from_config(ray_config, source=source, tag=tag)
			source.rays.append(ray)
		return source
	
	def translate(self, **kwargs):
		"""Translate the source as a whole.
		
		Same syntax and same side effects as
		:py:meth:`geoptics.elements.vector.Point.translate`
		
		Likewise, it is possible to
		insert a ``.copy()`` to avoid side-effects.
		FIXME: copy() not implemented yet...
		
		return self for convenience
		"""
		for ray in self.rays:
			ray.translate(**kwargs)
		return self


class SingleRay(Source):
	"""Single ray source.
	
	Args:
		line0 (Line): starting
	"""
	
	def __init__(self, line0=None, s0=None,
		               scene=None, tag=None):
		Source.__init__(self, scene=scene, tag=tag)
		if line0 is not None:
			self.rays = [self.ray_class(line0=line0, s0=s0, source=self)]
		else:
			self.rays = None
	
	def move_p0(self, dx, dy):
		"""Translate the starting point of the ray."""
		self.rays[0].move_p0(dx, dy)
		
	def change_line_0(self, line):
		"""Change the starting line of the ray."""
		self.rays[0].change_line_0(line)
		
	def __repr__(self):
		return '{cls}(tag={tag}, line0={line0}, s0={s0})'.format(
		         cls=self.__class__.__name__,
		         tag=self.tag,
		         line0=self.rays[0].parts[0].line,
		         s0=self.rays[0].parts[0].s
		       )
	
	
class Beam(Source):
	"""Beam of rays.
	
	The Beam is defined by two extreme rays (first and last).
	Intermediate rays positions and angles (:term:`lines`) are
	evenly interpolated between the first and last ray.
	
	Args:
		line_start (Line): starting line for the beam first ray
		line_end (Line): starting line for the beam last ray
		s_start (float): initial length of the beam first ray
		s_end (float): initial length of the beam last ray
		N_inter (int): number of intermediate rays (>= 0)
		scene (:class:`~.elements.scene.Scene`)
	Returns:
		Source with N_inter + 2 (first and last) rays.
	
	"""
	
	def __init__(self,
	             line_start=None, s_start=None,
	             line_end=None, s_end=None,
	             N_inter=0, scene=None, tag=None):
		Source.__init__(self, scene=scene, tag=tag)
		self.rays = [self.ray_class(source=self)
		             for _ in range(N_inter + 2)]
		self.N_inter = N_inter
		self.set(line_start=line_start, line_end=line_end,
		         s_start=s_start, s_end=s_end)
	
	@classmethod
	def from_config(cls, config, scene=None, tag=None):
		"""Alternate constructor.
		
		Args:
			config (dict): Configuration dictionary
		
		Returns:
			:class:`.Beam`: new Beam instance
		
		"""
		beam = super().from_config(config, scene=scene, tag=tag)
		# ensure consistency
		beam.set()
		return beam
	
	def set(self, line_start=None, line_end=None, s_start=None, s_end=None,
	        N_inter=None):
		"""Set beam parameters.
		
		The parameters are taken from the given arguments,
		or from existing rays if the corresponding argument is missing
		
		Args: same as :class:`.Beam`, except 'scene' (for now)
		
		"""
		if line_start is None:
			line_start = self.rays[0].parts[0].line
		if line_end is None:
			line_end = self.rays[-1].parts[0].line
		if s_start is None:
			s_start = self.rays[0].parts[0].s
		if s_end is None:
			s_end = self.rays[-1].parts[0].s
		if N_inter is None:
			self.N_inter = len(self.rays) - 2
		else:
			self.N_inter = N_inter
		
		N_total = self.N_inter + 2
		if N_total > len(self.rays):
			# need more rays
			N_add = N_total - len(self.rays)
			last_ray = self.rays.pop()
			new_rays = [self.ray_class(source=self) for _ in range(N_add)]
			self.rays.extend(new_rays)
			# keep the last ray at the end
			self.rays.append(last_ray)
		elif N_total < len(self.rays):
			N_remove = len(self.rays) - N_total
			# do not remove the last one
			del self.rays[(-1 - N_remove):-1]
		
		for i in range(N_total):
			x = i / (N_total - 1)
			# FIXME: line_start and line_end are the same for all x;
			#        a lot of calculations are made several times for nothing
			#        in Line.interpolate
			#        => it should be possible to pass a list instead
			#        or even better, a generator ?
			new_line_0 = Line.interpolate(line_start, line_end, x)
			self.rays[i].change_line_0(new_line_0)
			self.rays[i].change_s(0, (1 - x) * s_start + x * s_end)
