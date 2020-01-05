from dotenv import load_dotenv
import boto3
import greenstalk
import hashlib
import json
import mimetypes
import os
import psycopg2
import requests
import sys
import threading
import time

import blockchain as b
import database as db
import misc
import screenshot as ss

def process_screenshot(connection, payload):
	# Validate URL
	misc.log_message(f"""Validating URL: {payload["url"]}""")
	try:
		headers = {"User-Agent": os.getenv("ARCHIVE3_USER_AGENT")}
		response = requests.get(payload["url"], headers=headers, timeout=int(os.getenv("ARCHIVE3_URL_TIMEOUT")))
	except:
		raise Exception(f"""Failure while loading URL: {payload["url"]}""")
	response.raise_for_status()

	# Generate Screenshot
	file_path_temp = ss.generate_screenshot({"url": payload["url"]})
	misc.log_message(f"Generated screenshot: {file_path_temp}")

	# Generate Block
	block = b.generate_screenshot_block(file_path_temp)
	hash = block["data_hash"]
	misc.log_message(f"Block created: {block['id']}")

	# Rename screenshot.
	file_path_screenshot = os.path.join(misc.hash_to_path(hash), hash + ".png")
	os.makedirs(os.path.dirname(file_path_screenshot), exist_ok=True)
	os.rename(file_path_temp, file_path_screenshot)
	misc.log_message(f"""Screenshot moved to destination: {file_path_screenshot}""")

	# Generate thumbnail.
	file_path_thumb = os.path.join(misc.hash_to_path(hash), hash + "_thumb.jpg")
	ss.generate_thumbnail(file_path_screenshot, file_path_thumb)
	misc.log_message(f"""Thumbnail created: {file_path_thumb}""")

	# Upload to S3.
	if os.getenv("AWS_S3_UPLOAD_ENABLED") == "true":
		s3 = boto3.resource("s3", aws_access_key_id=os.getenv("AWS_S3_ACCESS_KEY_ID"), aws_secret_access_key=os.getenv("AWS_S3_SECRET_ACCESS_KEY"))
		bucket = s3.Bucket(os.getenv("AWS_S3_BUCKET_ID"))
		bucket.put_object(Key=os.path.basename(file_path_screenshot), Body=open(file_path_screenshot, "rb"), StorageClass=os.getenv("AWS_S3_STORAGE_CLASS"), ACL="public-read", ContentType=mimetypes.guess_type(file_path_screenshot)[0])
		misc.log_message(f"""Uploaded to S3: {os.getenv("AWS_S3_CDN_BASE_URL")}{os.path.basename(file_path_screenshot)}""")
		bucket.put_object(Key=os.path.basename(file_path_thumb), Body=open(file_path_thumb, "rb"), StorageClass=os.getenv("AWS_S3_STORAGE_CLASS"), ACL="public-read", ContentType=mimetypes.guess_type(file_path_screenshot)[0])
		misc.log_message(f"""Uploaded to S3: {os.getenv("AWS_S3_CDN_BASE_URL")}{os.path.basename(file_path_thumb)}""")

	# Update url record.
	data = {"timestamp_updated": "NOW()"}
	db.update_url_record(connection, payload["id"], data)
	connection.commit()
	misc.log_message(f"""Updated url record: {payload["id"]}""")

	# Create data record.
	data = {"url_id": payload["id"], "hash": hash, "block_id": block["id"]}
	data_record_id = db.create_data_record(connection, data)
	connection.commit()
	misc.log_message(f"""Created data record: {data_record_id}""")

	# Delete screenshots.
	if os.getenv("ARCHIVE3_DELETE_SCREENSHOTS"):
		os.remove(file_path_screenshot)
		misc.log_message(f"""Deleted local screenshot: {file_path_screenshot}""")
		os.remove(file_path_thumb)
		misc.log_message(f"""Deleted local screenshot: {file_path_thumb}""")

def process_preview(connection, payload):
	# Check if URL already exists.
	if db.check_url_exists(connection, payload["url"]):
		db.delete_submission_record(connection, payload["id"])
		connection.commit()
		misc.log_message(f"""URL already exists: {payload["url"]}""")
		return

	# Validate URL
	misc.log_message(f"""Validating URL: {payload["url"]}""")
	try:
		headers = {"User-Agent": os.getenv("ARCHIVE3_USER_AGENT")}
		response = requests.get(payload["url"], headers=headers, timeout=int(os.getenv("ARCHIVE3_URL_TIMEOUT")))
	except:
		raise Exception(f"""Failure while loading URL: {payload["url"]}""")
	response.raise_for_status()

	# Generate screenshot.
	file_path_temp = ss.generate_screenshot({"url": payload["url"], "width": 1280, "height": 720, "delay": 1})
	misc.log_message(f"Generated screenshot: {file_path_temp}")

	# Compress screenshot.
	file_path_screenshot = os.path.join(os.getcwd(), os.getenv("ARCHIVE3_SCREENSHOT_DIR"), "preview-" + str(payload["id"]) + ".jpg")
	ss.compress_preview(file_path_temp, file_path_screenshot)
	misc.log_message(f"""Compressed screenshot created: {file_path_screenshot}""")

	# Remove temp file.
	os.remove(file_path_temp)
	misc.log_message(f"""Temp file deleted: {file_path_temp}""")

	# Update submission record.
	data = {"ready": "true"}
	db.update_submission_record(connection, payload["id"], data)
	connection.commit()
	misc.log_message(f"""Updated submission record: {payload["id"]}""")

def start_processing_thread():
	queue = greenstalk.Client(host=os.getenv("GREENSTALK_HOST"), port=os.getenv("GREENSTALK_PORT"), watch=[os.getenv("GREENSTALK_TUBE_QUEUE")])
	while True:
		job = queue.reserve()

		try:
			connection = psycopg2.connect(dbname=os.getenv("POSTGRESQL_DB"), host=os.getenv("POSTGRESQL_HOST"), port=os.getenv("POSTGRESQL_PORT"), user=os.getenv("POSTGRESQL_USER"), password=os.getenv("POSTGRESQL_PASS"))

			payload = json.loads(job.body)
			misc.log_message(f"Processing job: {payload}")

			# Process screenshot or preview.
			if payload["type"] == "screenshot":
				process_screenshot(connection, payload)
			elif payload["type"] == "preview":
				process_preview(connection, payload)
			else:
				raise Exception(f"""Invalid payload type: {payload["type"]}""")

			# Delete job.
			queue.delete(job)
			misc.log_message(f"Deleted job: {payload}")
		except:
			# Delete job.
			queue.delete(job)
			misc.log_message(f"Deleting failed job: {payload}")
			# Erase submission record if it exists.
			if payload["type"] == "preview":
				db.delete_submission_record(connection, payload["id"])
				connection.commit()
				misc.log_message(f"""Deleted submission record: {payload["id"]}""")
			# Update error count for url_id.
			record = db.get_url_record(connection, payload["id"])
			error_count = record["errors"] + 1
			db.update_url_record(connection, payload["id"], {"errors": error_count})
			connection.commit()
			misc.log_message(f"""Updating errors for url_id {payload["id"]}: {error_count}""")
			raise
		finally:
			connection.close()

##### ENTRY POINT #####

load_dotenv()

thread_count = int(os.getenv("ARCHIVE3_PROCESSING_THREADS"))
threads = []
while True:	
	if len(threads)	< thread_count:
		thread = threading.Thread(target=start_processing_thread, daemon=True)
		thread.start()
		threads.append(thread)
		misc.log_message(f"Spawned thread: {thread.name}")
	for thread in threads:
		if not thread.is_alive():
			misc.log_message(f"Removing dead thread: {thread.name}")
			threads.remove(thread)
			break
	time.sleep(1)
