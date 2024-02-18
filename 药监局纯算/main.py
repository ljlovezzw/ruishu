import time
import requests
from lxml import etree
from loguru import logger
import execjs
import re
from rsvmp纯算 import RsVmp
# from basic_Toolkit.Get_Ip import Ip

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
    'Host': 'www.nmpa.gov.cn',
    'Referer': 'https://cn.bing.com/',
}

localStorage = {
    '$_YVTX': "Wu9C",
    '$_YWTU': "WdfoeGszN3PzN5X3qO4gd3uBbm4emzLNrUjRnA8S6z3",
}

rs = RsVmp()

url2 = 'https://www.nmpa.gov.cn'
url = 'https://www.nmpa.gov.cn/datasearch/home-index.html'

# ip_ = Ip().get_ip(1)[0]
# ip = ip_['ip']
# port = ip_['port']
#
# proxy = {
#     'https': f'http://{ip}:{port}',
#     'http': f'http://{ip}:{port}'
# }

# print(proxy)

# reps = requests.get(url, headers=headers, proxies=proxy)
reps = requests.get(url, headers=headers)

wO = reps.cookies.get('NfBCSins2OywO')
tc = reps.cookies.get('acw_tc')
reps.encoding = 'utf=8'
reps = reps.text
print(reps)

html = etree.HTML(reps)

js_ts = html.xpath('//script/text()')[0]

js_url = url2 + html.xpath('//script/@src')[0]

# reps = requests.get(js_url, headers=headers, proxies=proxy).text
reps = requests.get(js_url, headers=headers).text

vm_code = re.findall(r'_\$\w*\$?\w?=_\$\w*\$?\w?\.call.*?\);', reps)[0]

name = re.findall(r',(.*)\);', vm_code)[0]

reps = reps.replace(vm_code, f'window.vm_code={name}')

js_code = f"""
window=global;
document={{}};
{js_ts}
{reps}
function sdk(){{
    return [$_ts, vm_code]
}}
"""

com = execjs.compile(js_code)
sdk = com.call("sdk")
ts = sdk[0]

rs.evstr = js_code = sdk[1]
rs.cd = ts['cd']

aebi = ts['aebi']
rs.ident_arr = ts['cp'][1]

logger.success(f'变量名: {rs.ident_arr}')

# 匹配方法名
name = re.findall('return (.*?)\.apply', js_code)[0]
logger.success(f'方法名: {name}')

# 匹配方法
func = re.search('function ' + name.replace('$', '\$') + '[\s\S]*;}}}}}}', js_code).group()

rs.func_toStr = func
logger.success(f'匹配到的方法: {func}')

# 匹配操作符
aa = re.findall(',_\$\w*\$?\w?=(_\$\w*\$?\w?)\[1];', func)[0]
logger.success(aa)

js_code = f"""
window = global;
{aa} = {aebi};
{func}
function refunc(){{
    var name = ''
    try {{
        {name}(506)
    }} catch (e) {{
        pattern = /_\$\w*\$?\w*/g
        a = e.toString()
        name = pattern.exec(a)[0];
        window[name] = [];
        {name}(506);
        window[name] = window[name].map((v) => v.toString())
        return window[name]
    }}
}}
"""

com = execjs.compile(js_code)
func_list = com.call("refunc")
rs.func_list = func_list
logger.success(func_list)
end = time.time()

rs.arr37()
logger.success('aaaa')
wP = rs.run()
logger.success(time.time() - end)

logger.success(f'生成的cookie: {wP}')
logger.success(f'生成的cookie长度: {len(wP)}')

cookie = {
    'NfBCSins2OywP': wP,
    'NfBCSins2OywO': wO,
    'acw_tc': tc,
}
# url = 'https://www.nmpa.gov.cn/datasearch/home-index.html#category=yp'
url = 'https://www.gov.cn/yaowen/liebiao/202401/content_6924871.htm'
# reps = requests.get(url, headers=headers, cookies=cookie, proxies=proxy)
reps = requests.get(url, headers=headers, cookies=cookie)
logger.success(reps.status_code)
reps.encoding = 'utf-8'

logger.success(reps.text)
"""
arr1 耗时 0.019s
num_4arr1 耗时 0.005s
num_4arr2 耗时 0.004s
arr_to_str 基本不耗时
to_num1 耗时 0.147s
to_num2 耗时 1.147s
num_2arr 耗时 0.001s
arr4 耗时 0.587s
P 耗时 0.382s
arr_wei1 耗时 0.188
arr_wei2 耗时 0.195
arr_wei3 耗时 0.201
arr_wei4 耗时 0.202
arr_wei5 耗时 0.190
arr_wei6 耗时 0.190
"""
