import time
import xml.etree.cElementTree as ET

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


FILE = 'letu.xml'
XMLNS = 'http://www.sitemaps.org/schemas/sitemap/0.9'


tree = ET.parse(FILE)
root = tree.getroot()
links = []

for child in root.findall(f"{'{' + XMLNS + '}'}url/{'{' + XMLNS + '}'}loc"):
    links.append(child.text)

print(len(links))


options = webdriver.ChromeOptions()
options.headless = True
options.page_load_strategy = 'none'
chrome_path = ChromeDriverManager().install()
chrome_service = Service(chrome_path)
driver = Chrome(options=options, service=chrome_service)
driver.implicitly_wait(5)

links = ['https://www.letu.ru/product/dolce-gabbana-light-blue-italian-love-eau-de-toilette/116500016#productSpecs']

for link in links:
    driver.get(link)
    time.sleep(10)

    # print(driver, dir(driver))
    # with open('letu.png', 'w') as file:
    #     print(driver.get_screenshot_as_png(), file=file)

    # elem = driver.find_element_by_xpath("//*")
    # source_code = driver.get_attribute("outerHTML")
    # with open('letu.html', 'w') as file:
    #     file.write(source_code.encode('utf-8'))

    # Code
    with open('letu.html', 'w') as file:
        print(driver.page_source, file=file)

    # # Screenshot
    # s = lambda i: driver.execute_script(
    #     'return document.body.parentNode.scroll' + i
    # )
    # driver.set_window_size(s('Width'), s('Height'))
    # driver.get_screenshot_as_file('letu.png')

    # # content = driver.find_element(By.TAG_NAME, 'body')
    # content = driver.find_element(By.CSS_SELECTOR, "p[class='sticky-card__action-price--current']") # "span[itemprop='price'")
    # print(content.text)
    # print(content.value_of_css_property('class'))

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser') # lxml

    content = soup.find('p', {'class': 'sticky-card__action-price--current'})
    # print(content)
    print(content.text.strip())


    driver.quit()

    break
