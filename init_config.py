import json
from getpass import getpass

def main():
	user = input("Login: ")
	password = getpass("Password: ")
	with open("config.json", 'w') as creds_file:
		cred_json = json.dumps({"user": user,"pass": password,
"firebug_dir": "", "supportqueue_url": ""})
		creds_file.write(cred_json)



if __name__ == "__main__":
	main()
