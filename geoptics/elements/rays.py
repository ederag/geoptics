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


"""Rays of light.

:class:`.Part` should not be used directly.
Actually, even :class:`.Ray` should not be used directly.
Users wanting a single ray should instanciate a
:class:`~.elements.sources.SingleRay` source.
"""

import math
from operator import itemgetter
from sys import float_info

from .line import Line


class Part(object):
	"""Straight part of a ray."""
	
	def __init__(self, line=None, s=None, n=None):
		if line is None:
			#: starting point and direction
			self.line = Line()
		else:
			self.line = line.copy()
		#: length
		self.s = s
		#: :term:`optical index`
		self.n = n
	
	@property
	def config(self):  # noqa: D401
		"""Configuration dictionary."""
		return {'line': self.line.config,
		        's': self.s,
		        'n': self.n,
		        }
	
	@classmethod
	def from_config(cls, config):
		"""Alternate constructor.
		
		Args:
			config (dict): Configuration dictionary
		
		Returns:
			Part: new Part instance
		
		Examples:
			>>> from geoptics.elements.vector import Point, Vector
			>>> from geoptics.elements.line import Line
			>>> from geoptics.elements.rays import Ray
			>>> p = Point(10, 20)
			>>> u = Vector(30, 60)
			>>> line1 = Line(p, u)
			>>> s = 100
			>>> n = 1.5
			>>> part1 = Part(line1, s, n)
			>>> config = part1.config
			>>> part2 = Part.from_config(config)
			>>> part2.config == config
			True
		
		"""
		line = Line.from_config(config['line'])
		s = config['s']
		n = config['n']
		return cls(line, s, n)
		
	def __repr__(self):
		return "Part({line}, s={s}, n={n})".format(**vars(self))
	
	def translate(self, **kwargs):
		"""Translate the part as a whole.
		
		Same syntax and same side effects as
		:meth:`geoptics.elements.vector.Point.translate`
		
		Likewise, it is possible to
		insert a ``.copy()`` to avoid side-effects.
		FIXME: :meth:`copy()` not implemented yet...
		
		return `self` for convenience
		"""
		self.line.translate(**kwargs)
		return self


class Ray(object):
	"""A ray of light.
	
	A ray must have a source. normally rays are not created directly.
	Use one of the sources module objects instead.
	
	Args:
		line0 (Line): first point and direction
		s0 (float): initial length
		n (float): refractive index of the starting medium
		source (:class:`~geoptics.elements.sources.Source`): source of the ray
	
	"""
	
	def __init__(self, line0=None, s0=100, source=None, n=None, tag=None):
		self.source = source
		if line0 is None:
			self.parts = (Part(s=s0, n=n),)
		else:
			self.parts = (Part(line0, s0, n),)
		self.set_tag(tag)
	
	@classmethod
	def from_config(cls, config, source=None, tag=None):
		"""Alternate constructor.
		
		Args:
			config (dict): Configuration dictionary
		
		Returns:
			Part: new Part instance
		
		Examples:
			>>> from geoptics.elements.vector import Point, Vector
			>>> from geoptics.elements.line import Line
			>>> from geoptics.elements.rays import Ray
			>>> p = Point(10, 20)
			>>> u = Vector(30, 60)
			>>> line1 = Line(p, u)
			>>> s = 100
			>>> n = 1.5
			>>> ray1 = Ray(line0=line1, s0=s, n=n)
			>>> config = ray1.config
			>>> ray2 = Ray.from_config(config)
			>>> ray2.config == config
			True
		
		"""
		if tag is None:
			tag = config.get('tag')
		ray = cls(source=source, tag=tag)
		ray.parts = []
		for part_config in config['parts']:
			part = Part.from_config(part_config)
			ray.parts.append(part)
		return ray
	
	def set_tag(self, tag):
		"""Set tag."""
		self.tag = tag
	
	def add_part(self, u, s, n=None):
		"""Add a new part to the ray.
		
		Args:
			u (Line): starting point and direction for that part
			s (float): length of that part
			n (float, optional): :term:`optical index` encountered by that part.
		"""
		p = self.parts[-1].line.point(self.parts[-1].s)
		self.parts += (Part(Line(p, u), s, n),)
		
	def change_s(self, part_index, new_s):
		"""Change the length of one of the ray parts.
		
		Args:
			part_index (int): the index of the part to alter
			new_s (float): the new length pf that part
		
		"""
		self.parts[part_index].s = new_s
		
	def draw(self):
		"""Draw the ray.
		
		This method does nothing in the elements realm,
		but should be overloaded is there is a graphical counterpart
		In this case, the ray should be (re)drawn
		"""
		pass
	
	def move_p0(self, dx, dy):
		"""Translate the ray starting point, leaving the direction unchanged."""
		self.parts[0].line.p.translate(dx=dx, dy=dy)
		
	def change_line_0(self, line):
		"""Change the ray starting line."""
		self.parts[0].line = line.copy()
	
	@property
	def config(self):  # noqa: D401
		"""Configuration dictionary."""
		return {'parts': [part.config for part in self.parts]}
	
	def propagate(self, scene):
		"""Propagate ray across scene."""
		
		# get the first part
		part0 = self.parts[0]
		# Find in which region we start.
		# Starting point (part0.line.p) inside region ?
		# part0.line.u direction is often a good choice
		# since if it is tangential to the region,
		# there would be no intersection anyway
		current_region = scene.region_at(line=part0.line)
		# set first part refractive index
		part0.n = current_region.n
		# start with only this first part
		self.parts = [part0]
		# initialize to last refractive index encountered by this ray
		cont = 20  # set to the maximum number of ray parts
		while cont:
			smin = None
			intersections = []
			last_part_line = self.parts[-1].line
			
			for region in scene.regions:
				intersections.extend(region.intersection(last_part_line, 1))
			
			if intersections:
				# intersection returns (i_point, smin, eN, eT)
				# sort on the second item (smin), smaller first
				intersections.sort(key=itemgetter(1))
				
				for intersection in intersections:
					# point just after the next intersection
					# take a margin to avoid roundoff error
					# and jump across multiple tangent surfaces
					margin = float_info.epsilon * 1000
					s_ahead = intersection.s + margin
					point_ahead = last_part_line.point(s_ahead)
					region_ahead = scene.region_at(point_ahead)
					if region_ahead.n != current_region.n:
						# found a real diopter
						region2 = region_ahead
						(i_point, smin, eN, eT) = intersection
						break
			
			if smin is not None:
				n2 = region2.n
				self.change_s(-1, smin)
				cont -= 1
				# add next part only if we are going to continue
				# otherwise we could have a last part going
				# straight through regions
				# since when cont=0, no intersection is checked
				if cont > 0:
					# find next direction of propagation
					# for now, just lines
					u1 = self.parts[-1].line.u
					# u1 component along eN (normal to interface)
					u1N = u1 * eN
					# u1 component along eT (tangent to interface)
					u1T = u1 * eT
					# refractive index of the incident medium
					n1 = self.parts[-1].n
					# u2N^2
					u2N2 = (
					  ((n2 / n1) ** 2 - 1) * u1T ** 2
					  + (n2 / n1) ** 2 * u1N ** 2
					)
					if u2N2 >= 0:
						# refraction
						# sqrt() but with the same sign as u1N
						u2N = math.copysign(math.sqrt(u2N2), u1N)
						n_next = n2
						next_region = region2
					else:
						# total internal reflection
						u2N = - u1N
						n_next = n1
						next_region = current_region
					u_next = u1T * eT + u2N * eN
					u_next.normalize()
					#print "u_next = "
					# Note: float("inf") should be replaced with math.float_inf
					#       when python 3.4 support is dropped.
					self.add_part(u_next, float("inf"), n_next)
					current_region = next_region
			else:
				cont = 0
				# redraw anyway (this handles the case where
				#                there is no intersection anymore)
				self.draw()
	
	def __repr__(self):
		return 'Ray(line0={}, s={}, n={}, tag="{}")'.format(
		        self.parts[0].line, self.parts[0].s, self.parts[0].n, self.tag)
		
	def translate(self, **kwargs):
		"""Translate the ray as a whole.
		
		Same syntax and same side effects as
		:meth:`geoptics.elements.vector.Point.translate`
		
		Likewise, it is possible to
		insert a ``.copy()`` to avoid side-effects.
		FIXME: :meth:`copy()` not implemented yet...
		
		return `self` for convenience
		"""
		
		for part in self.parts:
			part.translate(**kwargs)
		return self
