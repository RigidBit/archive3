import greenstalk

GREENSTALK_HOST="127.0.0.1"
GREENSTALK_PORT=11300
GREENSTALK_TUBE_QUEUE="archive3-queue"

queue = greenstalk.Client(host=GREENSTALK_HOST, port=GREENSTALK_PORT, watch=GREENSTALK_TUBE_QUEUE)

while True:
	job = queue.reserve()
	queue.delete(job)
	print(f"""Deleted queue job: {job.body}""")
