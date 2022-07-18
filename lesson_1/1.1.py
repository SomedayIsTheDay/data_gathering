import requests
import json

url = "https://api.github.com/users/DEeidara/repos"

response = requests.get(url)
j_data = response.json()

repos = []
for i in j_data:
    repos.append(i["name"])
with open("repos.json", "w", encoding="utf-8") as f:
    json.dump(repos, f)
