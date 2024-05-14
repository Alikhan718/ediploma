import json

import requests

base_api_url = 'https://api.ediploma.kz'
auth_url = f"{base_api_url}/auth/login"

users_url = "https://generator.ediploma.kz/get-file/jsons/3/users.json"

res = requests.get(users_url)
users = json.loads(res.content)
counter = 1
for user in users:
    loginRes = requests.post(url=auth_url, json={
        'email': user['email'],
        'password': user['password']
    })
    if 'Invalid' in loginRes.text:
        print(user['email'])
    counter += 1

# universal_2002@mail.ru
