import os, sys, json

def start_msg():
    print("Current accounts:")
    for account in accounts:
        print(f"\t{account}")

    print("\nTry 'help' if you are new here\n")

def save(accounts: list):
    with open(f"{dir_root}\\settings\\accounts.json", "w", encoding="utf-8") as file:
        json.dump(accounts, file)
    os.system('cls')
    start_msg()    

dir_root = sys.argv[0]
if not os.path.isdir(dir_root):
    dir_root = "\\".join((dir_root, '..'))

with open(f"{dir_root}\\settings\\accounts.json", "r", encoding="utf-8") as file:
    accounts = json.load(file)

start_msg()
while True:
    command = input(">")
    action, *name = command.split(" ")

    if name:
        name = name[0]
    if action == "help":
        print("""help - show this message
add [name] - add account to check
del [name] - remove account to check
exit - finish the program""")
    elif action == "add":
        if not name in accounts and name:
            accounts.append(name)
            save(accounts)
    elif action == "del":
        if name in accounts:
            accounts.pop(accounts.index(name))
            save(accounts)
    elif action == "exit":
        quit()
    else:
        print("Incorrect input")