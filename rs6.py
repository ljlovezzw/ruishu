import random
import re
import execjs
import requests
import time

session = requests.session()

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Pragma': 'no-cache',
    'Host':'www.urbtix.hk',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
    'sec-ch-ua': '"Microsoft Edge";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

a = time.perf_counter()
def get_ts_object(ts):
    lis = []
    for i in ts.values():
        if type(i) == list:
            if len(i) > 300:
                lis = i
                break

    ts_ob = {
        '151':ts[ lis[151]],
        '188':ts[lis[188]],
        '50':ts[lis[50]],
        '200':ts[lis[200]],
        '133':ts[lis[133]],
        '194':ts[lis[194]],
        '152':ts[lis[152]],
        '136':ts[lis[136]]
    }

    ts_map = {"11": 102, "23": 103, "87": 127, "94": 126, "105": 208, "126": 181, "128": 108, "140": 240, "143": 103,
              "155": 100,
              "156": 11, "159": 203, "167": 101, "169": 102, "170": 181, "175": 180, "179": 225, "183": 0, "204": 224,
              "206": 203}

    ts_ob['105'] = ts_map[str(lis.index(ts[lis[198]]))]
    ts_ob['101'] = ts_map[str(lis.index(ts[lis[101]]))]
    ts_ob['96'] = ts_map[str(lis.index(ts[lis[96]]))]
    ts_ob['207'] = ts_map[str(lis.index(ts[lis[207]]))]

    return ts_ob

proxies = {
    "http": "http://127.0.0.1:7890",
    "https": "http://127.0.0.1:7890",
}
session.headers = headers
# session.proxies = proxies
response = session.get('http://www.urbtix.hk/')
print(time.perf_counter() - a)
# print(response)
js_code = re.findall('type="text/javascript" r=\'m\'>(.*?)</script>', response.text)[0]
# print(js_code)
ts_code = session.get('http://www.urbtix.hk/b3c79ec/f890b6f5917/6da34174.js').text

print(time.perf_counter() - a)
fp = open('rs6.js', encoding='utf8').read()
js = execjs.compile(fp)

ts = js.call('get_ts', js_code,ts_code)[0]
# print(ts)
ts_ob = get_ts_object(ts)
# print(ts_ob)
ck,houzhui,serverTime = execjs.compile(open('rs6.js', encoding='utf8').read()).call('rs6', ts_ob,"/api/internet/bookmark/count/v2")
# ck = js.call('rs6', ts_ob) #,"/api/internet/bookmark/count/v2")
print(time.perf_counter() - a)

# print(ck)
# print(houzhui)
# print(len(ck))
# print(len(houzhui))
session.cookies.set('Cc2838679FT', ck, domain="www.urbtix.hk")

response = session.get('http://www.urbtix.hk/')
print(time.perf_counter() - a)

response.encoding = 'utf8'
print(response)
js_200 = session.get('https://www.urbtix.hk/b3c79ec/f890b6f5917/rsab.js').text
ts_code = session.get('https://www.urbtix.hk/b3c79ec/f890b6f5917/6da34174.js', headers=headers).text

ts = js.call('get_ts', js_200,ts_code)[0]
ts_ob = get_ts_object(ts)
ck,houzhui,serverTime = execjs.compile(open('rs6.js', encoding='utf8').read()).call('rs6', ts_ob,"/api/internet/event/homePage/list")
print(ck)
print(len(ck))
print(houzhui)
# session.cookies.set('X-Client-ID', '976f013dfc27c08019332cefca351834', domain="www.urbtix.hk")
session.cookies.set('serverTime', str(serverTime), domain="www.urbtix.hk")
session.cookies.set('Cc2838679FT', ck, domain="www.urbtix.hk")
#
# headers['Content-Type'] = "application/json"
# headers['X-Client-ID'] = "976f013dfc27c08019332cefca351735"
# headers['X-Client-ID-Enc'] = "ewezMZFBw6aOZOdwGVWch4Ic+PJRlwu7Ky8GoiKjFey7/vn5PrrUEntXHuSGmfSc"
# headers['X-Client-Type'] = '1'
# headers['X-Sales-Channel'] = '1'
# headers['sw8'] = "1-OGZlNjg0ODktZDc5Mi1mOWYyLWQxMTQtNTQxNTliY2Q4NDg1LjEuMTcwMTI2MDEwNTgwMTAwMDA=-MA==-0-MA==-MA==-MA==-MA=="
# headers['X-Locale'] = "zh_CN"
#
res = session.post('https://www.urbtix.hk/api/internet/event/homePage/list?' + houzhui,json={'tab':'todaysEvents','pageNo':1,'pageSize':10},headers=headers)
print(res.text)
# print(session.cookies)
if response.status_code == 202:
    print('出错！')
print(response)

# print(response.text)
#     return ck
    # print(ts)


# get200()

print(time.perf_counter() - a)