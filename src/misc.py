import datetime
import json
import os
import sys
import threading

class DatetimeEncoder(json.JSONEncoder):
	def default(self, obj):
		try:
			return super(DatetimeEncoder, obj).default(obj)
		except TypeError:
			return str(obj)

def data_record_add_proof_status(record):
	record = dict(record)
	record["proof_available"] = int((datetime.datetime.now() - record["timestamp"]).total_seconds()) > int(os.getenv("RIGIDBIT_PROOF_DELAY"))
	return record

def log_message(message):
	if os.getenv("ARCHIVE3_VERBOSE") == "true":
		print(threading.current_thread().name, message)
		sys.stdout.flush()

def hash_to_path(hash):
	depth = int(os.getenv("ARCHIVE3_SCREENSHOT_DIR_DEPTH"))
	dirs = []
	for i in range(0, depth): dirs.append(hash[i])
	return os.path.join(os.getcwd(), os.getenv("ARCHIVE3_SCREENSHOT_DIR"), "/".join(dirs))

def page_title(id):
	switcher = {
		"404": "Error 404: Not Found - Archive3",
		"500": "Error 500: Internal Server Error - Archive3",
		"api_activate": "API Key Activated - Archive3",
		"api_help": "API Help - Archive3",
		"api_request": "API Key Requested - Archive3",
		"buried": "Manage Buried - Archive3",
		"contact": "Contact Us - Archive3",
		"default": "Archive3: Internet Archival Service with Blockchain Anchoring",
		"error": "Error - Archive3",
		"faq": "Frequently Asked Questions - Archive3",
		"manage": "Manage Submitted URLs - Archive3",
		"recent": "Recent Activity - Archive3",
		"search": "Search Results - Archive3",
		"stats": "Stats - Archive3",
		"submit": "Submit a URL - Archive3",
		"urls": "URL List - Archive3",
		"view": "View URL - Archive3",
		"pp": "Privacy Policy - Archive3",
		"tos": "Terms of Service - Archive3",
	}
	return switcher.get(id, "Archive3")
