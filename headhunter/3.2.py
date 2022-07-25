from pymongo import MongoClient


def salary_more_than(num):
    for vacancy in vacancies_hh.find(
        {
            "$and": [
                {"$or": [{"salary_from": {"$gt": num}}, {"salary_to": {"$gt": num}}]},
                {"currency": "руб."},
            ]
        }
    ):
        print(vacancy)


wanted_salary = int(input("Enter the salary you want to see in the list of vacancies"))
client = MongoClient("127.0.0.1", 27017)
db = client["headhunter"]
vacancies_hh = db.vacancies
salary_more_than(wanted_salary)
