import hashlib
import time
import random
import json
from config import *


m = ['a', 'b', 'e', 'g', 'h', 'i', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'w']

def g(e):
    return 255 & (e << 1 ^ 27) if 128 & e else e << 1

def x(e):
    return g(e) ^ e

def w(e):
    return x(g(e))

def v(e):
    return w(x(g(e)))

def C(e):
    return v(e) ^ w(e) ^ x(e)


def conversion(i):
    e = [ord(c) for c in i[-4:]]
    t = [0, 0, 0, 0]
    t[0] = C(e[0]) ^ v(e[1]) ^ w(e[2]) ^ x(e[3])
    t[1] = x(e[0]) ^ C(e[1]) ^ v(e[2]) ^ w(e[3])
    t[2] = w(e[0]) ^ x(e[1]) ^ C(e[2]) ^ v(e[3])
    t[3] = v(e[0]) ^ w(e[1]) ^ x(e[2]) ^ C(e[3])
    e[0] = t[0]
    e[1] = t[1]
    e[2] = t[2]
    e[3] = t[3]
    return sum(e)


def E(e, t, n):
    e = "/" + "/".join(filter(lambda x: x, e.split("/"))) + "/"
    # o = "JKMNPQRTX1234OABCDFG56789H"
    # r = Y(n + o)
    # a = Y(str(t) + e + r)[:9].ljust(9, "0")
    # s = int.from_bytes(a.encode(), byteorder='big')

    i = ""
    o = "JKMNPQRTX1234OABCDFG56789H"

    r = Y("".join(filter(lambda e: e.isdigit(), n + o)))
    a = Y(str(t) + e + r)
    a = "".join(filter(lambda e: e.isdigit(), a))[:9]
    aWithZero = a + "0" * (9 - len(a))

    s = int(aWithZero)
    for _ in range(5):
        p = s % len(o)
        s = s // len(o)
        i += o[p]
    
    d = str(conversion(i) % 100)
    if len(d) < 2:
        d = "0" + d
    return i + d

def Y(t):
    md5 = hashlib.md5()
    md5.update(t.encode())
    return md5.hexdigest()

def D(e):
    t = {}
    n = int(time.time())
    p = str(n) + str(random.random())[:18]
    i = Y(p).upper()
    t['hkey'] = F_g(e, n, i)
    t["_time"] = n
    t["nonce"] = i
    return t

def F_g(e, t, n):
    return E(e, t + 1, n)

text = "/bbs/web/profile/post/links"
detial_text = "/bbs/app/api/share/data"


# https://api.xiaoheihe.cn/bbs/web/profile/post/links?os_type=web&version=999.0.3&x_app=heybox_website&x_client_type=web&heybox_id=43580550&x_os_type=Mac&hkey=FDC9386&_time=1718355163&nonce=8957D56ECF6C4DA42220161FBF925778&userid=1985029&limit=20&offset=0&post_type=2&list_type=article
# https://api.xiaoheihe.cn/bbs/app/api/share/data/?os_type=web&app=heybox&client_type=mobile&version=999.0.3&x_client_type=web&x_os_type=Mac&x_client_version=&x_app=heybox&heybox_id=-1&offset=0&limit=3&link_id=125369222&use_concept_type=&hkey=C2N4Q78&_time=1718355967&nonce=28BCBB38D225EA790D352A9CC3E8932A
# https://api.xiaoheihe.cn/bbs/app/api/share/data/?os_type=web&app=heybox&client_type=mobile&version=999.0.3&x_client_type=web&x_os_type=Mac&x_client_version=&x_app=heybox&heybox_id=-1&offset=0&limit=3&link_id=125369222&use_concept_type=&hkey=OG9HQ86&_time=1718356744&nonce=9C5908337EA30ECB6F63E0FBA2BC03A8

def r_url(page: int,user_id:int):
    obj = D(text)
    return f'https://api.xiaoheihe.cn/bbs/web/profile/post/links?os_type=web&version=999.0.3&x_app=heybox_website&x_client_type=web&heybox_id=43580550&x_os_type=Mac&hkey={obj["hkey"]}&_time={obj["_time"]}&nonce={obj["nonce"]}&userid={user_id}&limit=20&offset={str((page - 1) * 20)}&post_type=2&list_type=article'

def detail_ulr(linkid:int,page:int=1):
    obj = D(detial_text)
    return f'https://api.xiaoheihe.cn/bbs/app/api/share/data/?os_type=web&app=heybox&client_type=mobile&version=999.0.3&x_client_type=web&x_os_type=Mac&x_client_version=&x_app=heybox&heybox_id=-1&offset={str((page - 1) * 20)}&limit=20&link_id={linkid}&use_concept_type=&hkey={obj["hkey"]}&_time={obj["_time"]}&nonce={obj["nonce"]}'


header = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.xiaoheihe.cn/",
}

def get_article_list(page: int = 1):
    # 1985029 小三
    # 26850094 清娜
    # 43580550 鹅
    url = r_url(page=page, user_id=26850094)
    # 125914096 125934489
    link_url = detail_ulr(125934489,page=1)
    # print(url)
    print(link_url)

    json_page = json.loads(other_request(url, headers=header).text)
    result_list = json_page["post_links"]
    result = []
    for item in result_list:
        gameinfo = {
            "链接": item["share_url"],
            "图片": item["thumbs"][0],
            "标题": item["title"],
        }
        result.append(gameinfo)

    return result


# curl -X GET 'https://api.xiaoheihe.cn/bbs/app/link/tree?h_src=YmJzX2FwcF9mZWVkc19fZmxvd19wb29sX2ZvcmNlX2luc2VydF9zcmNfXzBfX2xpbmtfaWRfXzEyOTI4ODI3OV9fYXBwX2ZlZWRzX2V4cG9zdXJlX2NvdW50X183OTQ3X19yZXF1ZXN0X2lkX18wdUFjTUZ5alpPeVloWFlZMHhVRGVDVWlBSjhZYmhWNV9fcmVjYWxsX18xMF9fYWxfX1JFQzAwMV9fdHlwZV92Ml9fMl9fZmxvd190aWNrZXRfaWRfXzA%3D&link_id=129288279&page=1&limit=30&is_first=1&owner_only=0&hide_cy=0&index=0&heybox_id=36331242&imei=58dcf9f48bba35a9&device_info=M2104K10AC&nonce=gZXtM9MIqWUpBlOXJdK3rzo2BBkclODj&hkey=1BA54A0D&os_type=Android&x_os_type=Android&x_client_type=mobile&os_version=12&version=1.3.312&build=824&_time=1722251270&dw=393&channel=heybox_google&x_app=heybox' -H 'User-Agent: Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.118 Safari/537.36 ApiMaxJia/1.0' -H 'Accept-Encoding: gzip' -H 'referer: http://api.maxjia.com/' -H 'Cookie: pkey=0MmRjcnRwZXO3kWoP3a/nv4l3iF8gJjbUY3+14/VspbnHI6N3o7ugbrAJIwe1RZ6vW7mrTlSkngH+QfBj953Diw=='