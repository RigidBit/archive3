from flask import Flask
from flask_testing import LiveServerTestCase
import os
import psycopg2
import requests
import sys
import time
import unittest
import uuid

# Fix path to allow application import.
sys.path.insert(2, os.path.abspath(os.path.join(sys.path[0], "..", "archive3")))
from web import app as application
from database import connect

# Suppress logging output.
import os
import logging
logging.getLogger("werkzeug").disabled = True
os.environ["WERKZEUG_RUN_MAIN"] = "true"

class TestWeb(LiveServerTestCase):

	@classmethod
	def setUpClass(self):
		self.connection = connect()
		self.test_data = {}
		self.test_data["api_key"] = None # Placeholder
		self.test_data["unverified_challenge"] = None # Placeholder

	def create_app(self):
		app = application
		app.config["TESTING"] = True
		app.config["LIVESERVER_PORT"] = 0
		return app

	# Basic Routes

	def test_root(self):
		response = requests.get(self.get_server_url())
		self.assertEqual(response.status_code, 200)

	def test_recent(self):
		response = requests.get(self.get_server_url() + "/recent")
		self.assertEqual(response.status_code, 200)

	def test_contact(self):
		response = requests.get(self.get_server_url() + "/contact")
		self.assertEqual(response.status_code, 200)

	def test_faq(self):
		response = requests.get(self.get_server_url() + "/faq")
		self.assertEqual(response.status_code, 200)

	def test_ping(self):
		response = requests.get(self.get_server_url() + "/ping")
		self.assertEqual(response.status_code, 200)

	def test_privacy_policy(self):
		response = requests.get(self.get_server_url() + "/privacy-policy")
		self.assertEqual(response.status_code, 200)

	def test_terms_of_service(self):
		response = requests.get(self.get_server_url() + "/terms-of-service")
		self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
	unittest.main()
