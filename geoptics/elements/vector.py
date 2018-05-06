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


"""Points and vectors in 2D."""


from math import atan2, sqrt


class Point(object):
	"""2D point."""
	
	__slots__ = ('x', 'y')
	
	def __init__(self, x=None, y=None):
		self.x = x
		self.y = y
	
	@classmethod
	def from_config(cls, config):
		"""Alternate constructor.
		
		Args:
			config (dict): Configuration dictionary
		
		Returns:
			Point: new Point instance
		
		Examples:
			>>> v1 = Point(10, 20)
			>>> config = v1.config
			>>> v2 = Point.from_config(config)
			>>> v2.config == config
			True
		
		"""
		return cls(**config)
	
	def translate(self, dv=None, dx=0, dy=0):
		"""Translate the point.
		
		The translation must be given as a single vector (``dv``)
		or with ``dx`` and/or ``dy``.
		If ``dv`` is given, ``dx`` and ``dy`` are discarded.
		
		For example::
		
			>>> p = Point(30, 50)
			>>> dv = Vector(x=10, y=20)
			>>> p.translate(dv)
			Point(40, 70)
		
		is the same as::
		
			>>> p = Point(30, 50)
			>>> p.translate(dx=10, dy=20)
			Point(40, 70)
		
		It is possible to change only one coordinate
			>>> p = Point(30, 50)
			>>> p.translate(dx=10)
			Point(40, 50)
		
		Beware that the transformation is done in-place.
		this can lead to side effects.
		For example, in order to leave p1 untouched,
		a `.copy()` has to be inserted::
		
			>>> p2 = p.copy().translate(dx=10, dy=20)
		
		Args:
			dv (Vector, optional): Translation vector
			dx (number, optional): Translation amount along `x`
			dy (number, optional): Translation amount along `y`
		
		Returns:
			Point:
				The point has been modified in-place, but for convenience,
				the point itself is also returned
		
		"""
		if dv is not None:
			self.x += dv.x
			self.y += dv.y
		else:
			self.x += dx
			self.y += dy
		return self
	
	@property
	def config(self):  # noqa: D401
		"""Configuration dictionary."""
		return {'x': self.x, 'y': self.y}
	
	def copy(self):
		"""Return an independent copy of the point."""
		p = Point(self.x, self.y)
		return p
	
	def __add__(self, other):
		# adding Points is meaningful for interpolation
		if isinstance(other, (Vector, Point)):
			return Point(self.x + other.x, self.y + other.y)
		else:
			raise NotImplementedError("Trying to add {}".format(type(other)))
	
	def __eq__(self, other):
		return (self.x == other.x) and (self.y == other.y)
	
	def __iter__(self):
		return iter((self.x, self.y))
	
	def __mul__(self, other):
		if isinstance(other, (float, int)):
			return Point(self.x * other, self.y * other)
		else:
			raise NotImplementedError("Trying to add {}".format(type(other)))
			
	def __rmul__(self, other):
		return self.__mul__(other)
	
	def __repr__(self):
		return "Point({}, {})".format(self.x, self.y)


class Vector(object):
	"""2D Vector."""
	
	__slots__ = ('x', 'y')
	
	def __init__(self, x, y):
		self.x = x
		self.y = y
	
	@property
	def config(self):  # noqa: D401
		"""Configuration dictionary."""
		return {'x': self.x, 'y': self.y}
	
	@classmethod
	def from_config(cls, config):
		"""Alternate constructor.
		
		Args:
			config (dict): Configuration dictionary
		
		Returns:
			Vector: new Vector instance
		
		Examples:
			>>> v1 = Vector(10, 20)
			>>> config = v1.config
			>>> v2 = Vector.from_config(config)
			>>> v2.config == config
			True
		
		"""
		return cls(**config)
	
	def norm(self):
		"""Return the vector norm."""
		return sqrt(self.x * self.x + self.y * self.y)
	
	def normalize(self):
		"""Normalize vector (divide it by its norm.
		
		The normalization is done in-place,
		but also return self, for convenience.
		"""
		norm = self.norm()
		self.x = self.x / norm
		self.y = self.y / norm
		return self
	
	def normal(self, normalized=False):
		"""Return a vector orthogonal to self."""
		n = Vector(self.y, -self.x)
		if normalized:
			n.normalize()
		return n
	
	def copy(self):
		"""Return an independent copy of the vector."""
		return Vector(self.x, self.y)
		
	def colinear(self, other):
		"""Return True if self and other are colinear."""
		return (self.x * other.y - self.y * other.x) == 0
	
	def theta_x(self):
		"""Return the inclination angle over the x axis, in rad."""
		return atan2(self.y, self.x)
			
	def __imul__(self, other):
		# in-place multiplication for "*="
		if isinstance(other, Vector):
			self.x *= other.x
			self.y *= other.y
		else:
			self.x *= other
			self.y *= other
			return self
	
	def __iter__(self):
		return iter((self.x, self.y))
	
	def __mul__(self, other):
		if isinstance(other, Vector):
			# scalar product
			return self.x * other.x + self.y * other.y
		else:
			return Vector(self.x * other, self.y * other)
	
	def __rmul__(self, other):
		return self.__mul__(other)
	
	def __add__(self, other):
		if isinstance(other, Vector):
			return Vector(self.x + other.x, self.y + other.y)
		else:
			raise NotImplementedError("Trying to add {}".format(type(other)))
	
	def __repr__(self):
		return "Vector({}, {})".format(self.x, self.y)


class Vector_M1M2(Vector):
	"""Vector joining M1 to M2.
	
	Args:
		M1 (Point): starting point
		M2 (Point): end point
	"""
	
	__slots__ = ()  # prevent any dict to be created (~ half lighter)
	
	def __init__(self, M1, M2):
		Vector.__init__(self, M2.x - M1.x, M2.y - M1.y)
