"""
Decorators for the web and API endpoints.
"""

from flask import request
from functools import wraps
import json
import os

import database as db

def admin_required(func):
	"""Guard to ensure a valid admin password is provided."""
	def wrapper(*args, **kwargs):
		if not request.authorization or request.authorization.password != os.getenv("ARCHIVE3_ADMIN_PASSWORD"):
			return ("Could not authenticate!", 401, {"WWW-Authenticate": "Basic realm=\"Login Required\""})
		return func(*args, **kwargs)
	wrapper.__name__ = func.__name__
	return wrapper
