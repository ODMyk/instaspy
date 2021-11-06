from time import sleep
from app.functional import on_new_post_detected, on_new_story_detected, start_session, options, sleep

browser = None
while True:
    link_to_download = input("Enter an instagram URL here:\n")

    if not link_to_download:
        break

    post, story = False, False

    if "instagram.com/p/" in link_to_download:
        post = True
    elif "instagram.com/stories/" in link_to_download:
        story = True
    else:
        print("Invalid URL")

    if story:
        if not browser:
            browser = start_session(options)
        on_new_story_detected(link_to_download, None, browser)
        browser.get(r"https://www.instagram.com")
        sleep(1)
    elif post:
        on_new_post_detected(link_to_download)

if browser:
    browser.close()
    browser.quit()
