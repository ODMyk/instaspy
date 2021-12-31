from .options import *
path = f"{path}\\data"

@logger.catch
def load_cookies(browser: webdriver.Chrome):
	logger.info("Loading cookies for selenium [...]")
	try:
		for cookie in cookies:
			browser.add_cookie(cookie)
	except FileNotFoundError:
		print("run Authorization.py (settings dir) first")
		quit(-1)
	logger.info("Cookies for selenium were loaded [.]")

@logger.catch
def start_session(options: webdriver.ChromeOptions) -> webdriver.Chrome:
	logger.info("Starting new session [...]")
	
	browser = webdriver.Chrome(
	executable_path = driver_path,
	options = options
	)

	browser.get(r"https://www.instagram.com")
	sleep(2)
	load_cookies(browser)
	browser.refresh()
	logger.info("Session was started successfully [.]")
	
	return browser

@logger.catch
def get_last_post_link(browser: webdriver.Chrome, account: str):
	last_post_on_page = browser.find_element_by_class_name('v1Nh3.kIKUG._bz0w')
	link_to_last_post = last_post_on_page.find_element_by_xpath(".//a").get_attribute("href")

	return link_to_last_post

@logger.catch
def get_last_3_posts_links(browser: webdriver.Chrome, account: str) -> list:
	links = []
	last_posts_on_page = browser.find_elements_by_class_name('v1Nh3.kIKUG._bz0w')[:3]
	for post in last_posts_on_page:
		link = post.find_element_by_xpath(".//a").get_attribute("href")
		links.append(link)
	
	return links

@logger.catch
def save_posts_links(links: list, account: str) -> None:
	json.dump(links, open(f"{path}\\{account}_last_posts.json", "w+"))

@logger.catch
def get_checked_posts(browser: webdriver.Chrome, account: str) -> list:
	try:
		last_posts_links = json.load(open(f"{path}\\{account}_last_posts.json", "r"))
	except FileNotFoundError:
		last_posts_links = get_last_3_posts_links(browser, account)
		save_posts_links(last_posts_links, account)
	
	return last_posts_links

@logger.catch
def check_for_new_post(browser: webdriver.Chrome, account: str) -> Union[str, None]:

	checked_posts_links = get_checked_posts(browser, account)
	last_post_link = get_last_post_link(browser, account)
	
	if not last_post_link in checked_posts_links:
		return last_post_link
	else:
		return None

@logger.catch
def get_multi_post(json_data: dict) -> tuple:
	images = []
	videos = []
	
	for edge in json_data['carousel_media']:
		is_video = "video_versions" in edge.keys()
		if not is_video:
			images.append(get_best(edge['image_versions2']['candidates'])['url'])
		else:
			videos.append(get_best(edge['video_versions'])["url"])
	
	return (images, videos)

def get_best(data):
	Max = None
	for el in data:
		if not Max:
			Max = el
		else:
			if Max['width'] < el['width']:
				Max = el
	
	return Max

@logger.catch
def get_single_post(json_data: dict) -> tuple:
	images = []
	videos = []

	is_video = "video_versions" in json_data.keys()
	if not is_video:
		images.append(get_best(json_data['image_versions2']['candidates'])['url'])
	else:
		videos.append(get_best(json_data['video_versions'])['url'])
	
	return (images, videos)

@logger.catch
def get_post_json(link: str) -> dict:
	response = requests.get(url=link, headers=headers, params=params, cookies=CookieJar)
	post_json = response.json()['items'][0]

	return post_json

@logger.catch
def get_post(link: str) -> list:	
	post_json = get_post_json(link)
	is_single = 'carousel_media_count' not in post_json.keys()
	if is_single:
		images, videos = get_single_post(post_json)
	else:
		images, videos = get_multi_post(post_json)
	
	post = {
		"is_single": is_single,
		"images": images,
		"videos": videos
	}
	
	return post

@logger.catch
def add_new_checked_post_link(browser: webdriver.Chrome, account: str, link: str) -> None:
	links = get_checked_posts(browser, account)
	links.insert(0, link)
	try:
		del links[3]
	except IndexError:
		pass
	save_posts_links(links, account)

@logger.catch
def get_post_images(images_links: list) -> list:
	images = []
	for link in images_links:
		response = requests.get(link, headers=headers)
		img = io.BytesIO(bytes(response.content))
		images.append(img)
	
	return images


@logger.catch
def get_post_videos(videos_links: list) -> list:
	videos = []
	for link in videos_links:
		response = requests.get(link, headers=headers)
		video = io.BytesIO(bytes(response.content))
		videos.append(video)
	
	return videos

@logger.catch
def get_post_media(post: dict) -> dict:
	media = {}

	media["is_single"] = post["is_single"]
	media["images"] = get_post_images(post["images"])
	media["videos"] = get_post_videos(post["videos"])

	return media

@logger.catch
def on_new_post_detected(link: str, account: str=None, browser: webdriver.Chrome=None) -> None:
	checker_mode = account and browser
	if checker_mode:
		logger.info(f"New post of {account} was detected.")
	post = get_post(link)
	if post:
		post_media = get_post_media(post)
		if checker_mode:
			logger.info(f"Successfully downloaded post of {account}.")
		notify_about_new_post(account, post_media, not checker_mode)
		if checker_mode:
			add_new_checked_post_link(browser, account, link)
			logger.info(f"Notification about new post of {account} was sent.")

@logger.catch
def check_account_for_post(browser: webdriver.Chrome, account: str) -> None:
	new_post_link = check_for_new_post(browser, account)
	if new_post_link:
		on_new_post_detected(new_post_link, account, browser)
		

@logger.catch
def check_story_button_for_active(button: webdriver.remote.webelement.WebElement) -> bool:
        attr = button.get_attribute("height")
        return  attr == "168"

@logger.catch
def pause_story(browser: webdriver.Chrome) -> None:
	pause_button = browser.find_element_by_class_name("wpO6b")
	aria_label = pause_button.find_element_by_class_name("_8-yf5").get_attribute("aria-label")

	if aria_label == "Приостановить":
		pause_button.click()

@logger.catch
def get_story_link(browser: webdriver.Chrome, account: str) -> Union[None, str]:
	sleep(1)
	pause_story(browser)
	current_story_link = browser.current_url
	
	return current_story_link

@logger.catch
def check_for_new_story(browser: webdriver.Chrome, account: str) -> Union[str, None]:
	story_button = browser.find_element_by_class_name("XjzKX")
	aria_disabled = story_button.find_element_by_xpath("./div").get_attribute("aria-disabled")
	story_exists = aria_disabled == "false"
	if story_exists:
		is_new = check_story_button_for_active(story_button.find_element_by_xpath(".//div/canvas"))

		if is_new:
			story_button.click()
			sleep(2)
			story_link = get_story_link(browser, account)

			return story_link

	return None

@logger.catch
def get_story_video(div: webdriver.remote.webelement.WebElement) -> Union[dict, None]:
	try:
		video = div.find_element_by_xpath(".//video")
		link = video.find_element_by_xpath(".//source").get_attribute("src")
		video_bytes = io.BytesIO(bytes(requests.get(headers=headers, url=link).content))
	except:
		video_bytes = None
	finally:
		return video_bytes

@logger.catch
def get_story_image(div: webdriver.remote.webelement.WebElement) -> bytes:
	image_html = div.find_element_by_xpath(".//img")
	link = image_html.get_attribute("src")
	image_bytes = io.BytesIO(bytes(requests.get(headers=headers, url=link).content))

	return image_bytes

@logger.catch
def next_story(browser: webdriver.Chrome):
	button = browser.find_element_by_class_name("FhutL")
	button.click()

@logger.catch
def go_to_highlight(browser: webdriver.Chrome, username: str, title: str, to_skip: int) -> None:
	browser.get(r"https://www.instagram.com/{}".format(username))
	sleep(1)
	highlights = browser.find_elements_by_class_name("Ckrof")

	for highlight in highlights:
		div = highlight.find_element_by_class_name("eXle2")
		if str(div.text) == str(title):
			highlight.click()
			sleep(5)
			break
	
	for _ in range(to_skip):
		next_story(browser)
		sleep(0.1)

	pause_story(browser)

@logger.catch
def highlight_mode_set(browser: webdriver.Chrome, link: str):
	count = len(browser.find_elements_by_class_name("_7zQEa"))
	to_skip = int(input(f"Number of highlight( [1; {count}] ): ")) - 1
	response = requests.get(f"{link}?__a=1", headers=headers, params=params).json()
	username = response['user']['username']
	title = response['highlight']['title']
	go_to_highlight(browser, username, title, to_skip)

@logger.catch
def get_story(browser: webdriver.Chrome, link: str, extra_click: bool=False) -> dict:
	
	browser.get(link)
	sleep(2)

	if extra_click:
		browser.find_element_by_class_name("sqdOP.L3NKy.y1rQx.cB_4K").click()
	
	pause_story(browser)

	if "highlight" in link.lower():
		highlight_mode_set()

	story = {
		"type": None,
		"bytes": None
	}

	div_with_data = browser.find_element_by_class_name("qbCDp")
	video = get_story_video(div_with_data)
	if video:
		story["type"] = "video"
		story["file"] = video
	else:
		story["type"] = "image"
		story["file"] = get_story_image(div_with_data)
	
	return story

@logger.catch
def notify_about_new_post(account: str, post: dict, download: bool=False) -> None:
	if not download:
		caption = f"{account}'s new post!"
	else:
		caption = "Downloaded post"
	if post["is_single"]:
		if post["images"]:
			bot.send_photo(USER_ID, photo=post["images"][0], caption=caption)
		else:
			bot.send_video(USER_ID, data=post["videos"][0], caption=caption)
	else:
		bot.send_message(USER_ID, caption)
		for video in post["videos"]:
			bot.send_video(USER_ID, data=video)
		for photo in post["images"]:
			bot.send_photo(USER_ID, photo=photo)

@logger.catch
def notify_about_new_story(account: str, story: dict, download: bool=False) -> None:
	file = story["file"]
	if not download:
		caption = f"{account}'s new story!"
	else:
		caption = "Downloaded story"
	if story["type"] == "video":
		bot.send_video(USER_ID, data=file, caption=caption)
	elif story["type"] == "image":
		bot.send_photo(USER_ID, photo=file, caption=caption)

@logger.catch
def on_new_story_detected(link, account, browser):
	if account:
		logger.info(f"New story of {account} was detected.")
	story = get_story(browser, link, extra_click=True)
	if account:
		logger.info(f"Successfully downloaded story of {account}.")
	notify_about_new_story(account, story, download=not account)
	if account:
		logger.info(f"Notification about new story of {account} was sent.")


@logger.catch
def check_account_for_story(browser: webdriver.Chrome, account: str) -> None:
	new_story_link = check_for_new_story(browser, account)
	if new_story_link:
		on_new_story_detected(new_story_link, account, browser)
		
@logger.catch
def check_account(browser: webdriver.Chrome, account: str) -> None:
	browser.get(r"https://www.instagram.com/{}".format(account))
	sleep(5)
	check_account_for_post(browser, account)
	check_account_for_story(browser, account)

@logger.catch
def go_to_end_of_page(browser: webdriver.Chrome) -> None:
	browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

@logger.catch
def get_all_posts_links(browser: webdriver.Chrome, account: str) -> tuple:
	browser.get(f"https://www.instagram.com/{account}")
	sleep(4)
	posts_count = int(browser.find_element_by_class_name("v9tJq.AAaSh.VfzDr").find_element_by_xpath(".//ul/li/span/span").text)

	loaded_posts = 0
	links = []
	threads = []
	print("Loading posts...")
	while loaded_posts != posts_count:
		go_to_end_of_page(browser)
		sleep(2)
		current_posts = browser.find_elements_by_class_name("v1Nh3.kIKUG._bz0w")
		
		for post in current_posts:
			link = post.find_element_by_xpath(".//a").get_attribute("href")
			if link not in links:
				links.append(link)

		loaded_posts = len(links)
		print("{:.2f} %".format(loaded_posts / posts_count * 100))
	print("Loading completed.")

	return tuple(links)

@logger.catch
def set_like(browser: webdriver.Chrome) -> None:
	button = browser.find_element_by_class_name("fr66n").find_element_by_xpath(".//button")
	svg = button.find_element_by_class_name("_8-yf5")

	if not "не" in svg.get_attribute("aria-label").lower():
		button.click()
