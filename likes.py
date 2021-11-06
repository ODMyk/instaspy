from app.options import options, sleep
from app.functional import start_session, get_all_posts_links, set_like

account_name = input("Enter instagram profile name here: ")
browser = start_session(options)

links = get_all_posts_links(browser, account_name)
posts_count = len(links)
print("Starting likes")
for index, link in enumerate(links):
    browser.get(link)
    sleep(4)

    for _ in range(3):
        set_like(browser)

    print("Process: {:.2f} %".format((index + 1) / posts_count * 100))

print("Sucessfully liked all posts of the {account_name} [!]")

browser.close()
browser.quit()
print("Program finished with code 0")