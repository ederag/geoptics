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


"""Define :term:`Lines`."""


from collections import namedtuple
from math import cos, pi, sin

from geoptics.elements.vector import Point, Vector


Intersection = namedtuple('Intersection', 'p, s, eN, eT')
Intersection.__doc__ += (
	""": Intersection between a :class:`Line` and another element
	
	Attributes:
		p (:class:`.Point`): point of intersection
		
		s (float): `s` multiplier of the :class:`Line` (p0, u0),
		            such that ``p = p0 + u0 * s``
		
		eN (:class:`.Vector`): unit vector normal to the other element,
		                       at the intersection
		
		eT (:class:`.Vector`): unit vector tangent to the other element,
	                           at the intersection
	"""
)

# in python 3.5 it will be possible to set the doctring for properties:
#Intersection.p.__doc__ = "`Point` of intersection"


class Line(object):
	"""Line defined by a point `p` and a direction vector `u`.
	
	Args:
		p (Point): Reference point belonging to the line
		u (Vector): Direction vector
	
	"""
	
	def __init__(self, p=None, u=None):
		if p is None:
			self.p = Point(x=0, y=0)
		else:
			self.p = p.copy()
		if u is None:
			self.u = Vector(x=1, y=0)
		else:
			self.u = u.copy()
	
	@property
	def config(self):  # noqa: D401
		"""Configuration dictionary."""
		return {'p': self.p.config,
		        'u': self.u.config,
		        }
	
	def copy(self):
		"""Return an independent copy."""
		return Line(self.p, self.u)
	
	@classmethod
	def from_config(cls, config):
		"""Alternate constructor.
		
		Args:
			config (dict): Configuration dictionary
		
		Returns:
			Line: new Line instance
		
		Examples:
			>>> from geoptics.elements.vector import Point, Vector
			>>> p = Point(10, 20)
			>>> u = Vector(30, 60)
			>>> line1 = Line(p, u)
			>>> config = line1.config
			>>> line2 = Line.from_config(config)
			>>> line2.config == config
			True
		
		"""
		p = Point.from_config(config['p'])
		u = Vector.from_config(config['u'])
		return cls(p, u)
	
	def normal(self, normalized=False):
		"""Return a vector orthogonal to the line.
		
		Args:
			normalized (bool): if True, return a unit vector.
		
		Returns:
			:class:`.Vector`
		
		"""
		normal = self.u.normal(normalized)
		return normal
	
	def tangent(self, normalized=False):
		"""Return a tangent vector to the line.
		
		For a line, this is basically `u` itself.
		
		Args:
			normalized (bool): if True, return a unit vector.
		
		Returns:
			:class:`.Vector`
		
		"""
		if normalized:
			tangent = self.u.copy()
			tangent.normalize()
			return tangent
		else:
			return self.u.copy()
	
	def intersection(self, other, sign_of_s=0):
		"""Intersections of the line with another line.
		
		Args:
			other (Line): another line.
			sign_of_s (float):
				if ``sign_of_s !=0``, consider other as a half line,
				and search for intersections with `s` having the
				same sign as `sign_of_s`.
		
		Returns:
			:obj:`list` of :class:`Intersection`:
				list either empty (no intersection),
				or holding a single intersection.
				
				This is done for consistency with other elements that
				can have multiple intersections with a line.
		
		"""
		if isinstance(other, Line):
			if other.u.colinear(self.u):
				result = []
			else:
				s = ((
				      (self.p.x - other.p.x) * self.u.y -
				      (self.p.y - other.p.y) * self.u.x
				     ) /
				      (other.u.x * self.u.y - other.u.y * self.u.x))
				if (sign_of_s == 0 and s != 0) or (s * sign_of_s > 0):
					Mi = Point(other.p.x + s * other.u.x,
					           other.p.y + s * other.u.y)
					eN = self.normal(normalized=True)
					eT = self.tangent(normalized=True)
					result = [Intersection(Mi, s, eN, eT)]
				else:
					result = []
		else:
			raise NotImplementedError(
			             "intersection between Line and {}".format(type(other)))
		return result
	
	@staticmethod
	def interpolate(line_start, line_end, x):
		"""Interpolated line.
		
		The returned line is interpolated between two given lines,
		going ccw from `line_start` to `line_end`.
		
		The interpolation is done on `Line.p` and on the `Line.u` angle.
		
		Args:
			line_start (Line): The starting line.
			line_end (Line): The ending line.
			x (float):
				the fraction, between 0.0 (starting line) and 1.0 (ending line).
		
		Returns:
			Line: Interpolated line.
		
		"""
		
		p = (1 - x) * line_start.p + x * line_end.p
		angle_start = line_start.u.theta_x()
		angle_end = line_end.u.theta_x()
		if angle_end < angle_start:
			# we want to go ccw from start to end
			angle_end += 2 * pi
		angle = (1 - x) * angle_start + x * angle_end
		u = Vector(x=cos(angle), y=sin(angle))
		return Line(p=p, u=u)
	
	def point(self, s):
		"""Return the :class:`.Point` at the position ``p + s * u``."""
		return Point(self.p.x + s * self.u.x,
		             self.p.y + s * self.u.y)
	
	def __repr__(self):
		return "Line({p}, {u})".format(**vars(self))
	
	def translate(self, **kwargs):
		"""Translate the starting point.
		
		Same syntax and same side effects as
		:py:func:`geoptics.elements.vector.Point.translate`
		
		Likewise, it is possible to insert a ``.copy()``
		to avoid side-effects.
		
		return `self` for convenience
		"""
		self.p.translate(**kwargs)
		return self
