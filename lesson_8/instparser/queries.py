# from pymongo import MongoClient
#
# client = MongoClient("localhost", 27017)
# db = client["instparser"]
# inst = db.instagram
# user_in_db = input("Enter the user that exists in the database: ")
#
# i = 1
# for user in inst.find(
#     {
#         "$and": [
#             {f"{user_in_db}.status": "following"},
#             {f"{user_in_db}.status": {"$ne": "follower"}},
#         ]
#     }
# ):
#     print(user[user_in_db]["username"], i)
#     i += 1
#     print(user[user_in_db]["username"], user[user_in_db]["status"])

# for user in inst.find({f"{user_in_db}.status": "following"}):
#     print(user[user_in_db]["link"], user[user_in_db]["status"])
