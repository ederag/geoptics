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


"""Define an arc of a circle."""


from math import pi, sqrt

from geoptics.elements.vector import Vector_M1M2

from .line import Intersection, Line


class Arc(object):
	"""Arc of a circle.
	
	Args:
		M1 (Point): starting point
		M2 (Point): ending point
		tangent (Vector): tangent to the arc at the starting point M1
	"""
	
	def __init__(self, M1, M2, tangent):
		self.M1 = M1.copy()
		self.M2 = M2.copy()
		self.tangent = tangent.copy()
		self.C = self.center()
		self.r = self.radius()
		self.theta1 = Vector_M1M2(self.C, self.M1).theta_x()
		self.theta2 = Vector_M1M2(self.C, self.M2).theta_x()
		self.ccw = self.ccw()
	
	def center(self):
		"""Return the arc center."""
		
		# middle of the chord
		Mm = (self.M1 + self.M2) * 0.5
		# normal to the chord
		Vch = Vector_M1M2(self.M1, self.M2).normal()
		# normal to the tangent
		Vtg = self.tangent.normal()
		# normally there should be only one intersection
		# there should be only one intersection
		intersection, = Line(Mm, Vch).intersection(Line(self.M1, Vtg))
		C = intersection.p
		return C
	
	@property
	def config(self):  # noqa: D401
		"""Configuration dictionary."""
		return {'Class': 'Arc',
		        'M1': self.M1.config,
		        'M2': self.M2.config,
		        'tangent': self.tangent.config,
		        }
	
	def radius(self):
		"""Return the arc radius of curvature."""
		return Vector_M1M2(self.M1, self.center()).norm()
	
	def ccw(self):
		"""Return true if the arc goes from M1 to M2 ccw."""
		CM1 = Vector_M1M2(self.C, self.M1)
		return ((CM1.x * self.tangent.y - CM1.y * self.tangent.x) > 0)
	
	def __contains__(self, M):
		"""Return `True` if the point M belongs to the arc sector.
		
		Distances are not checked.
		"""
		theta_i = Vector_M1M2(self.C, M).theta_x()
		if self.theta2 < self.theta1:
			if (self.theta2 < theta_i) and (theta_i < self.theta1):
				return not self.ccw
		else:
			if (
			   ((self.theta2 < theta_i) and (theta_i <= pi)) or
			   ((theta_i > (-pi)) and (theta_i < self.theta1))
			   ):
				return not self.ccw
					
	def intersection(self, other, sign_of_s=0):
		"""Intersections of the arc with another element.
		
		Args:
			other (Line): another element (as of v0.18, it must be a Line)
			sign_of_s (int):
				if `sign_of_s !=0`, consider other as a half line.
				i.e. `s_other` must have the same sign
				as `sign_of_s` or intersection will be empty
		
		Returns:
			:obj:`list` of :class:`.Intersection`: list of intersections
		
		"""
		result = []
		if isinstance(other, Line):
			s_list = []
			a = other.u.x ** 2 + other.u.y ** 2
			if a != 0:
				b = (other.u.x * (other.p.x - self.C.x) +
				     other.u.y * (other.p.y - self.C.y)
				     )
				c = ((other.p.x - self.C.x) ** 2 +
				     (other.p.y - self.C.y) ** 2 -
				     self.r ** 2
				     )
				# reduced discriminant
				delta = b ** 2 - a * c
				# compute roots
				if delta > 0:
					# this way is numerically more stable (?)
					if b >= 0:
						q = -b - sqrt(delta)
					else:
						q = -b + sqrt(delta)
					# two roots
					s1 = q / a
					s2 = c / q
					s_list.extend([s1, s2])
				elif delta == 0:
					# one root
					s = -b / a
					s_list.append(s)
			for s in s_list:
				# intersection point
				M = other.point(s)
				if (M in self) and (s * sign_of_s >= 0):
					# normal is \vec{CM}/CM
					eN = Vector_M1M2(self.C, M).normalize()
					# tangent is orthogonal to normal for a circle
					eT = eN.normal(normalized=True)
					result.append(Intersection(M, s, eN, eT))
		else:
			raise NotImplementedError(
			            "intersection between Line and {}".format(type(other)))
		return result
	
	def __repr__(self):
		return "Arc({M1}, {M2}, {tangent})".format(**vars(self))
	
	def translate(self, **kwargs):
		"""Translate the segment as a whole.
		
		Same syntax and same side effects as
		:py:func:`geoptics.elements.vector.Point.translate`
		
		Likewise, it is possible to
		insert a `.copy()` to avoid side-effects.
		FIXME: copy() not implemented yet...
		
		Returns:
			`self`, for convenience
		
		Examples:
			>>> from geoptics.elements.vector import Point, Vector
			>>> M1 = Point(110, 190)
			>>> M2 = Point(120, 60)
			>>> tg = Vector(10, -20)
			>>> arc = Arc(M1, M2, tg)
			>>> arc.C
			Point(-44.54545454545456, 112.72727272727272)
			>>> tr = Vector(5, 15)
			>>> arc.translate(dv=tr)
			>>> arc.M1
			Point(115, 205)
			>>> arc.M2
			Point(125, 75)
			>>> arc.C
			Point(-39.54545454545456, 127.72727272727272)
		
		"""
		self.M1.translate(**kwargs)
		self.M2.translate(**kwargs)
		self.C.translate(**kwargs)
