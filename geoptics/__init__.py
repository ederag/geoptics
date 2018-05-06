"""Geoptics package composition.

- :term:`elements`: the physical layer (e.g. ray propagation)

- guis: the visual display and control

- shared: common tools

"""

__version__ = "0.19"


import logging
# https://docs.python.org/2/howto/logging.html#advanced-logging-tutorial
logger = logging.getLogger(__name__)   # noqa: E402
# this the toplevel file, hence the toplevel logger
# beware that without a setLevel() somewhere,
# the default value (warning) will be used, so no debug message will be shown
# give the level there, for now
# FIXME: this should be done in the application files. How ?
#logger.setLevel(logging.DEBUG)
logger.setLevel(logging.WARNING)
# this is a basic handler, with output to stderr
logger_handler = logging.StreamHandler()
formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
logger_handler.setFormatter(formatter)
del formatter
logger.addHandler(logger_handler)
del logger_handler
