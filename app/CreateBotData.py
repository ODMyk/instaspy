import os
import sys

path = sys.argv[0]
if not os.path.isdir(path):
    path = f"{path}\\.."

TOKEN = os.getenv("telegram_bot_token")
USER_ID = os.getenv("telegram_user_id")

def NoVar(missing: str) -> None:
	print(f"No {missing} in enviroment variables.\nuse set variable=value\nFor Authorization needed telegram_bot_token and telegram_user_id variables.")
	quit(-1)

if TOKEN is None:
    NoVar("Token")

if USER_ID is None:
    NoVar("User ID")

string = f'''
TOKEN = "{TOKEN}"
USER_ID = "{USER_ID}"
'''

with open("BotData.py", "w+") as f:
    f.write(string)