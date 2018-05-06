import pytest


@pytest.fixture()
def scene(qapp):
	"""Return an empty guis.qt.scene."""
	from geoptics.guis.qt import scene
	return scene.Scene()


@pytest.fixture(params=["direct creation",
                        "scene.load",
                        "load individually",
                        ])
def creation_type(request):
	"""Return items creation type."""
	return request.param


@pytest.fixture()
def gui(qapp):
	"""Return a guis.qt GUI."""
	from geoptics.guis.qt.main import Gui
	
	gui = Gui()
	# avoid flickering windows
	gui.setVisible(False)
	
	return gui
