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


"""Define regions.

Specific region classes should inherit from the generic :class:`.Region`.

Currently an all-purpose :class:`.Polycurve` is available.
"""


from geoptics.elements.line import Line
from geoptics.elements.vector import Point, Vector

from .arc import Arc
from .segment import Segment


class Region(object):
	"""Region of space."""
	
	def __init__(self, n=None, scene=None):
		#: :term:`optical index`
		self.n = n
		#: physical scene where the region will be placed
		self.scene = scene
		if scene:
			self.scene.add(self)
	
	def contains(self, point=None, u=None, line=None):  # noqa: D400
		"""Is a given point contained in this region ?
		
		Alternatively, `line` can be given,
		in which case `point` is taken from `line.p`,
		and `u` from `line.u`.
		
		Args:
			point (Point): The point of interest
			u (Vector): Searching direction
			line (Line):
				Contains both point and searching direction (see above)
		
		"""
		if line is None:
			line = Line(p=point, u=u)
		intersections = self.intersection(line, sign_of_s=1)
		if len(intersections) % 2:
			# odd number of intersections with the region
			# point is inside it
			return True
		else:
			return False
	
	def intersection(self, other, sign_of_s=0):
		"""Return the intersections between the region boundaries and other.
		
		By default, return an empty list.
		This method should be overloaded by specific region classes.
		
		Args: same as :meth:`.elements.segment.Segment.intersection`
		"""
		return []


class Polycurve(Region):
	"""Define a region inside curves (line segments, arcs, ...).
	
	Args:
		n (float): :term:`optical index` of the region
		M1 (Point): first point
		tag (str): tag for this region
	
	Returns:
		Region: a region
	
	"""
	
	def __init__(self, n=None, scene=None, tag=None):
		Region.__init__(self, n=n, scene=scene)
		
		self.tag = tag
		
	def start(self, M_start):
		"""Initialize the region boundary.
		
		Set the starting point to `M_start`
		"""
		self.M = [M_start.copy()]
		self.curves = []
		
	def add_line(self, M_next):
		"""Add a straight section to the region boundary.
		
		The added section is actually a :class:`~.elements.segment.Segment`,
		between the last point and the given `M_next` point.
		"""
		self.curves.append(Segment(self.M[-1], M_next))
		self.M.append(M_next)
	
	def add_arc(self, M_next, tangent):
		"""Add an :class:`~.elements.arc.Arc` curve to the boundary.
		
		The arc starts from the last point with the given tangent,
		and ends on M_next.
		"""
		self.curves.append(Arc(self.M[-1], M_next, tangent))
		self.M.append(M_next)
			
	def close(self):
		"""Join the last point to the first point with a segment."""
		self.curves.append(Segment(self.M[-1], self.M[0]))
	
	@property
	def config(self):  # noqa: D401
		"""Configuration dictionary."""
		return {'Class': 'Polycurve',
		        'tag': self.tag,
		        'n': self.n,
		        'curves': [curve.config for curve in self.curves],
		        }
	
	@classmethod
	def from_config(cls, config, scene=None, tag=None):
		"""Alternate constructor.
		
		Args:
			config (dict): Configuration dictionary
		
		Returns:
			:class:`.Polycurve`: new Polycurve instance
		
		"""
		
		if tag is None:
			tag = config.get('tag')
		region = cls(scene=scene, tag=tag)
		curves_config = config['curves']
		M_start = Point.from_config(curves_config[0]['M1'])
		region.start(M_start)
		region.tag = config.get('tag')
		region.n = config['n']
		for curve_config in curves_config:
			cls = curve_config['Class']
			if cls == 'Segment':
				M_next = Point.from_config(curve_config['M2'])
				region.add_line(M_next)
			elif cls == 'Arc':
				M_next = Point.from_config(curve_config['M2'])
				tangent = Vector.from_config(curve_config['tangent'])
				region.add_arc(M_next, tangent)
			else:
				raise NotImplementedError
		# normally, the stored polycurves are already closed
		# (the last point is equal to the first one)
		# no need for a final close()
		return region
	
	def intersection(self, other, sign_of_s=0):
		"""Return the intersections between the region boundaries and other.
		
		Args: same as :meth:`.elements.segment.Segment.intersection`
		"""
		result = []
		for curve in self.curves:
			result.extend(curve.intersection(other, sign_of_s))
		return result
	
	def translate(self, **kwargs):
		"""Translate the region as a whole.
		
		Same syntax and same side effects as
		:py:func:`geoptics.elements.vector.Point.translate`
		
		Likewise, it is possible to
		insert a ``.copy()`` to avoid side-effects.
		FIXME: :meth:`copy()` not implemented yet...
		
		Return `self` for convenience
		"""
		for curve in self.curves:
			curve.translate(**kwargs)
		return self
