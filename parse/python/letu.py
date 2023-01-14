import re
import asyncio
import xml.etree.cElementTree as ET

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


FILE = 'letu.xml'
XMLNS = 'http://www.sitemaps.org/schemas/sitemap/0.9'
BATCH_SIZE = 5


options = webdriver.ChromeOptions()
options.headless = True
options.page_load_strategy = 'none'
chrome_path = ChromeDriverManager().install()
chrome_service = Service(chrome_path)
driver = Chrome(options=options, service=chrome_service)
driver.implicitly_wait(5)


def get_links():
    tree = ET.parse(FILE)
    root = tree.getroot()
    links = []

    for child in root.findall(f"{'{' + XMLNS + '}'}url/{'{' + XMLNS + '}'}loc"):
        links.append(child.text)

    return links

async def parse(link, delay=10, code=False, screenshot=False):
    driver.get(link)
    await asyncio.sleep(delay)

    # Code
    html = driver.page_source
    if code:
        with open('letu.html', 'w') as file:
            print(html, file=file)

    # Screenshot
    if screenshot:
        s = lambda i: driver.execute_script(
            'return document.body.parentNode.scroll' + i
        )
        driver.set_window_size(s('Width'), s('Height'))
        driver.get_screenshot_as_file('letu.png')

    soup = BeautifulSoup(html, 'html.parser') # lxml
    data = {}

    content = soup.find('p', {'class': 'sticky-card__action-price--current'})
    if content is not None:
        data['price'] = int(re.sub(r'[^0-9]', '', content.text.strip()))

    return data


async def main():
    # Get product links
    links = get_links()
    print(len(links))

    # Parse data
    # TODO: by batch
    for link in links:
        print('-' * 20)
        print(link)

        data = await parse(link, code=True)
        if data:
            print(data)
            break

    driver.quit()


if __name__ == '__main__':
    asyncio.run(main())
