from dotenv import load_dotenv
import greenstalk
import json
import os
import sys
import time

import database as db
import emails as e
import misc

##### ENTRY POINT #####

load_dotenv()
queue = greenstalk.Client(host=os.getenv("GREENSTALK_HOST"), port=os.getenv("GREENSTALK_PORT"), use=os.getenv("GREENSTALK_TUBE_QUEUE"))

while True:
	connection = db.connect()
	expired = db.get_expired_active_url_records(connection, int(os.getenv("ARCHIVE3_URL_EXPIRATION")), int(os.getenv("ARCHIVE3_URL_ERROR_RETRIES")))
	for e in expired:
		data = {"timestamp_queued": "NOW()"}
		db.update_url_record(connection, e["id"], data)
		connection.commit()
		payload = {"id": e["id"], "url": e["url"]}
		queue.put(json.dumps(payload), ttr=int(os.getenv("ARCHIVE3_PROCESSING_TTR")))
		misc.log_message(f"""Queued {e["id"]}: {e["url"]}""")
	connection.close()
	time.sleep(int(os.getenv("ARCHIVE3_QUEUE_PROCESSOR_SLEEP")))