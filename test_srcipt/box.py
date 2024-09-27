import hashlib
import time
import random
import json
from urllib.parse import urlencode
from config import *



# 字符集
char_set = ['a', 'b', 'e', 'g', 'h', 'i', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'w']

# 左移和按位与操作，主要用于加密计算
def byte_shift(e):
    return 255 & (e << 1 ^ 27) if 128 & e else e << 1

# 单字节异或操作
def byte_xor(e):
    return byte_shift(e) ^ e

# 扩展异或
def byte_expand(e):
    return byte_xor(byte_shift(e))

# 进一步的异或运算
def byte_expand_more(e):
    return byte_expand(byte_xor(byte_shift(e)))

# 最终字节转换，用于加密
def final_byte_transform(e):
    return byte_expand_more(e) ^ byte_expand(e) ^ byte_xor(e)

# 将输入字符串转换成整数，用于生成验证码等加密操作
def convert_to_int(input_string):
    byte_list = [ord(c) for c in input_string[-4:]]
    transformed = [0, 0, 0, 0]
    transformed[0] = final_byte_transform(byte_list[0]) ^ byte_expand_more(byte_list[1]) ^ byte_expand(byte_list[2]) ^ byte_xor(byte_list[3])
    transformed[1] = byte_xor(byte_list[0]) ^ final_byte_transform(byte_list[1]) ^ byte_expand_more(byte_list[2]) ^ byte_expand(byte_list[3])
    transformed[2] = byte_expand(byte_list[0]) ^ byte_xor(byte_list[1]) ^ final_byte_transform(byte_list[2]) ^ byte_expand_more(byte_list[3])
    transformed[3] = byte_expand_more(byte_list[0]) ^ byte_expand(byte_list[1]) ^ byte_xor(byte_list[2]) ^ final_byte_transform(byte_list[3])
    return sum(transformed)

# 生成加密字符串，类似于验证码生成
def generate_code(endpoint, timestamp, nonce):
    # 规范化URL路径
    normalized_endpoint = "/" + "/".join(filter(lambda x: x, endpoint.split("/"))) + "/"
    
    # 字符集
    char_pool = "JKMNPQRTX1234OABCDFG56789H"
    
    # 处理nonce和字符集进行哈希运算
    hash_nonce = generate_md5("".join(filter(lambda e: e.isdigit(), nonce + char_pool)))
    hashed_string = generate_md5(str(timestamp) + normalized_endpoint + hash_nonce)
    
    # 提取数字并拼接为9位
    digits_only = "".join(filter(lambda e: e.isdigit(), hashed_string))[:9]
    extended_digits = digits_only.ljust(9, "0")
    
    numeric_value = int(extended_digits)
    code = ""
    
    # 使用数字生成字符组合
    for _ in range(5):
        index = numeric_value % len(char_pool)
        numeric_value //= len(char_pool)
        code += char_pool[index]
    
    # 计算校验码（百分制两位数字）
    check_sum = str(convert_to_int(code) % 100).zfill(2)
    return code + check_sum

# 生成MD5哈希值
def generate_md5(input_string):
    md5 = hashlib.md5()
    md5.update(input_string.encode())
    return md5.hexdigest()

# 生成请求签名和随机数
def create_signature(endpoint):
    result = {}
    current_time = int(time.time())
    random_seed = str(current_time) + str(random.random())[:18]
    
    nonce = generate_md5(random_seed).upper()
    result['hkey'] = generate_hkey(endpoint, current_time, nonce)
    result["_time"] = current_time
    result["nonce"] = nonce
    return result

# 根据加密算法生成hkey
def generate_hkey(endpoint, timestamp, nonce):
    return generate_code(endpoint, timestamp + 1, nonce)


def dict_to_query_string(params: dict,text_url:str) -> str:
    """
    将字典转换为 URL 查询参数格式
    :param params: 要转换的字典
    :return: 转换后的查询参数字符串
    """

    obj = create_signature(text_url)
    baseQuery = {
        "client_type": "heybox_chat",
        "x_client_type": "web",
        "os_type": "web",
        "x_os_type": "Windows",
        "device_info": "Chrome",
        "x_app": "heybox_chat",
        "version": "999.0.3",
        "web_version": "1.0.0",
        "chat_os_type": "web",
        "chat_version": "1.24.4",
        "chat_exe_version": "",
        "heybox_id": "36331242",
        "hkey": obj["hkey"],
        "_time": obj["_time"],
        "nonce": obj["nonce"],
        "imei": "58dcf9f48bba35a0",
        "build": "783"
    }

    params.update(baseQuery)

    # 使用 urllib.parse.urlencode 将字典转换为查询参数字符串
    query_string = urlencode(params)
    return f"?{query_string}"

url = "https://api.xiaoheihe.cn"
text = "/bbs/web/profile/post/links"
detial_text = "/bbs/app/api/share/data"
list_text='/game/get_game_list_v3'
search_text = '/bbs/app/api/general/search/v1'

# https://api.xiaoheihe.cn/bbs/web/profile/post/links?os_type=web&version=999.0.3&x_app=heybox_website&x_client_type=web&heybox_id=43580550&x_os_type=Mac&hkey=FDC9386&_time=1718355163&nonce=8957D56ECF6C4DA42220161FBF925778&userid=1985029&limit=20&offset=0&post_type=2&list_type=article
# https://api.xiaoheihe.cn/bbs/app/api/share/data/?os_type=web&app=heybox&client_type=mobile&version=999.0.3&x_client_type=web&x_os_type=Mac&x_client_version=&x_app=heybox&heybox_id=-1&offset=0&limit=3&link_id=125369222&use_concept_type=&hkey=C2N4Q78&_time=1718355967&nonce=28BCBB38D225EA790D352A9CC3E8932A

# 获取文章评论
# https://api.xiaoheihe.cn/bbs/app/link/tree?link_id=133798885&page=1&limit=100&sort_filter=hot&client_type=heybox_chat&x_client_type=web&os_type=web&x_os_type=Windows&device_info=Chrome&x_app=heybox_chat&version=999.0.3&web_version=1.0.0&chat_os_type=web&chat_version=1.24.4&chat_exe_version=&heybox_id=36331242&nonce=fb1da23e46ff7597356afaf788bdb5e2&_time=1726630912&hkey=KMF1D02&_chat_time=540590493&imei=58dcf9f48bba35a0&build=783
# 搜索
# https://api.xiaoheihe.cn/bbs/app/api/general/search/v1


def r_url(page: int,user_id:int,limit:int=20):
    """
    获取帖子详情，包含点击量 评论数等信息
    """
    obj = create_signature(text)
    return f'https://api.xiaoheihe.cn/bbs/web/profile/post/links?os_type=web&version=999.0.3&x_app=heybox_website&x_client_type=web&heybox_id=43580550&x_os_type=Mac&hkey={obj["hkey"]}&_time={obj["_time"]}&nonce={obj["nonce"]}&userid={user_id}&limit={limit}&offset={str((page - 1) * 20)}&post_type=2&list_type=article'

def detail_ulr(linkid:int,page:int=1):
    """
    获取分享详情
    """
    obj = create_signature(detial_text)
    return f'https://api.xiaoheihe.cn/bbs/app/api/share/data/?os_type=web&app=heybox&client_type=mobile&version=999.0.3&x_client_type=web&x_os_type=Mac&x_client_version=&x_app=heybox&heybox_id=-1&offset={str((page - 1) * 20)}&limit=20&link_id={linkid}&use_concept_type=&hkey={obj["hkey"]}&_time={obj["_time"]}&nonce={obj["nonce"]}'


def list_url():
    # https://api.xiaoheihe.cn/game/get_game_list_v3/?filter_tag=all&sort_type=heybox_wish&filter_platform=all&only_chinese=0&filter_release=all&filter_steam_deck=all&filter_version=all&filter_head=pc&show_dlc=0&filter_os=all&filter_family_share=all&filter_library=no&offset=0&limit=30&heybox_id=36331242&imei=712a5ff71b30482a&device_info=Chrome&nonce=sYRgJfL252rFvEeUuVNJ5GlJPK8rAivP&hkey=BA05AF0C&os_type=Android&x_os_type=Android&x_client_type=mobile&os_version=13&version=1.3.335&build=883&_time=1726809839&dw=393&channel=heybox_xiaomi&x_app=heybox
    obj = create_signature(list_text)

    return f'https://api.xiaoheihe.cn/game/get_game_list_v3/?filter_tag=all&sort_type=heybox_wish&filter_platform=all&only_chinese=0&filter_release=all&filter_steam_deck=all&filter_version=all&filter_head=pc&show_dlc=0&filter_os=all&filter_family_share=all&filter_library=no&offset=0&limit=30&heybox_id=36331242&imei=712a5ff71b30482a&device_info=Chrome&nonce={obj["nonce"]}&hkey={obj["hkey"]}&os_type=web&x_os_type=Mac&x_client_type=web&os_version=13&version=1.3.335&build=883&_time={obj["_time"]}&dw=393&channel=heybox_google&x_app=heybox'


def search_url(keyword:str=''):

    # obj = create_signature(search_text)
    query_string = dict_to_query_string({
        "q": keyword,
        "search_type":"game",
        "limit": 20,
        "offset": 0,
        "time_range":"",
        "sort_filter":"sort_filter",
    },search_text)
    return f'{url}{search_text}{query_string}'
    


header = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.xiaoheihe.cn/",
}

def get_article_list(page: int = 1,limit:int=20):
    # 1985029 小三
    # 26850094 清娜
    # 43580550 鹅
    # url = r_url(page=page,limit=limit, user_id=26850094)
    # 125914096 125934489
    # link_url = detail_ulr(125934489,page=1)
    print('url ---',search_url('艾尔登'))
    # print('link_url ---', link_url)

    # json_page = json.loads(other_request(url, headers=header).text)
    # result_list = json_page["post_links"]
    # result = []
    # for item in result_list:
    #     gameinfo = {
    #         "链接": item["share_url"],
    #         "图片": item["thumbs"][0],
    #         "标题": item["title"],
    #     }
    #     result.append(gameinfo)

    # return result
    return []


# curl -X GET 'https://api.xiaoheihe.cn/bbs/app/link/tree?h_src=YmJzX2FwcF9mZWVkc19fZmxvd19wb29sX2ZvcmNlX2luc2VydF9zcmNfXzBfX2xpbmtfaWRfXzEyOTI4ODI3OV9fYXBwX2ZlZWRzX2V4cG9zdXJlX2NvdW50X183OTQ3X19yZXF1ZXN0X2lkX18wdUFjTUZ5alpPeVloWFlZMHhVRGVDVWlBSjhZYmhWNV9fcmVjYWxsX18xMF9fYWxfX1JFQzAwMV9fdHlwZV92Ml9fMl9fZmxvd190aWNrZXRfaWRfXzA%3D&link_id=129288279&page=1&limit=30&is_first=1&owner_only=0&hide_cy=0&index=0&heybox_id=36331242&imei=58dcf9f48bba35a9&device_info=M2104K10AC&nonce=gZXtM9MIqWUpBlOXJdK3rzo2BBkclODj&hkey=1BA54A0D&os_type=Android&x_os_type=Android&x_client_type=mobile&os_version=12&version=1.3.312&build=824&_time=1722251270&dw=393&channel=heybox_google&x_app=heybox' -H 'User-Agent: Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.118 Safari/537.36 ApiMaxJia/1.0' -H 'Accept-Encoding: gzip' -H 'referer: http://api.maxjia.com/' -H 'Cookie: pkey=0MmRjcnRwZXO3kWoP3a/nv4l3iF8gJjbUY3+14/VspbnHI6N3o7ugbrAJIwe1RZ6vW7mrTlSkngH+QfBj953Diw=='