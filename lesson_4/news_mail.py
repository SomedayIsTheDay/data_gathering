from pprint import pprint
import requests
import hashlib
from pymongo import MongoClient
from lxml import html

client = MongoClient("127.0.0.1", 27017)
db = client["news"]
news_mail_ru = db.news_mail_ru
# news_mail_ru.delete_many({})
url = "https://news.mail.ru/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36."
}
session = requests.Session()
response = session.get(url, headers=headers)
dom = html.fromstring(response.text)
photo_links = dom.xpath("//a[contains(@class, 'js-topnews__item')]/@href")
links = dom.xpath("//li[@class='list__item']/a/@href")
links.extend(photo_links)
for link in links:
    news_data = {}
    response = session.get(link, headers=headers)
    dom = html.fromstring(response.text)
    source = "".join(dom.xpath("//a[contains(@class,'breadcrumbs__link')]/span/text()"))
    datetime = (
        "".join(dom.xpath("//span[contains(@class,'js-ago')]/@datetime"))
        .replace("+03:00", "")
        .replace("T", " ")
    )
    header = "".join(dom.xpath("//h1[@class='hdr__inner']/text()"))
    # //time[@class='js-ago ']/@datetime
    if not header:
        datetime = (
            "".join(dom.xpath("//time[@class='js-ago ']/@datetime"))
            .replace("+03:00", "")
            .replace("T", " ")
        )
        header = "".join(dom.xpath("//h1[@itemprop='headline']/text()"))
        source = "many sources"

    news_data["_id"] = hashlib.md5(link.encode()).hexdigest()
    news_data["link"] = link
    news_data["source"] = source
    news_data["datetime"] = datetime
    news_data["header"] = header

    news_mail_ru.update_one({"_id": news_data["_id"]}, {"$set": news_data}, upsert=True)

for item in news_mail_ru.find({}):
    pprint(item)
