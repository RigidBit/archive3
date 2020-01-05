from dotenv import load_dotenv
import greenstalk
import json
import os
import sys
import time

import database as db
import misc

##### ENTRY POINT #####

load_dotenv()
queue = greenstalk.Client(host=os.getenv("GREENSTALK_HOST"), port=os.getenv("GREENSTALK_PORT"), use=os.getenv("GREENSTALK_TUBE_QUEUE"))

while True:
	connection = db.connect()
	for e in db.get_expired_active_url_records(connection, int(os.getenv("ARCHIVE3_URL_EXPIRATION")), int(os.getenv("ARCHIVE3_URL_ERROR_RETRIES"))):
		data = {"timestamp_queued": "NOW()"}
		db.update_url_record(connection, e["id"], data)
		connection.commit()
		payload = {"type": "screenshot", "id": e["id"], "url": e["url"]}
		queue.put(json.dumps(payload), ttr=int(os.getenv("ARCHIVE3_PROCESSING_TTR")))
		misc.log_message(f"""Queued Screenshot {e["id"]}: {e["url"]}""")
	for p in db.get_unprocessed_submission_records(connection):
		if db.get_ready_submission_record_count(connection)["count"] >= int(os.getenv("ARCHIVE3_PROCESSING_READY_LIMIT")):
			break
		if db.check_url_exists(connection, p["url"]):
			db.delete_submission_record(connection, p["id"])
			connection.commit()
			misc.log_message(f"""URL already exists: {p["url"]}""")
		else:
			data = {"processed": "true"}
			db.update_submission_record(connection, p["id"], data)
			connection.commit()
			payload = {"type": "preview", "id": p["id"], "url": p["url"]}
			queue.put(json.dumps(payload), ttr=int(os.getenv("ARCHIVE3_PROCESSING_TTR")))
			misc.log_message(f"""Queued Preview {p["id"]}: {p["url"]}""")
	connection.close()
	time.sleep(int(os.getenv("ARCHIVE3_QUEUE_PROCESSOR_SLEEP")))
