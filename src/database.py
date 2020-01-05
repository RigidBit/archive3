from psycopg2 import sql
import os
import psycopg2
import psycopg2.extras
import time

def connect():
	return psycopg2.connect(dbname=os.getenv("POSTGRESQL_DB"), host=os.getenv("POSTGRESQL_HOST"), port=os.getenv("POSTGRESQL_PORT"), user=os.getenv("POSTGRESQL_USER"), password=os.getenv("POSTGRESQL_PASS"))

def check_active_url_exists(connection, url):
	cursor = connection.cursor()
	cursor.execute("SELECT COUNT(*) FROM urls WHERE url=%s AND removed=false", (url,))
	return cursor.fetchone()[0] >= 1

def check_url_exists(connection, url):
	cursor = connection.cursor()
	cursor.execute("SELECT COUNT(*) FROM urls WHERE url=%s", (url,))
	return cursor.fetchone()[0] >= 1

def check_active_submission_exists(connection, url):
	cursor = connection.cursor()
	cursor.execute("SELECT COUNT(*) FROM submissions WHERE url=%s AND processed=false", (url,))
	return cursor.fetchone()[0] >= 1

# def check_submission_exists(connection, url):
# 	cursor = connection.cursor()
# 	cursor.execute("SELECT COUNT(*) FROM submissions WHERE url=%s", (url,))
# 	return cursor.fetchone()[0] >= 1

def create_data_record(connection, data):
	keys = list(data.keys())
	values = list(map(str, data.values()))
	query = sql.SQL("INSERT INTO data ({}) VALUES ({}) RETURNING id;").format(sql.SQL(", ").join(map(sql.Identifier, keys)), sql.SQL(", ").join(map(sql.Literal, values)))
	cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)	
	cursor.execute(query)
	return cursor.fetchone()[0]

def create_submission_record(connection, data):
	keys = list(data.keys())
	values = list(map(str, data.values()))
	query = sql.SQL("INSERT INTO submissions ({}) VALUES ({}) RETURNING id;").format(sql.SQL(", ").join(map(sql.Identifier, keys)), sql.SQL(", ").join(map(sql.Literal, values)))
	cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
	cursor.execute(query)
	return cursor.fetchone()[0]

def create_url_record(connection, data):
	keys = list(data.keys())
	values = list(map(str, data.values()))
	query = sql.SQL("INSERT INTO urls ({}) VALUES ({}) RETURNING id;").format(sql.SQL(", ").join(map(sql.Identifier, keys)), sql.SQL(", ").join(map(sql.Literal, values)))
	cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
	cursor.execute(query)
	return cursor.fetchone()[0]

# def create_url_error_record(connection, data):
# 	keys = list(data.keys())
# 	values = list(map(str, data.values()))
# 	query = sql.SQL("INSERT INTO url_errors ({}) VALUES ({}) RETURNING id;").format(sql.SQL(", ").join(map(sql.Identifier, keys)), sql.SQL(", ").join(map(sql.Literal, values)))
# 	cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
# 	cursor.execute(query)
# 	return cursor.fetchone()[0]

def delete_submission_record(connection, id):
	cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
	cursor.execute("DELETE FROM submissions WHERE id=%s RETURNING *;", (id,))
	record = cursor.fetchone()
	return dict(record) if record is not None else None

# def get_data_record(connection, id):
# 	cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
# 	cursor.execute("SELECT * FROM data WHERE id=%s", (id,))
# 	record = cursor.fetchone()
# 	return dict(record) if record is not None else None

def get_active_data_record(connection, id):
	cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
	cursor.execute("SELECT * FROM data WHERE id=%s and removed=false", (id,))
	record = cursor.fetchone()
	return dict(record) if record is not None else None

def get_active_data_records_for_url_id(connection, url_id, limit):
	cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
	cursor.execute("SELECT * FROM data WHERE url_id=%s AND removed=false ORDER BY id DESC LIMIT %s", (url_id, limit))
	return cursor.fetchall()

def get_active_url_record(connection, id):
	cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
	cursor.execute("SELECT * FROM urls WHERE id=%s and removed=false", (id,))
	record = cursor.fetchone()
	return dict(record) if record is not None else None

def get_data_record_count(connection):
	cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
	cursor.execute("SELECT COUNT(*) as count FROM data;")
	record = cursor.fetchone()
	return dict(record) if record is not None else None

def get_url_record_count(connection):
	cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
	cursor.execute("SELECT COUNT(*) as count FROM urls;")
	record = cursor.fetchone()
	return dict(record) if record is not None else None

def get_submission_record_count(connection):
	cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
	cursor.execute("SELECT COUNT(*) as count FROM submissions;")
	record = cursor.fetchone()
	return dict(record) if record is not None else None

def get_pending_submission_record_count(connection):
	cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
	cursor.execute("SELECT COUNT(*) as count FROM submissions WHERE processed=true AND ready=false;")
	record = cursor.fetchone()
	return dict(record) if record is not None else None

def get_ready_submission_record_count(connection):
	cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
	cursor.execute("SELECT COUNT(*) as count FROM submissions WHERE processed=true AND ready=true;")
	record = cursor.fetchone()
	return dict(record) if record is not None else None

def get_url_record(connection, id):
	cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
	cursor.execute("SELECT * FROM urls WHERE id=%s", (id,))
	record = cursor.fetchone()
	return dict(record) if record is not None else None

def get_url_record_by_url(connection, url):
	cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
	cursor.execute("SELECT * FROM urls WHERE url=%s", (url,))
	record = cursor.fetchone()
	return dict(record) if record is not None else None

def get_expired_active_url_records(connection, delay, error_limit):
	cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
	cursor.execute("SELECT id, url FROM urls WHERE removed=false AND (timestamp_queued < NOW() - INTERVAL '%s seconds' OR timestamp_queued IS NULL) AND errors < %s ORDER BY RANDOM()", (delay, error_limit))
	return cursor.fetchall()

def get_pending_submission_record(connection):
	cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
	cursor.execute("SELECT * FROM submissions WHERE processed=true AND ready=true ORDER BY RANDOM() LIMIT 1")
	record = cursor.fetchone()
	return dict(record) if record is not None else None

def get_unprocessed_submission_records(connection):
	cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
	cursor.execute("SELECT * FROM submissions WHERE processed=false")
	return cursor.fetchall()

def get_recent_active_data_records(connection, limit):
	cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
	cursor.execute("SELECT data.hash, urls.url, data.timestamp FROM data LEFT JOIN urls ON data.url_id=urls.id WHERE data.removed=false AND urls.removed=false ORDER BY data.id DESC LIMIT %s", (limit,))
	return cursor.fetchall()

def get_submission_record(connection, id):
	cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
	cursor.execute("SELECT * FROM submissions WHERE id=%s", (id,))
	record = cursor.fetchone()
	return dict(record) if record is not None else None

def get_url_list(connection):
	cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
	cursor.execute("SELECT url FROM urls;")
	return cursor.fetchall()

def search_active_url_records(connection, search, count):
	query = sql.SQL("SELECT urls.url, urls.timestamp_updated, (SELECT hash FROM data WHERE url_id=urls.id ORDER BY id DESC LIMIT 1) as hash FROM urls where url LIKE {} AND removed=false AND EXISTS(SELECT hash FROM data WHERE url_id=urls.id ORDER BY id DESC LIMIT 1) LIMIT "+str(count)+";").format(sql.Literal("%"+search+"%"))
	cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
	cursor.execute(query)
	return cursor.fetchall()

def update_data_record(connection, id, data):
	query = sql.SQL("UPDATE data SET {} WHERE id={};").format(sql.SQL(", ").join(map(lambda kv: sql.SQL("{}={}").format(sql.Identifier(kv[0]), sql.Literal(kv[1])), data.items())), sql.Literal(id))
	cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)	
	cursor.execute(query)
	return id

def update_submission_record(connection, id, data):
	query = sql.SQL("UPDATE submissions SET {} WHERE id={};").format(sql.SQL(", ").join(map(lambda kv: sql.SQL("{}={}").format(sql.Identifier(kv[0]), sql.Literal(kv[1])), data.items())), sql.Literal(id))
	cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)	
	cursor.execute(query)
	return id

def update_url_record(connection, id, data):
	query = sql.SQL("UPDATE urls SET {} WHERE id={};").format(sql.SQL(", ").join(map(lambda kv: sql.SQL("{}={}").format(sql.Identifier(kv[0]), sql.Literal(kv[1])), data.items())), sql.Literal(id))
	cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)	
	cursor.execute(query)
	return id
