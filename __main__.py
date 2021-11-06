from app.functional import *


try:
	browser = start_session(options)
	while True:
		for account in accounts_to_check:
			logger.info(f"Checking account {account} [...]")
			check_account(browser, account)
			logger.info(f"Finished checking of {account} [.]")
		logger.info("Pausing [...]")
		sleep(60)
		logger.info("Finished pause [.]")
# except Exception as e:
# 	print(e)
finally:
	browser.close()
	browser.quit()
