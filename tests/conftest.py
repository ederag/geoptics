import os

import pytest

import yaml


def pytest_addoption(parser):
	parser.addoption("--test-scripts", action="store_true",
	                 help="test installed scripts")


@pytest.fixture(params=["elements", "guis.qt"])
def scene(request):
	"""Return an empty scene."""
	scene_type = request.param
	if scene_type == "elements":
		from geoptics.elements import scene
	elif scene_type == "guis.qt":
		# dynamically load the qapp fixture
		request.getfixturevalue('qapp')
		from geoptics.guis.qt import scene
	else:
		raise ValueError()
	sc = scene.Scene()
	return sc


@pytest.fixture
def scene_polycurve_beam_singleray(scene):
	"""Return a Scene with Polycurve region + Beam and SingleRay sources."""
	from geoptics.elements.vector import Point, Vector
	
	n = 1.5
	m1 = Point(70, 60)
	
	# rp1
	cls = scene.class_map['Regions']['Polycurve']
	rp1 = cls(n=n, scene=scene)
	rp1.start(m1)
	m2 = Point(70, 190)
	rp1.add_line(m2)
	m3 = Point(110, 190)
	rp1.add_line(m3)
	m4 = Point(110, 60)
	tg4 = Vector(10, -20)
	#rp1.add_line(m4)
	rp1.add_arc(m4, tg4)
	rp1.close()
	
	return scene


def load_from_file(filename, category_str, scene):
	"""Return an item from a file.
	
	Args:
		category_str: 'Regions' or 'Sources'
	"""
	dirname = os.path.dirname(__file__)
	full_filename = os.path.join(dirname, filename)
	with open(full_filename, 'r') as f:
		config = yaml.safe_load(stream=f)
		class_name = config['Class']
		rp1_cls = scene.class_map[category_str][class_name]
		item = rp1_cls.from_config(config, scene=scene)
	return item


@pytest.fixture
def region_polycurve_1(scene):
	"""Return a Polycurve region."""
	filename = './region_polycurve_1.geoptics'
	category_str = 'Regions'
	item = load_from_file(filename, category_str, scene)
	return item


@pytest.fixture
def source_singleray_1(scene):
	"""Return a SingleRay source."""
	filename = './source_singleray_1.geoptics'
	category_str = 'Sources'
	item = load_from_file(filename, category_str, scene)
	return item


@pytest.fixture
def source_beam_1(scene):
	"""Return a Beam source."""
	filename = './source_beam_1.geoptics'
	category_str = 'Sources'
	item = load_from_file(filename, category_str, scene)
	return item


@pytest.fixture(params=["./region_polycurve_1.geoptics"])
def region(request, scene):
	"""Return a generic region."""
	filename = request.param
	category_str = 'Regions'
	item = load_from_file(filename, category_str, scene)
	return item


@pytest.fixture(params=["./source_singleray_1.geoptics",
                        "./source_beam_1.geoptics"])
def source(request, scene):
	"""Return a generic source."""
	filename = request.param
	category_str = 'Sources'
	item = load_from_file(filename, category_str, scene)
	return item
