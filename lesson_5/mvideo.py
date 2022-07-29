import time
from pprint import pprint
import hashlib
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from pymongo import MongoClient

client = MongoClient("127.0.0.1", 27017)
db = client["selenium"]
mvideo = db.mvideo
s = Service("./chromedriver.exe")

options = Options()
options.add_argument("start-maximized")
options.add_experimental_option(
    "prefs", {"profile.default_content_setting_values.notifications": 1}
)  # to remove "mvideo wants to show notifications" popup
driver = webdriver.Chrome(service=s, options=options)
actions = ActionChains(driver)
driver.get("https://www.mvideo.ru/")
y = 300

while True:
    driver.execute_script(f"window.scrollTo(0, {y})")
    y += 300
    time.sleep(0.5)
    try:
        trend = driver.find_element(By.XPATH, "//span[contains(text(), 'В тренде')]")
        if trend:
            trend.click()
            break
    except NoSuchElementException:
        pass

products = driver.find_element(
    By.XPATH, "//mvid-product-cards-group[@_ngcontent-serverapp-c276]"
)

labels = products.find_elements(By.CLASS_NAME, "product-mini-card__labels")
status = products.find_elements(By.CLASS_NAME, "product-mini-card__status")
names = products.find_elements(By.CLASS_NAME, "product-mini-card__name")
ratings = products.find_elements(By.CLASS_NAME, "product-mini-card__rating")
prices = products.find_elements(By.CLASS_NAME, "price__main-value")
credit = products.find_elements(By.CLASS_NAME, "product-mini-card__credit")
bonus = products.find_elements(By.CLASS_NAME, "product-mini-card__bonus-rubles")

for (l, s, n, r, p, c, b) in zip(labels, status, names, ratings, prices, credit, bonus):
    link = n.find_element(By.TAG_NAME, "a").get_attribute("href")
    prods_data = {
        "_id": hashlib.md5(link.encode()).hexdigest(),
        "label": l.text,
        "status": s.text,
        "name": n.text,
        "link": link,
        "rating": r.text.replace("\n", " - "),
        "price": p.text,
        "credit": c.text,
        "bonus": b.text,
    }
    mvideo.update_one({"_id": prods_data["_id"]}, {"$set": prods_data}, upsert=True)

driver.close()

for item in mvideo.find({}):
    pprint(item)
