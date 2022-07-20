import requests

access_token = input("Enter your access token: ")
url = f"https://api.vk.com/method/groups.get?&access_token={access_token}&v=5.131&extended=1"

response = requests.get(url)
j_data = response.json()
print(j_data)
