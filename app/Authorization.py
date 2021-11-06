import sys
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep
from enum import Enum
import pickle


def NoVar(missing: str) -> None:
	print(f"No {missing} in enviroment variables.\nuse set variable=value\nFor Authorization needed inst_login and inst_password variables.")
	quit(-1)

class Instagram(Enum):
	PASSWORD = os.getenv("inst_password")
	LOGIN = os.getenv("inst_login")

if Instagram.PASSWORD.value is None:
	NoVar("paswword")

if Instagram.LOGIN.value is None:
	NoVar("login")

path = sys.argv[0]
if not  os.path.isdir(path):
	path = f"{path}\\.."

cookies_file_path = f"{path}\\..\\settings\\cookies"

options = webdriver.ChromeOptions()
options.add_argument("user-agent=Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0")
options.add_argument("--disable-blink-features=AutomationControlled")

browser = webdriver.Chrome(
	executable_path=f"{path}\\..\\..\\drivers\\Chrome\\chromedriver.exe",
	options=options
	)

try:
	browser.get(url=r"https://www.instagram.com")
	sleep(5)
	
	LoginInput = browser.find_element_by_name("username")
	LoginInput.clear()
	LoginInput.send_keys(Instagram.LOGIN.value)

	PasswordInput = browser.find_element_by_name("password")
	PasswordInput.clear()
	PasswordInput.send_keys(Instagram.PASSWORD.value)
	PasswordInput.send_keys(Keys.ENTER)

	input()

	cookies = browser.get_cookies()
	pickle.dump(cookies, open(cookies_file_path, "wb"))
	
except Exception as e:
	print(e)
finally:
	browser.close()
	browser.quit()
