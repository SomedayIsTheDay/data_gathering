from pprint import pprint
import requests
from bs4 import BeautifulSoup
import re
from pymongo import MongoClient


def salary_func(string, replace_str):
    return int("".join(string.group().replace(replace_str, "").strip().split()))


client = MongoClient("127.0.0.1", 27017)
db = client["headhunter"]
vacancies_hh = db.vacancies
# vacancies_hh.delete_many({})
vacancy_text = input("Please enter the job title you want to find: ")
url = "https://ufa.hh.ru/search/vacancy"
params = {
    "text": vacancy_text,
    "salary": "",
    "clusters": "true",
    "ored_clusters": "true",
    "enable_snippets": "true",
    "page": 0,
}
headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; SM-A205U) AppleWebKit/537.36 (KHTML, like Gecko)"
    "Chrome/103.0.5060.71 Mobile Safari/537.36."
}
session = requests.Session()
response = session.get(url, headers=headers, params=params)
dom = BeautifulSoup(response.text, "html.parser")
last_page = int(
    dom.select_one("span[data-qa='pager-block-dots']").parent.text.replace("...", "")
)
pages_to_parse = int(
    input(f"How many pages do you want to parse? (not more than {last_page}): ")
)
if pages_to_parse > last_page:
    exit(1)
for i in range(0, pages_to_parse):
    params["page"] = i
    print(f"Scraping page No.{i+1}")
    response = session.get(url, headers=headers, params=params)
    dom = BeautifulSoup(response.text, "html.parser")
    vacancies = dom.select("div.vacancy-serp-item__layout")
    for vacancy in vacancies:
        vacancy_data = {}
        name = vacancy.select_one("a.bloko-link")
        href = name.get("href")
        name = name.text
        work_from_home = (
            "May work from home"
            if vacancy.select_one("div[data-qa='vacancy-serp__vacancy-work-schedule']")
            is not None
            else "Can't work from home"
        )

        salary = vacancy.select_one(
            "span[data-qa='vacancy-serp__vacancy-compensation']"
        )

        if salary is not None:
            vacancy_data["salary_to"] = None
            vacancy_data["salary_from"] = None
            currency = re.search(r"[a-zA-Zа-яёА-ЯЁ]{3,}.?", salary.text).group()
            vacancy_data["currency"] = currency
            salary_from = re.search(r"^(от)?\s?(?:\d+\s?)+", salary.text)
            salary_to = re.search(r"((до)|–)\s(?:\d+\s?)+", salary.text)
            if salary_from is not None and salary_to is not None:
                vacancy_data["salary_from"] = salary_func(salary_from, "")
                vacancy_data["salary_to"] = salary_func(salary_to, "–")

            elif salary_from is not None:
                vacancy_data["salary_from"] = salary_func(salary_from, "от")

            elif salary_to is not None:
                vacancy_data["salary_to"] = salary_func(salary_to, "до")

        company = vacancy.select_one("a[data-qa='vacancy-serp__vacancy-employer']").text
        city = vacancy.select_one("div[data-qa='vacancy-serp__vacancy-address']").text

        req_desc = vacancy.select_one(
            "div[data-qa='vacancy-serp__vacancy_snippet_requirement']"
        )
        res_desc = vacancy.select_one(
            "div[data-qa='vacancy-serp__vacancy_snippet_responsibility']"
        )
        if res_desc is None and req_desc is None:
            short_description = ""
        elif res_desc is not None and req_desc is not None:
            short_description = res_desc.text + " " + req_desc.text
        elif res_desc is None and req_desc is not None:
            short_description = req_desc.text
        else:
            short_description = res_desc.text
        vacancy_data["_id"] = hash(href)
        vacancy_data["name"] = name
        vacancy_data["href"] = href
        vacancy_data["work_from_home"] = work_from_home
        vacancy_data["company"] = company
        vacancy_data["city"] = city
        vacancy_data["short_description"] = short_description

        vacancies_hh.update_one(
            {"_id": vacancy_data["_id"]}, {"$set": vacancy_data}, upsert=True
        )

for item in vacancies_hh.find({}):
    pprint(item)
