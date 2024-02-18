
url = 'http://www.fangdi.com.cn/new_house/new_house.html'

import re
import time
import json
import struct
import base64
import subprocess
import requests_html
from Crypto.Hash import SHA1
from Crypto.Cipher import AES
from Crypto.Util import Padding
from Crypto.Random import get_random_bytes
from urllib import parse


class RS4Cookie(object):

    def __init__(self, base_url):
        self.url_parse = parse.urlparse(base_url)
        self.eval_js = ''
        self.content_table = None
        self.ts_json = None
        self.arr_128 = b''
        self.arr_16 = []
        self.message = []
        self.start_time = int(time.time() * 1000)
        self.local_storage = {}

    def set_ts_json(self, ts_json):
        self.ts_json = ts_json
        self.eval_js = ts_json[-1]
        return self

    def set_content(self, content):
        self.content_table = get_content_table(content, self.ts_json[2:5])
        return self

    def set_arr_16(self, arr_16):
        self.arr_16 = arr_16
        return self

    def set_cookie(self, requests):
        name_table = decrypt_bytes(b64decode(self.content_table(10))).split(';')
        cookie_key = name_table[13] + self.content_table(14) + 'T'
        requests.cookies.set(cookie_key, self.dump(requests), domain=self.url_parse.hostname, path='/')

    def set_raw_cookie(self, requests):
        name_table = decrypt_bytes(b64decode(self.content_table(10))).split(';')
        cookie_key = name_table[13] + self.content_table(14) + 'T'
        requests.cookies.set(cookie_key, decrypt_bytes(b64decode(self.content_table(5))), domain=self.url_parse.hostname, path='/')

    def generate(self, index_value):
        self.arr_128 = b''
        self.message = []
        value_3 = 0
        self.message.append(254)
        self.message.append(3)
        self.message.append(index_value)
        self.message.append(None)
        self.message.append(struct.pack(">ii", 25166848, 2))
        self.message.append(14)
        self.message.append(1)

        ts_value_table = dict()
        number_list = [103, 0, 102, 203, 224, 181, 108, 240, 101, 126, 103, 11, 102, 203, 225, 181, 208, 180, 100, 127]
        for index, each in enumerate(re.findall("((_\$[\w\W]{2}\._\$[\w\W]{2}=_\$[\w\W]{2};){20})?var _\$[\w\W]{2}=64;", self.eval_js)[0][0][:-1].split(";")):
            ts_value_table[each[5:9]] = number_list[index]
        self.message.append(b64decode(self.ts_json[19]) + bytes(map(lambda n: ts_value_table[n], [self.ts_json[21], self.ts_json[23], self.ts_json[25], self.ts_json[27]])))

        self.message.append(98)
        self.message.append([0, 0])
        value_3 |= 32

        self.message.append(0)
        value_3 |= 64

        if index_value == 13:
            self.message.append(struct.pack(">h", 1))
            value_3 |= 128

        # 8字节的解密结果
        encrypt_data = self.local_storage.get('$_YWTU')
        if not encrypt_data:
            encrypt_data = b64decode(self.content_table(26))
            self.local_storage['$_YWTU'] = encrypt_data
        self.message.append(aes_decrypt(encrypt_data, bytes([each ^ self.ts_json[3] for each in b64decode(self.content_table(19) + self.ts_json[15])])))
        self.message.append(0)
        value_3 |= 512

        if index_value == 13:
            self.message.append(self.message[-3])  # 耗时
            value_3 |= 32768

            try:
                version = int(self.content_table(28))
            except:
                version = 0
            if 0 < version < 8:
                self.message.append(version)
                value_3 |= 65536

        self.message.append(239)
        self.message[3] = struct.pack(">i", value_3)
        for each in self.message:
            if isinstance(each, bytes):
                self.arr_128 += each
            elif isinstance(each, int):
                self.arr_128 += bytes([each])
            elif isinstance(each, list):
                self.arr_128 += bytes(each)
            else:
                raise Exception('')
        return self

    def dump(self, requests):
        name_table = decrypt_bytes(b64decode(self.content_table(10))).split(';')
        cookie_key = name_table[13] + self.content_table(14) + 'T'
        key_17 = [each ^ self.ts_json[3] for each in b64decode(self.content_table(21) + self.ts_json[17])]
        arr_4 = rs4_function_709(requests.cookies.get(cookie_key), key_17)
        time_server = int(decrypt_bytes(b64decode(self.content_table(25))))
        time_2 = int(time.time() * 1000)
        time_3 = time_server + time_2 - self.start_time
        time_data = struct.pack(">qii", time_3, time_server // 1000, self.start_time // 1000)
        sign_data = time_data + b64decode(self.content_table(22) + self.ts_json[16])[:4] + self.arr_128
        header = arr_4[1]
        xor_value = rs4_get_xor_value(header + sign_data, self.eval_js)
        header = [each ^ xor_value for each in header]

        aes_key = rs4_function_685(key_17, self.ts_json, self.content_table, self.arr_16)
        cookie = '4' + b64encode(bytes(header) + bytes([xor_value]) + aes_encrypt(sign_data, aes_key))
        return cookie


def get_content_table(content, ts_number):
    table = 'qrcklmDoExthWJiHAp1sVYKU3RFMQw8IGfPO92bvLNj.7zXBaSnu0TC6gy_4Ze5d{}|~ !#$%()*+,-;=?@[]^'
    table_mapping = [-1 for _ in range(256)]
    for i in range(len(table)):
        value = ord(table[i])
        table_mapping[value] = i
    i = 0

    def hc():
        nonlocal i
        res_value = table_mapping[ord(content[i])]
        i += 1
        if res_value < 0:
            a1 = table_mapping[ord(content[i])] * 7396
            i += 1
            a2 = table_mapping[ord(content[i])] * 86
            i += 1
            a3 = table_mapping[ord(content[i])]
            i += 1
            return a1 + a2 + a3
        elif res_value < 64:
            return res_value
        else:
            a1 = table_mapping[ord(content[i])]
            i += 1
            return res_value * 86 + a1 - 5440

    hc()
    decrypt_table = []
    while i < len(content):
        _dz = hc()
        decrypt_table.append(content[i: i + _dz])
        i += _dz

    def salt_mapping(salt):
        inti_table = [0, 1, 3, 7, 15, 31]
        return salt >> ts_number[2] | (salt & inti_table[ts_number[2]]) << 6 - ts_number[2]

    def get_content_value(value_index):
        salt = value_index % 64
        table_index = value_index - salt
        salt = salt_mapping(salt)
        salt ^= ts_number[0]
        table_index += salt
        return decrypt_table[table_index]

    return get_content_value


def decrypt_bytes(data):
    key = struct.unpack(">h", data[:2])[0]
    data = bytearray(data)
    data_len = len(data)
    for i in range(2, data_len, 2):
        data[i] ^= key >> 8
        if i + 1 < data_len:
            data[i + 1] ^= key & 255
        key += 1
    return bytes(data[2:]).decode()


def b64decode(data):
    str_trans = str.maketrans("qrcklmDoExthWJiHAp1sVYKU3RFMQw8IGfPO92bvLNj.7zXBaSnu0TC6gy_4Ze5d", "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/")
    data = data.translate(str_trans)
    while len(data) % 4 != 0:
        data += '='
    return base64.b64decode(data.encode())


def b64encode(data):
    str_trans = str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/", "qrcklmDoExthWJiHAp1sVYKU3RFMQw8IGfPO92bvLNj.7zXBaSnu0TC6gy_4Ze5d")
    return base64.b64encode(data).decode().translate(str_trans).replace('=', '')


def rs4_function_709(cookie, key):
    index_number = 64
    ver = cookie[0]
    out_data = bytearray(b64decode(cookie[1:]))
    xor_value = out_data[index_number + 1]
    for i in range(index_number + 1):
        out_data[i] ^= xor_value
    left_text = out_data[:65]
    right_text = out_data[66:]
    assert ver and len(left_text) == index_number + 1 and key[31] == left_text[index_number]
    return [ver, left_text, xor_value, right_text]


def rs4_function_685(data, ts_json, content_table, arr_16):
    sign_1 = SHA1.new(bytes(data + arr_16)).digest()[:16]
    sign_2 = SHA1.new(bytes([each ^ ts_json[3] for each in b64decode(content_table(19) + ts_json[15])])).digest()[:16]
    sign_data = []
    for i in range(16):
        sign_data.append(sign_1[i])
        sign_data.append(sign_2[i])
    return bytes(sign_data)


def rs4_get_xor_value(data, eval_js):
    arr_4 = eval(re.findall('\[0x.{2},0x.{2},0x.{2},0x.{2}\]', eval_js)[0])
    data += bytes(arr_4)
    table = [0 for _ in range(256)]
    for i in range(256):
        value = i
        for j in range(8):
            if (value & 128) != 0:
                value = value << 1 ^ 7
            else:
                value <<= 1
        table[i] = value & 255
    xor_value = 0
    data_len = len(data)
    i = 0
    while i < data_len:
        xor_value = table[(xor_value ^ data[i]) & 255]
        i += 1
    return xor_value


def aes_encrypt(data, key):
    iv = get_random_bytes(16)
    crypto = AES.new(key=key, mode=AES.MODE_CBC, iv=iv)
    return iv + crypto.encrypt(Padding.pad(data, AES.block_size))


def aes_decrypt(data, key):
    iv = data[:16]
    data = data[16:]
    crypto = AES.new(key=key, mode=AES.MODE_CBC, iv=iv)
    return Padding.unpad(crypto.decrypt(data), AES.block_size)


def main():
    requests = requests_html.HTMLSession()
    response = requests.get(url)
    html_js = filter(lambda n: '(function()' in n.text, response.html.find('script')).__next__().find('script', first=True).text
    js_url = response.html.find('script[charset="iso-8859-1"]', first=True).attrs['src']
    content = filter(lambda n: n.attrs['content'].startswith('{'), response.html.find('meta[content]')).__next__().attrs['content']
    encrypt_js = requests.get(parse.urljoin(url, js_url)).content.decode('iso-8859-1')
    ret = re.findall('ret=.{4}\.call.{12}', html_js)[0]
    ret_name = ret[-6: -2]
    ff = subprocess.Popen('node', stdin=subprocess.PIPE, stdout=subprocess.PIPE, encoding='utf-8')  # 需要安装node环境
    ff.stdin.write("window = global;\nwindow['$_ts'] = {}\n")
    ff.stdin.write(encrypt_js)
    ff.stdin.write(html_js.replace(ret, "ret={};window['$_ts']['js']=" + ret_name + ";console.log(JSON.stringify(window['$_ts']));process.exit(0)"))
    ff.stdin.close()
    ts_json = list(json.loads(ff.stdout.read()).values())

    rs_cookie = RS4Cookie(url).set_ts_json(ts_json).set_content(content).set_arr_16([14, 7, 1, 9, 4, 11, 4, 13, 6, 15, 8, 1, 10, 3, 12, 5]).generate(13)
    rs_cookie.set_raw_cookie(requests)
    rs_cookie.set_cookie(requests)
    print(requests.cookies)
    response = requests.get(url)
    print(response.status_code)


if __name__ == '__main__':
    main()
