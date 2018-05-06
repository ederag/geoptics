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


"""Define a geometric Segment [M1, M2]."""


from geoptics.elements.vector import Vector_M1M2

from .line import Line


class Segment(object):
	"""Segment defined by its two ends: M1 et M2.
	
	Args:
		M1 (Point): first end
		M2 (Point): second end
	"""
	
	def __init__(self, M1, M2):
		self.M1 = M1.copy()
		self.M2 = M2.copy()
	
	@property
	def config(self):  # noqa: D401
		"""Configuration dictionary."""
		return {'Class': 'Segment',
		        'M1': self.M1.config,
		        'M2': self.M2.config,
		        }
	
	def normal(self, normalized=False):
		"""Return a normal to the segment.
		
		Args:
			normalized (bool):  if True, return a unit vector.
		Returns:
			:class:`~.elements.vector.Vector`
		
		"""
		return Vector_M1M2(self.M1, self.M2).normal(normalized=normalized)
	
	def middle(self):
		"""Return the middle of the segment."""
		return (self.M1 + self.M2) * 0.5
	
	def intersection(self, other, sign_of_s=0):
		"""Intersections of the segment with another element.
		
		Args:
			other (Line): another element (as of v0.18, it must be a Line)
			sign_of_s (int): if `sign_of_s !=0`,
				consider other as a half line.
				i.e. `s_other` must have the same sign
				as `sign_of_s` or intersection will be empty
		Returns:
			:obj:`list` of :class:`.Intersection`: list of intersections
		"""
		if isinstance(other, Line):
			result = Line(self.M1,
			              Vector_M1M2(self.M1, self.M2)
			              ).intersection(other, sign_of_s)
			if not result:
				# no intersection
				return []
			else:
				# there should be only one intersection
				# split the sequence unpacking in two chunks for
				# kdevelop semantic analysis
				intersection, = result
				Mi, s, eN, eT = intersection
				if abs(self.M2.x - self.M1.x) > abs(self.M2.y - self.M1.y):
					# M1M2 closer to x axis
					if (self.M2.x > self.M1.x):
						# M2 to the right of M1
						if (Mi.x < self.M1.x) or (Mi.x > self.M2.x):
							# outside
							return []
					else:
						# M2 to the left of M1
						if (Mi.x < self.M2.x) or (Mi.x > self.M1.x):
							# outside
							return []
				else:
					# M1M2 closer to y axis
					if (self.M2.y > self.M1.y):
						# M2 above M1
						if (Mi.y < self.M1.y) or (Mi.y > self.M2.y):
							# outside
							return []
					else:
						# M2 below M1
						if (Mi.y < self.M2.y) or (Mi.y > self.M1.y):
							# outside
							return []
		else:
			raise NotImplementedError(
			   "intersection between Line and {}".format(type(other))
			)
		return result
	
	def __repr__(self):
		return "Segment({M1}, {M2})".format(**vars(self))
	
	def translate(self, **kwargs):
		"""Translate the segment as a whole.
		
		Same syntax and same side effects as
		:py:func:`geoptics.elements.vector.Point.translate`
		
		Likewise, it is possible to
		insert a ``.copy()`` to avoid side-effects.
		FIXME: :meth:`copy()` not implemented yet...
		
		return `self` for convenience
		"""
		self.M1.translate(**kwargs)
		self.M2.translate(**kwargs)
		return self
