from flask import Flask
from flask_testing import LiveServerTestCase
import json
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

	# Static Routes

	def test_root(self):
		response = requests.get(self.get_server_url())
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

	# Admin Routes

	def test_buried(self):
		response = requests.get(self.get_server_url() + "/buried", auth=requests.auth.HTTPBasicAuth("", "password"))
		self.assertEqual(response.status_code, 200)

	def test_manage(self):
		response = requests.get(self.get_server_url() + "/manage", auth=requests.auth.HTTPBasicAuth("", "password"))
		self.assertEqual(response.status_code, 200)

	def test_stats(self):
		response = requests.get(self.get_server_url() + "/stats", auth=requests.auth.HTTPBasicAuth("", "password"))
		self.assertEqual(response.status_code, 200)

	# Public Dynamic Routes

	def test_recent(self):
		response = requests.get(self.get_server_url() + "/recent")
		self.assertEqual(response.status_code, 200)

	def test_search(self):
		response = requests.get(self.get_server_url() + "/search?q=google")
		self.assertEqual(response.status_code, 200)

	def test_submit(self):
		response = requests.get(self.get_server_url() + "/submit")
		self.assertEqual(response.status_code, 200)

	# Server needs tighter checks.
	# def test_submit_url_invalid(self):
	# 	data = {"url": ""}
	# 	response = requests.post(self.get_server_url() + "/submit", data=data)
	# 	self.assertEqual(response.status_code, 400)

	def test_submit_url_1(self):
		data = {"url": "https://www.google.com/"}
		response = requests.post(self.get_server_url() + "/submit", data=data)
		self.assertEqual(response.status_code, 200)

	def test_submit_url_2(self):
		data = {"url": "https://www.yahoo.com/"}
		response = requests.post(self.get_server_url() + "/submit", data=data)
		self.assertEqual(response.status_code, 200)

	def test_z_manage_urls(self):
		data = {"accepted": json.dumps([1]), "rejected": json.dumps([2])}
		response = requests.post(self.get_server_url() + "/manage", data=data, auth=requests.auth.HTTPBasicAuth("", "password"))
		self.assertEqual(response.status_code, 200)

	def test_z_view_url(self):
		response = requests.get(self.get_server_url() + "/view?url=https://google.com/")
		self.assertEqual(response.status_code, 200)

	def test_z_view_url_nonexistent(self):
		response = requests.get(self.get_server_url() + "/view?url=https://yahoo.com/")
		self.assertEqual(response.status_code, 404)

if __name__ == "__main__":
	unittest.main()
