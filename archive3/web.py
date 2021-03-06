from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template, send_file, send_from_directory, Response, redirect
from uuid import uuid4
import datetime
import greenstalk
import json
import mimetypes
import os
import requests

from decorators import admin_required
import misc
import database as db
import screenshot as ss
import validation as v

##### ENTRY POINT #####

load_dotenv()
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY")

if __name__ == "__main__":
	app.run(host="0.0.0.0")

##### STATIC ROUTES #####

@app.route("/contact", methods=["GET"])
def contact():
	return render_template("contact.html", page_title=misc.page_title("contact"))

@app.route("/ping", methods=["GET"])
def ping():
	with db.connect() as connection:
		db.check_url_exists(connection, "")
		return "Pong!"

@app.route("/faq", methods=["GET"])
def api_help():
	data = {}
	return render_template("faq.html", page_title=misc.page_title("faq"), data=data)

@app.route("/terms-of-service", methods=["GET"])
def terms_of_service():
	return render_template("terms_of_service.html", page_title=misc.page_title("tos"))

@app.route("/privacy-policy", methods=["GET"])
def privacy_policy():
	return render_template("privacy_policy.html", page_title=misc.page_title("pp"))

##### DYNAMIC API ROUTES #####

@app.route("/buried", methods=["GET", "POST"])
@admin_required
def buried():
	with greenstalk.Client(host=os.getenv("GREENSTALK_HOST"), port=os.getenv("GREENSTALK_PORT"), use=os.getenv("GREENSTALK_TUBE_QUEUE")) as queue:
		form = v.BuriedForm()
		if form.validate_on_submit():
			try:
				print(form.data)
				if form.data["action"] == "delete" and form.data["job_id"] is not None:
					queue.delete(form.data["job_id"])
				elif form.data["action"] == "kick" and form.data["job_id"] is not None:
					queue.kick_job(form.data["job_id"])
			except greenstalk.NotFoundError:
				return redirect("/buried", code=302)
		try:
			job = queue.peek_buried()
			data = {"job_body": job.body, "job_id": job.id}
		except greenstalk.NotFoundError:
			data = {}
		return render_template("buried.html", page_title=misc.page_title("buried"), data=data)

@app.route("/manage", methods=["GET", "POST"])
@admin_required
def manage():
	with db.connect() as connection:
		data = {}
		form = v.ManageForm()
		if form.validate_on_submit():
			accepted = json.loads(form.data["accepted"])
			for item in accepted:
				record = db.get_submission_record(connection, item)
				if record is not None and not db.check_url_exists(connection, record["url"]):
					data = {"url": record["url"]}
					db.create_url_record(connection, data)
					misc.log_message(f"""Created url record: {record["url"]}""")
				db.delete_submission_record(connection, item)
				misc.log_message(f"""Deleted submission record: {item}""")
				file_path_screenshot = os.path.join(os.getcwd(), os.getenv("ARCHIVE3_SCREENSHOT_DIR"), "preview-" + str(item) + ".jpg")
				if os.path.exists(file_path_screenshot):
					os.remove(file_path_screenshot)
				misc.log_message(f"""Deleted local preview screenshot: {file_path_screenshot}""")
			rejected = json.loads(form.data["rejected"])
			for item in rejected:
				db.delete_submission_record(connection, item)
				misc.log_message(f"""Deleted submission record: {item}""")
				file_path_screenshot = os.path.join(os.getcwd(), os.getenv("ARCHIVE3_SCREENSHOT_DIR"), "preview-" + str(item) + ".jpg")
				if os.path.exists(file_path_screenshot):
					os.remove(file_path_screenshot)
				misc.log_message(f"""Deleted local preview screenshot: {file_path_screenshot}""")
			connection.commit()
		data["pending"] = db.get_pending_submission_records(connection, 100)
		return render_template("manage.html", page_title=misc.page_title("manage"), data=data)

@app.route("/recent", methods=["GET"])
def recent():
	with db.connect() as connection:
		limit = int(request.values["limit"]) if "limit" in request.values else int(os.getenv("ARCHIVE3_RECENT_LIMIT"))
		data = {}
		data["cdn_base_url"] = os.getenv("AWS_S3_CDN_BASE_URL")
		data["recent"] = db.get_recent_active_data_records(connection, limit)
		return render_template("recent.html", page_title=misc.page_title("recent"), data=data)

@app.route("/search", methods=["GET"])
def search():
	with db.connect() as connection:
		form = v.SearchForm(request.values)
		if form.validate():
			data = {}
			data["cdn_base_url"] = os.getenv("AWS_S3_CDN_BASE_URL")
			data["search_results"] = db.search_active_url_records(connection, request.values["q"], int(os.getenv("ARCHIVE3_SEARCH_RESULT_LIMIT")))
			data["search_term"] = request.values["q"]
		else:
			data = {}
		return render_template("search.html", page_title=misc.page_title("search"), data=data)

@app.route("/submit", methods=["GET", "POST"])
def submit():
	with db.connect() as connection:
		data = {}
		form = v.SubmitForm()
		if form.validate_on_submit():
			url = misc.normalize_url(form.data["url"])
			if not db.check_url_exists(connection, url) and not db.check_active_submission_exists(connection, url):
				data = {"url": url, "ip": request.remote_addr, "processed": "false"}
				db.create_submission_record(connection, data)
				connection.commit()
			data["message"] = "Your URL submission has been received. Thank you."
		else:
			for key in form.errors:
				data["message"] = f"""Error: {key} - {form.errors[key][0]}"""
		return render_template("submit.html", page_title=misc.page_title("submit"), data=data)

# @app.route("/image/<hash>", methods=["GET"])
# def web_image(hash):
# 	file_path = misc.hash_to_path(hash)
# 	filename = hash + ".png"
# 	print(file_path, filename, os.getcwd())
# 	as_attachment = "download" in request.values and request.values["download"] == "true"
# 	return send_from_directory(file_path, filename, mimetype=mimetypes.guess_type(filename)[0], as_attachment=as_attachment)

@app.route("/preview", methods=["GET"])
def preview():
	form = v.PreviewForm(request.values)
	if form.validate():
		filename = os.path.join(os.getcwd(), os.getenv("ARCHIVE3_SCREENSHOT_DIR"), "preview-" + str(form.data["id"]) + ".jpg")
		if os.path.exists(filename):
			return send_file(filename)
		else:
			filename = ss.generate_screenshot({"url": form.data["url"], "width": 1280, "height": 720, "delay": 1})
			return send_file(filename)
	return render_template("error.html", page_title=misc.page_title("500"), data={"header": "500", "error": f"""Unable to generate preview."""}), 500

@app.route("/proof/<data_id>", methods=["GET"])
def proof(data_id):
	with db.connect() as connection:
		data_record = db.get_active_data_record(connection, data_id)
		if data_record != None:
			proof_available = True if int((datetime.datetime.now() - data_record["timestamp"]).total_seconds()) > int(os.getenv("RIGIDBIT_PROOF_DELAY")) else False
			if proof_available:
				headers = {"api_key": os.getenv("RIGIDBIT_API_KEY")}
				url = os.getenv("RIGIDBIT_BASE_URL") + "/api/trace-block/" + str(data_record["block_id"])
				content = requests.get(url, headers=headers).content
				return Response(content, mimetype="application/json", headers={"Content-disposition": f"attachment; filename={str(data_record['timestamp']).replace(' ', '_')}.json"})
		return render_template("error.html", page_title=misc.page_title("404"), data={"header": "404", "error": f"""Proof not found or not yet available."""}), 404

@app.route("/stats", methods=["GET"])
@admin_required
def stats():
	with db.connect() as connection:
		data = \
		{
			"data_count": db.get_data_record_count(connection)["count"],
			"url_count": db.get_url_record_count(connection)["count"],
			"pending_submission_count": db.get_pending_submission_record_count(connection)["count"],
			"ready_submission_count": db.get_ready_submission_record_count(connection)["count"],
		}
		return render_template("stats.html", page_title=misc.page_title("stats"), data=data)

@app.route("/urls", methods=["GET"])
def urls():
	with db.connect() as connection:
		data = {"urls": db.get_url_list(connection)}
		return render_template("urls.html", page_title=misc.page_title("urls"), data=data)

@app.route("/view", methods=["GET"])
def view():
	with db.connect() as connection:
		form = v.ViewForm(request.values)
		if form.validate() and db.check_active_url_exists(connection, form.data["url"]):
			data = {}
			data["url_record"] = db.get_url_record_by_url(connection, form.data["url"])
			data["data_records"] = db.get_active_data_records_for_url_id(connection, data["url_record"]["id"], int(os.getenv("ARCHIVE3_VIEW_LIMIT")))
			data["data_records"] = list(map(misc.data_record_add_proof_status, data["data_records"]))
			data["data_records_json"] = json.dumps(list(map(lambda x: dict(x), data["data_records"])), cls=misc.DatetimeEncoder)
			data["cdn_base_url"] = os.getenv("AWS_S3_CDN_BASE_URL")
			return render_template("view.html", page_title=misc.page_title("view"), data=data)
		return render_template("error.html", page_title=misc.page_title("404"), data={"header": "404", "error": f"""Unable to load URL."""}), 404

@app.route("/", methods=["GET"])
def root():
	return render_template("index.html", page_title=misc.page_title("default"))
