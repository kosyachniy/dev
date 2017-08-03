import json
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

driver = webdriver.Chrome('./chromedriver')
driver.get("http://steamcommunity.com/market/")

elem=driver.find_element_by_class_name('global_action_link')
elem.click()

with open('db.txt', 'r') as file:
	s=json.loads(file.read())
	elem.send_keys(s['login'])
	elem.send_keys(Keys.TAB)
	elem.send_keys(s['password'])
	elem.send_keys(Keys.RETURN)

#

driver.close()