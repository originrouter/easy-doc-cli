import requests
import json

url = "https://api.easytransnote.com/article/v1/doc/list"
headers = { "x-api-key": "sk-v1-W3tO-37o6mK6+UjNpyuilwS+2og-Ik2Y+lA" }

response = requests.post(url, headers=headers, json={})

ans = response.json()["data"]["articles"]

print(ans.__len__())

for i in ans:
    print("group id: ", i["group_id"])
    print("group name: ", i["name"])

for i in ans[2]["articles"]:
    print("article id: ", i["outer_id"])
    print("article name: ", i["name"])
    print("create time: ", i["time_create"])
    for j in i["children"]:
        print("     child article id: ", j["outer_id"])
        print("     child article name: ", j["name"])
        print("     create time: ", j["time_create"])

with open("response.json", "w", encoding="utf-8") as f:
    json.dump(response.json()["data"]["articles"], f, indent=2, ensure_ascii=False)
