import hashlib
import time
import random
import json
from urllib.parse import urlencode

import requests
import os
# 配置项
# 代理ip设置
proxies = {}


header = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.xiaoheihe.cn/",
}

# 图片形式的消息里最多展现的项目数量
Limit_num = 20

# 其他必需的配置项，不了解的话请勿乱改
s = requests.session()


def other_request(url, headers=None, cookie=None):
    """
    请求
    """
    try:
        content = s.get(url, headers=headers, cookies=cookie, timeout=4)
    except Exception:
        content = s.get(url, headers=headers, cookies=cookie,
                        proxies=proxies, timeout=4)
    return content


m = ['a', 'b', 'e', 'g', 'h', 'i', 'm', 'n',
     'o', 'p', 'q', 'r', 's', 't', 'u', 'w']


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


def dict_to_query_string(params: dict) -> str:
    """
    将字典转换为 URL 查询参数格式
    :param params: 要转换的字典
    :return: 转换后的查询参数字符串
    """
    # 使用 urllib.parse.urlencode 将字典转换为查询参数字符串
    query_string = urlencode(params)
    return f"?{query_string}"

url = 'https://api.xiaoheihe.cn'
links_text = "/bbs/web/profile/post/links"
detial_text = "/bbs/app/api/share/data"
user_info_text = "/bbs/app/profile/user/profile"

# https://api.xiaoheihe.cn/bbs/web/profile/post/links?os_type=web&version=999.0.3&x_app=heybox_website&x_client_type=web&heybox_id=43580550&x_os_type=Mac&hkey=FDC9386&_time=1718355163&nonce=8957D56ECF6C4DA42220161FBF925778&userid=1985029&limit=20&offset=0&post_type=2&list_type=article
# https://api.xiaoheihe.cn/bbs/app/api/share/data/?os_type=web&app=heybox&client_type=mobile&version=999.0.3&x_client_type=web&x_os_type=Mac&x_client_version=&x_app=heybox&heybox_id=-1&offset=0&limit=3&link_id=125369222&use_concept_type=&hkey=C2N4Q78&_time=1718355967&nonce=28BCBB38D225EA790D352A9CC3E8932A
# https://api.xiaoheihe.cn/bbs/app/api/share/data/?os_type=web&app=heybox&client_type=mobile&version=999.0.3&x_client_type=web&x_os_type=Mac&x_client_version=&x_app=heybox&heybox_id=-1&offset=0&limit=3&link_id=125369222&use_concept_type=&hkey=OG9HQ86&_time=1718356744&nonce=9C5908337EA30ECB6F63E0FBA2BC03A8

# 获取文章评论
# https://api.xiaoheihe.cn/bbs/app/link/tree?link_id=133798885&page=1&limit=100&sort_filter=hot&client_type=heybox_chat&x_client_type=web&os_type=web&x_os_type=Windows&device_info=Chrome&x_app=heybox_chat&version=999.0.3&web_version=1.0.0&chat_os_type=web&chat_version=1.24.4&chat_exe_version=&heybox_id=36331242&nonce=fb1da23e46ff7597356afaf788bdb5e2&_time=1726630912&hkey=KMF1D02&_chat_time=540590493&imei=58dcf9f48bba35a0&build=783


def article_url(page: int, user_id: int, limit: int = 20):
    """
    获取帖子列表，包含点击量 评论数等信息
    """
    obj = D(links_text)
    query_string = dict_to_query_string({
        "os_type": "web",
        "version": "999.0.3",
        "x_app": "heybox_website",
        "x_client_type": "web",
        "heybox_id": 43580550,
        "x_os_type": "Mac",
        "hkey": obj["hkey"],
        "_time": obj["_time"],
        "nonce": obj["nonce"],
        "userid": user_id,
        "limit": limit,
        "offset": str((page - 1) * 20),
        "post_type": 2,
        "list_type": "article"
    })
    return f'{url}{links_text}?{query_string}'


def detail_ulr(linkid: int, page: int = 1):
    """
    获取分享详情
    """
    obj = D(detial_text)
    return f'https://api.xiaoheihe.cn/bbs/app/api/share/data/?os_type=web&app=heybox&client_type=mobile&version=999.0.3&x_client_type=web&x_os_type=Mac&x_client_version=&x_app=heybox&heybox_id=-1&offset={str((page - 1) * 20)}&limit=20&link_id={linkid}&use_concept_type=&hkey={obj["hkey"]}&_time={obj["_time"]}&nonce={obj["nonce"]}'


def get_article_list(user_id: str, page: int = 1, limit: int = 20):
    """
    获取文章列表
    """
    url = article_url(page=page, user_id=user_id, limit=limit)
    json_page = json.loads(other_request(url, headers=header).text)
    # result_list = json_page["post_links"]
    # result = []
    # for item in result_list:
    #     gameinfo = {
    #         "链接": item["share_url"],
    #         "图片": item["thumbs"][0],
    #         "标题": item["title"],
    #     }
    #     result.append(gameinfo)

    return json_page

def get_user_info(user_id: str):
    """
    获取用户信息
    """
    user_url = f'{url}{user_info_text}?userid={user_id}'
   
    user_json = json.loads(other_request(user_url, headers=header).text)

    if not user_json or user_json.get('status') != 'ok':
        return None
    return user_json['result']['account_detail'] if user_json.get('result') else None
