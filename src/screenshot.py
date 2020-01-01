from selenium import webdriver
from PIL import Image
import json
import os
import requests
import tempfile
import time

DEFAULT_SETTINGS = {"maxWidth": 1366, "maxHeight": 1080*10, "minWidth": 1, "minHeight": 1, "width": 1920, "height": 1080, "full_page": False, "fullPageMaxLoops": 3, "delay": 3,  "maxDelay": 10}

def determine_screenshot_filename(request_id):
	return os.getenv("ARCHIVE3_SCREENSHOT_DIR") + "/" + str(request_id) + ".png"

def generate_screenshot(job_settings):
	settings = DEFAULT_SETTINGS.copy()
	settings.update(job_settings)
	url = settings["url"]
	screenshot_filename = os.path.join(tempfile._get_default_tempdir(), "archive3-" + next(tempfile._get_candidate_names()) + ".png")
	window_x = settings["width"]
	window_y = settings["height"]

	try:
		options = webdriver.ChromeOptions()
		options.add_argument("--ignore-certificate-errors")
		options.add_argument("--headless")
		options.add_argument("--incognito")
		options.add_argument("--hide-scrollbars")
		options.add_argument("user-agent="+os.getenv("ARCHIVE3_USER_AGENT"))
		options.binary_location = "/usr/bin/google-chrome"

		driver = webdriver.Chrome(chrome_options=options)
		driver.set_page_load_timeout(int(os.getenv("SELENIUM_TIMEOUT")))
		driver.set_window_position(0, 0)
		driver.set_window_size(window_x, window_y)
		driver.get(url)

		if settings["full_page"] == True:
			current_x = 0
			current_y = 0
			for _x in range(0, settings["fullPageMaxLoops"]):
				required_width = driver.execute_script("return Math.max(document.body.scrollWidth, document.body.offsetWidth, document.documentElement.clientWidth, document.documentElement.scrollWidth, document.documentElement.offsetWidth)")
				required_height = driver.execute_script("return Math.max(document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight)")
				window_x = min(required_width, settings["maxWidth"])
				window_y = min(required_height, settings["maxHeight"])
				if current_x == window_x and current_y == window_y:
					break
				else:
					current_x = window_x
					current_y = window_y
					driver.set_window_size(window_x, window_y)

		if settings["delay"] > 0:
			time.sleep(settings["delay"])
		elif settings["full_page"] == True:
			time.sleep(1)

		driver.save_screenshot(screenshot_filename)
	except Exception as e:
		raise e
	finally:
		driver.quit()

	return screenshot_filename

def generate_thumbnail(screenshot_input, screenshot_output):
	image = Image.open(screenshot_input)
	# Remove alpha channel so it can be saved to jpeg.
	if image.mode in ('RGBA', 'LA'):
		background = Image.new(image.mode[:-1], image.size, "#ffffff")
		background.paste(image, (0, 0))
		image = background
	image = image.resize((320, 180), resample=Image.BILINEAR)
	image.save(screenshot_output, quality=90, optimize=True, progressive=False)
