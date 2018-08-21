import requests
import toml


rsp = requests.get('https://api.live.bilibili.com/rc/v1/Title/webTitles')
json_rsp = rsp.json()
data = json_rsp['data']
dict_title = {i['identification']: i['name'] for i in data}
    
with open('title.toml', 'w', encoding="utf-8") as f:
    toml.dump(dict_title, f)


