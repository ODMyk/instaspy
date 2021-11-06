import os
import io
import sys
import json
import pickle
import telebot
import requests

from .BotData import *
from time import sleep
from typing import Union
from loguru import logger
from selenium import webdriver
from fake_useragent import UserAgent
from requests.cookies import RequestsCookieJar
# from selenium.webdriver.common.keys import Keys


ua = UserAgent()
bot = telebot.TeleBot(TOKEN)

path = sys.argv[0]
if not  os.path.isdir(path):
	path = f"{path}\\.."

logger.add(f"{path}\\LOGS.log", format="[{level}] | {time} | {message}", level="DEBUG", rotation="5 MB", compression="zip")

cookies_file_path = f"{path}\\settings\\cookies"
cookies = pickle.load(open(cookies_file_path, "rb"))
CookieJar = RequestsCookieJar()

logger.info("Loading cookies for requests.py [...]")
for cookie in cookies:
	if 'expiry' in cookie:
		cookie['expires'] = cookie["expiry"]
		del cookie["expiry"]
	if 'httpOnly' in cookie:
		cookie['rest'] = {"httpOnly": cookie["httpOnly"]}
		del cookie["httpOnly"]
	CookieJar.set(**cookie)
logger.info("Cookies for requests.py were loaded [.]")

driver_path = f"{path}\\app\\chromedriver.exe"
accounts_to_check = json.load(open(f"{path}\\settings\\accounts.json", "r"))

options = webdriver.ChromeOptions()
options.add_argument(f"user-agent={ua.random}")
options.add_argument("--disable-blink-features=AutomationControlled")
options.headless = True

options_no_headless = webdriver.ChromeOptions()
options_no_headless.add_argument(f"user-agent={ua.random}")
options_no_headless.add_argument("--disable-blink-features=AutomationControlled")

headers = {
	"User-Agent": ua.random
}
params = dict(
    origin='Chicago,IL',
    destination='Los+Angeles,CA',
    waypoints='Joplin,MO|Oklahoma+City,OK',
    sensor='false',
	__a="1"
)

account_checking_interval = 60
