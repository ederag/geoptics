PACKAGE=geoptics
FIGURE_DIR=docs/figures

clean_egg-info:
	rm -rf GeOptics.egg-info/

clean: clean_egg-info
	# need the pycmd package
	py.cleanup
	rm -f *.xdot
	rm -rf .cache/
	rm -rf .pytest_cache/

distclean: clean
	rm -rf .tox/
	rm -rf .eggs/

html:
	make clean_egg-info
	cd docs && make html

# --------------------------------- tests ------------------------------------

check:
	# work around "py.test ." not setting PYTHONPATH correctly
	# http://stackoverflow.com/a/34140498/3565696
	# python3 -m pytest tests/
	
	# this one is recommended by
	# http://docs.pytest.org/en/latest/goodpractices.html#integrating-with-setuptools-python-setup-py-test-pytest-runner
	python3 setup.py test --addopts "-rs --doctest-modules"
	flake8 geoptics/ tests/ setup.py

vcheck:
	python3 setup.py test --addopts "-v -rs --doctest-modules"
	flake8 geoptics/ tests/ setup.py

vvcheck:
	python3 setup.py test --addopts "-vv -rs --doctest-modules"
	flake8 geoptics/ tests/ setup.py

coverage:
	python3 setup.py test --addopts "--cov-report=term-missing:skip-covered --cov=geoptics"

fixtures:
	PYTHONPATH=$(PYTHONPATH):. pytest --fixtures

pyreverse:
	# -my to show module names
	# -k to show only classes, not attributes or methods
	pyreverse -my -k -o xdot -p $(PACKAGE) $(PACKAGE)
	# how to put the generated files directly in the right place ?
	mv classes_$(PACKAGE).xdot packages_$(PACKAGE).xdot $(FIGURE_DIR)

graph_packages: pyreverse
	xdot $(FIGURE_DIR)/packages_geoptics.xdot &
graph_classes: pyreverse
	xdot $(FIGURE_DIR)/classes_geoptics.xdot &
