"""
Run a function from a JSON configuration file.
"""

import json


def from_config(func):
	"""Run a function from a JSON configuration file."""
	
	def decorator(filename):
		with open(filename, 'r') as file_in:
			config = json.load(file_in)
		return func(**config)
	
	return decorator
