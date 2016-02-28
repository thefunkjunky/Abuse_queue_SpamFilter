# This is a designed to identify spam tickets in our spam/abuse queue 
# at the datacenter I work at.  The difficulty in using traditional
# spam filtering methods is that they will always select legitimate abuse tickets,
# because they always contain the full, original spam text in the body. 
# The task is further complicated by the fact that I am not given access to the support api, so I
# used Selenium to automate the actual browser (not ideal, but it works).
#
# This script only works (well, worked) on the particular abuse queue at my work, 
# I leave it here as a reference for my methods for future Selenium projects.
# It no longer functions at work, as management found out about it and promptly changed the api
# and ticketing web interface to break the script.  

# When it was working, it consistently selected NO false positives, and missed NO false negatives.
# It saved approximately 2 hours of work that was typically assigned to system admins, who are too
# valuable to be wasting time on such a simple and tedius task.




from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import json
import time
import re

def main():
	# Load config params
	# NOTE: fbug_dir and abusequeue_url must be entered manually into
	# config.json after its creation using init_config.py.
	# fbug_dir is the direcory of FireBug plugin directory location
	# abusequeue_url is the url of my ticketing system URL
	# TODO: make fbug optional
	with open("config.json", "r") as config:
		config_json = json.load(config)
		login = config_json["user"]
		password = config_json["user"]
		fbug_dir = config_json["fbug_dir"]
		abusequeue_url = config_json["abusequeue_url"]

	# Stuff to load firefox with the firebug extension in my profile.  Location 
	# must be updated to your local firebug location.
	# TODO: make this optional
	firefoxProfile = webdriver.FirefoxProfile()
	firebuglocation = fbug_dir
	# firefoxProfile.add_extension(extension=firebuglocation)
	# Disable javascript to run faster
	firefoxProfile.set_preference("browser.download.folderList", 2)
	firefoxProfile.set_preference("javascript.enabled", False)
	# set up browser webdriver
	browser = webdriver.Firefox(firefoxProfile)
	browser.get(abusequeue_url)
	# Fill out login form from JSON data.
	with open("abuse_creds.json", "r") as cred_files:
		creds = json.loads(cred_files.read())
		login, password = [i for i in creds]
	loginElem = browser.find_element_by_id("login")
	loginElem.send_keys(login)
	passElem = browser.find_element_by_id("pass")
	passElem.send_keys(password)
	passElem.submit()

	# Give iframe time to load, then switch to "content" iframe
	time.sleep(3)
	browser.switch_to_frame(browser.find_element_by_id('content'))

	# Generate a list of elements, starting from the XPath specified,
	# and containing the word "ticket" in the id.
	# The Xpath for the first ticket (2nd row of the list) is:
	# /html/body/form/div/table[2]/tbody/tr[2] (example)

	# Generate list of all ticket rows as a list of elements, using path above,
	# selecting for rows whose Xpath id contains the word "ticket" in it
	tableRows = browser.find_elements_by_xpath(
		"//body/form/div/table[2]/tbody/*[contains(@id, 'ticket')]")

	# Insert filter here to remove list elements that aren't spam (whitelisted).
	# Use a simple whitelist first, then do individual ticket analysis on blacklisted items (faster)

	# REGEX to select for only alphanumeric characters and remove everything else.  Prevents trip ups
	# by spam tickets with crazy characters in the subject line designed to break stuff like this.
	# UNICODE compliant
	pattern = re.compile(r'[\W_]+', re.UNICODE)

	# iterate through each row element
	for index, elem in enumerate(tableRows):
		print("INDEX: {}".format(index))
		# Get Subject text (relative to row path)
		subjectElem = elem.find_element_by_xpath(".//td[3]/a")
		subjectText = subjectElem.text
		# Apply REGEX to subjectText
		subTextREGEX = pattern.sub('', subjectText).lower()
		print("subjectTextRegex: {}".format(subTextREGEX))
		# the whitelist. ignore every row element whose subject 
		# has any of these words in it
		whitelist = [
		"spam",
		"dmca",
		"infringement",
		"spamcop",
		"copyright",
		"abuse",
		"fraudulent",
		"takedown",
		"phishing",
		"attack",
		"hack",
		"cease",
		"desist",
		"irregular",
		"trademark"]
		# Whitelist application using any(list comprehension)
		if any(s in subTextREGEX for s in whitelist):
			print("Row {} ignored for whitelist match".format(index))
		elif not any(s in subTextREGEX for s in whitelist):
			# Not whitelisted, now checks to see if there is an IP address
			# in the body text.  Thinking here is that practically every abuse ticket
			# will have an IP address in the body of its text, but few (in my experience,
			# zero) spam tickets will ever include an IP address in the messege. Why would
			# they?  The whitelist method usually sorts everything pretty well actually,
			# but adding this filter seals the deal.
			#
			# NOTE: in the interest of saving a shit ton of time and headache, I've enlisted
			# the help of katebot and the mouseover preview window instead
			# of manually opening and checking each link for an IP RegEx.  Katebot already
			# does this, and updates the ticket with a notice.  It is this notice that the script
			# looks for.  
			# NOTE: this is where automation gets sloppy.  The preview window 
			# won't show up right away on mouseover, and attempts to read it will
			# crash the script.  Would have been a better idea to use try...except
			# here.  Anyway, I mitigate this by setting a delay timer.  This is
			# adjusted directly in the script, but I had plans to use a while 
			# loop that wouldn't break until the preview was opened and found.

			# Gets a list of elements by <td> in row element.  Needed for checkbox
			# (checkbox doesn't have an id)
			rowElems = elem.find_elements_by_xpath(".//td")
			# finds the row element with class name 'activity'
			rowActionElem = elem.find_element_by_class_name('activity')
			# Get list of all the table elements in the current row element
			# Get the checkbox element. Found relative to the row's 1st table element
			selectorBox = rowElems[0].find_element_by_xpath(".//*[contains(@id, 'selected')]")
			# perform mouseover (hover) action on the action element to enable the preview element
			hov = ActionChains(browser).move_to_element(rowActionElem)
			hov.perform()
			# Give it a moment to pull up preview data
			time.sleep(0.1)
			# Get preview element relative to action element
			actionPreview = rowActionElem.find_element_by_xpath(
			".//*[contains(@id, 'preview')]")
			# Move it back to the selectorbox to get rid of preview box
			hov = ActionChains(browser).move_to_element(selectorBox)
			hov.perform()
			# Check for katebot's "No IP found" in preview.
			# if found, check selectorbox
			if "No IP found".lower() in actionPreview.text.lower():
				print(
				"No IP in row {} message text. Selecting as spam".format(index))
				selectorBox.click()
		else:
			print("Skipping, for some inexplicable reason...")


if __name__ == "__main__":
	main()