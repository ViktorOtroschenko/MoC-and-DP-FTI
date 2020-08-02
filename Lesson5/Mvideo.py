from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from pprint import pprint
from pymongo import MongoClient
import json


chrome_options = Options()
chrome_options.add_argument('start-maximized')
driver = webdriver.Chrome(options=chrome_options)
driver.get('https://www.mvideo.ru')

hits_sellers = driver.find_element_by_xpath(
    "//div[contains(text(),'Хиты продаж')]/../../../div[@class='gallery-layout sel-hits-block ']"
)

while True:
    try:
        button = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
            (By.XPATH, '//div[@data-init="ajax-category-carousel"][2]//a[@class="next-btn sel-hits-button-next"]')))
        button.click()
    except Exception:
        break

names = []
items = hits_sellers.find_elements_by_css_selector('li.gallery-list-item')

for item in items:
    item = json.loads(item.find_element_by_css_selector('a.sel-product-tile-title').get_attribute('data-product-info'))
    names.append(item)

pprint(names)

client = MongoClient('127.0.0.1', 27017)
db = client['mvideo_db']
mvideo = db['mvideo']
mvideo.insert_many(names)

# driver.close()
