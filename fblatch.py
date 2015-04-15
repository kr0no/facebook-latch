import time, latch
from mechanize import Browser

# FACEBOOK SETTINGS
USER = 'YOUR_FB_EMAIL'
PASSWD = 'YOUR_FB_PASSWORD'

# LATCH SETTINGS
APP_ID = 'LATCH_APP_ID'
APP_SECRET = 'LATCH_APP_SECRET'
api = latch.Latch(APP_ID, APP_SECRET)

# Time beetwen auth checks in seconds
TIME = 3

sessions_detected = False

# The AccountID we receive when we pair the device is saved in 'asd'.
# We read it, and if it has no content, we request the pairing code
f = open('account_id', 'r+')
accountId = f.read()
if(accountId == ''):
	print "Type your pairing code"
	pair_code = raw_input("> ")
	response = api.pair(pair_code)
	responseData = response.get_data()
	accountId = responseData["accountId"]
	f.write(accountId)
f.close()

# Use of mechanize to enter in our fb account
br = Browser()
br.set_handle_robots(False)
br.open('https://m.facebook.com/login.php?next=https://m.facebook.com/settings/security/?active_sessions')
br._factory.is_html = True
br.select_form(nr=0)
br.form["email"] = USER
br.form["pass"] = PASSWD
br.submit()

# Infinite loop checking for unauthorized sessions
while True:
	time.sleep(TIME)
	br.open("https://m.facebook.com/settings/security/?active_sessions")
	br._factory.is_html = True
	br.select_form(nr=1)
	try:
		for i in range(0, len(br.find_control(type="checkbox").items)):
			br.find_control(type="checkbox").items[i].selected = True
			sessions_detected = True
	except:
		print '[+] No active sessions'
		sessions_detected = False
		
	if sessions_detected == True:
			print '[+] Active sessions detected. Checking Latch status...'
			status = api.status(accountId)
			statusData = status.get_data()
			try:
				if(statusData['operations'][APP_ID]['status'] == 'off'):
					print '[!] INTRUDER'
					br.submit()
				else:
					print '[+] Authorized'
			except:
				print 'Latch error (maybe an AccountId error, try to delete \'account_id\' content)'