from app.functional import options_no_headless, start_session

try:
	browser = start_session(options_no_headless)
	input("Press enter to exit")
# except Exception as e:
# 	print(e)
finally:
	browser.close()
	browser.quit()
