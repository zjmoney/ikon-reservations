from msedge.selenium_tools import Edge, EdgeOptions
from datetime import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import calendar
import time

# Date to look for reservations on
date_str = "2021-1-31"
date = datetime.strptime(date_str, "%Y-%m-%d")

# Length of time to wait between retries
retry_wait_in_sec = 60

# Maximum retries. Set to 0 or less for infinite
max_attempts = 0

# Email and Password of account
email = ""
password = ""

# Resort to reserve at as listed on the Ikon pass website
resort = "Crystal Mountain Resort"

print("Starting web driver...")

options = EdgeOptions()
options.use_chromium = True
options.add_argument("headless")
options.add_argument("--log-level=3")

driver = Edge(options=options)
driver.get("https://account.ikonpass.com/en/login?redirect_uri=/en/myaccount/add-reservations/")

def remove_overlay():
	#get rid of cc overlay
	buttons = driver.find_elements_by_css_selector("a.cc-btn")
	while any(map(lambda x: x.size["height"] != 0, buttons)):
		for button in buttons:
			try:
				button.click()
			except:
				pass
		buttons = driver.find_elements_by_css_selector("a.cc-btn")

remove_overlay()

#login
email_box = driver.find_element_by_css_selector("input#email")
email_box.send_keys(email)
password_box = driver.find_element_by_css_selector("input#sign-in-password")
password_box.send_keys(password)
submit = driver.find_element_by_css_selector("button.submit")
submit.click()

WebDriverWait(driver,10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input.react-autosuggest__input')))   
remove_overlay()

print("Logged In")

#select resort
search = driver.find_element_by_css_selector("input.react-autosuggest__input")
search.send_keys(resort)
button = driver.find_element_by_css_selector("li#react-autowhatever-resort-picker-section-1-item-0")     
button.click()
button = driver.find_element_by_xpath("//span[contains(text(), 'Continue')]")
button.click()

print("Selected " + resort)

WebDriverWait(driver,10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.DayPicker-wrapper')))
remove_overlay()

print("Looking for reservations on " + date_str)

#select date
datepicker = driver.find_element_by_css_selector("div.DayPicker-wrapper") 
month_selected = False
while not month_selected:
	month_text = calendar.month_name[date.month]
	month = datepicker.find_elements_by_xpath("//span[contains(text(), " + "'" + month_text + "')]")
	if len(month) > 0:
		month_selected = True
	else:
		button = datepicker.find_element_by_class_name("icon-chevron-right")
		button.click()

day = datepicker.find_element_by_xpath("//div[@aria-label='" + date.strftime("%a %b %d %Y") + "']")
day.click()
day_classes = day.get_attribute(name="class")
available = "past" not in day_classes and "unavailable" not in day_classes
booked = "confirmed" in day_classes
div = driver.find_elements_by_xpath("//div[contains(text(), 'Reservation Limit Reached')]")
reservations_left = len(div) == 0

tries = 0

while max_attempts <= 0 or tries < max_attempts:
	if available and not booked and reservations_left:
		remove_overlay()
		button = driver.find_element_by_xpath("//span[contains(text(), 'Save')]")
		button.click()
		button = driver.find_element_by_xpath("//span[contains(text(), 'Continue To Confirm')]")
		button.click()

		WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, "//input[@type='checkbox']")))   
		button = driver.find_element_by_xpath("//input[@type='checkbox']")
		button.click()
		WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Confirm Reservations')]")))   
		button = driver.find_element_by_xpath("//span[contains(text(), 'Confirm Reservations')]")
		button.click()
		with open("flag.txt", "w") as f:
			f.write("Booked")

		print("Booked successfully!")
		break

	time.sleep(retry_wait_in_sec)
	tries = tries+1
	if (tries % 5 == 0):
		print("Attempted " + str(tries) + " times...")

with open("log.txt", "a") as f:
	f.write(datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
	f.write(": Available - %r, Booked - %r, Reservations Left- %r" % (available, booked, reservations_left))
	f.write("\n")
driver.close()
