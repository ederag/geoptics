"""Tools that can be used by several backends."""

import inspect


def find_classes(module):
	"""Find classes in a given module.
	
	Args:
		module: a python module object
	
	Returns:
		dict: {name_str: cls} dictionnary
	
	"""
	
	# set module as a default argument to store it
	# predicate will be used with the member argument only
	# note: a lambda would be prettier here, but
	# pep8: E731 do not assign a lambda expression, use a def
	def predicate(member, module=module):
		return (inspect.isclass(member)
		        and member.__module__ == module.__name__)
	
	# getmembers return a list of tuples like
	# [('Beam', <class 'geoptics.guis.qt.sources.Beam'>), ...]
	lst = inspect.getmembers(module, predicate)
	return {name: cls for (name, cls) in lst}
