import hashlib
import time
import random
import base64
import hmac

# 生成MD5哈希值
def generate_md5(input_string):
    md5 = hashlib.md5()
    md5.update(input_string.encode())
    return md5.hexdigest()


class AppSignGenerator:
    @staticmethod
    def hkey(path: str, time_num: int, nonce: str) -> str:
        base64_encoded = base64.b64encode(path.encode()).decode()
        result = [''] * 5

        nums = sum(1 for b in nonce if '0' <= b <= '9')
        time_num += nums

        # 将时间戳分成不同的位
        v24 = chr((time_num >> 24) & 0xFF)
        v16 = chr((time_num >> 16) & 0xFF)
        v8 = chr((time_num >> 8) & 0xFF)
        bytes_array = bytearray(8)

        # 生成的字符集
        v77 = ("23456789BCDFGHJKMNPQRTVWXY" + nonce.upper()).encode()

        bytes_array[4] = ord(v24)
        bytes_array[5] = ord(v16)
        bytes_array[6] = ord(v8)
        bytes_array[7] = time_num & 0xFF

        # HMAC 生成
        dist = AppSignGenerator.gen_hmac(bytes_array, base64_encoded.encode())
        reverse = dist[dist[19] & 0xF:dist[19] & 0xF + 4]

        # 字节数组转换为整数
        v34 = AppSignGenerator.byte_array_to_int(reverse)
        v35 = AppSignGenerator.bswap32(v34) & 0x7FFFFFFF
        v36 = v35
        v37 = int(1307386003 * ((v35 >> 2) & 0x1FFFFFFF)) >> 40

        v39 = v77[(v36 - 58 * (v36 // 58)) % 0x3A]
        v40 = v77[(v36 // 0x3A) % 0x3A]
        v41 = v77[(v36 // 0x2FA28) % 0x3A]
        v42 = v77[(v36 // 0xACAD10) % 0x3A]

        result[0] = chr(v39)
        result[1] = chr(v40)
        result[2] = chr(v37)
        result[3] = chr(v41)
        result[4] = chr(v42)

        # 应用自定义函数
        array = [ord(result[1]), ord(result[2]), ord(result[3]), ord(result[4])]
        AppSignGenerator.sub_249C(array)

        v43 = (sum(array) % 100)
        num = AppSignGenerator.format_with_leading_zeros(v43)
        return ''.join(result) + num

    @staticmethod
    def format_with_leading_zeros(value: int, min_length: int = 2) -> str:
        return str(value).zfill(min_length)

    @staticmethod
    def bswap32(x: int) -> int:
        return ((x << 24) & 0xFF000000) | ((x << 8) & 0x00FF0000) | ((x >> 8) & 0x0000FF00) | ((x >> 24) & 0x000000FF)

    @staticmethod
    def byte_array_to_int(bytes_array: bytearray) -> int:
        return int.from_bytes(bytes_array, byteorder='big')

    @staticmethod
    def gen_hmac(data: bytearray, key: str) -> bytearray:
        block_size = 64  # SHA-1 block size in bytes

        # Step 1: Pad the key to the block size
        if len(key) > block_size:
            key = hashlib.sha1(key).digest()
        padded_key = key.ljust(block_size, b'\0')

        # Step 2: Create inner and outer padded keys
        inner_key_pad = bytearray((padded_key[i] ^ 0x36) for i in range(block_size))
        outer_key_pad = bytearray((padded_key[i] ^ 0x5C) for i in range(block_size))

        # Step 3: Compute the inner hash
        inner_hash = hashlib.sha1(inner_key_pad + data).digest()

        # Step 4: Compute the outer hash
        return hashlib.sha1(outer_key_pad + inner_hash).digest()
    
    @staticmethod
    def sub_249C(result: list):
      v1 = result[0]  # w9
      v2 = result[1]  # w10
      v3 = result[2]  # w11
      v4 = result[3]  # w13

      v5 = 2 * v4
      v6 = 2 * v2
      v7 = (2 * v4) & 0xFE ^ 0x1B

      v8 = (2 * v1 & 0xFE ^ 0x1B) if (v1 & 0x80) != 0 else 2 * v1
      v9 = (2 * v8 & 0xFE ^ 0x1B) if (v8 & 0x80) != 0 else 2 * v8
      v10 = v9 ^ v8

      v11 = 2 * v10
      if (v10 & 0x80) != 0:
          v11 = (2 * v10 & 0xFF) ^ 0x1B

      v12 = 2 * v11
      if (v11 & 0x80) != 0:
          v12 = (2 * v11 & 0xFE) ^ 0x1B

      if (v2 & 0x80) != 0:
          v6 = (2 * v2 & 0xFF) ^ 0x1B

      v13 = 2 * v6
      if (v6 & 0x80) != 0:
          v13 = (2 * v6 & 0xFE) ^ 0x1B

      v14 = 2 * (v13 ^ v6)
      if ((v13 ^ v6) & 0x80) != 0:
          v14 = (2 * (v13 ^ v6) & 0xFF) ^ 0x1B

      v15 = v11 ^ v4
      v16 = 2 * v3
      v17 = v15 ^ v1
      v18 = v14 ^ v1 ^ v2 ^ v8

      v19 = (2 * v14 & 0xFE ^ 0x1B) if (v14 & 0x80) != 0 else 2 * v14

      if (v3 & 0x80) != 0:
          v16 = (2 * v3 & 0xFE) ^ 0x1B

      v20 = 2 * v16
      if (v16 & 0x80) != 0:
          v20 = (2 * v16 & 0xFE) ^ 0x1B

      v21 = v18 ^ v13
      v22 = v15 ^ v3
      v23 = v20 ^ v16

      if (v4 & 0x80) != 0:
          v5 = v7

      v24 = v22 ^ v16
      v25 = 2 * v23
      v26 = (v23 & 0x80) == 0

      v27 = v17 ^ v5 ^ v9 ^ v23
      v28 = (v25 & 0xFE ^ 0x1B) if not v26 else v25

      v29 = v24 ^ v13 ^ v6
      v30 = v28 ^ v2 ^ v3
      v31 = (2 * v28 & 0xFE ^ 0x1B) if (v28 & 0x80) != 0 else 2 * v28

      v32 = v27 ^ v14 ^ v12
      v33 = v30 ^ v6

      if (v28 & 0x80) == 0:
          v31 = 2 * v28

      v34 = v32 ^ v19
      v35 = v33 ^ v10

      v36 = (2 * v5 & 0xFF ^ 0x1B) if (v5 & 0x80) != 0 else 2 * v5

      result[0] = v34
      v37 = v36 ^ v5
      v38 = 2 * (v36 ^ v5)
      v39 = v21 ^ v37

      if (v37 & 0x80) == 0:
          v40 = v38
      else:
          v40 = v38 & 0xFE ^ 0x1B

      v41 = v39 ^ v28 ^ v19
      result[1] = v41 ^ v31

      v42 = (2 * v40 & 0xFE ^ 0x1B) if (v40 & 0x80) != 0 else 2 * v40

      v43 = v35 ^ v20 ^ v40 ^ v31
      result[2] = v43 ^ v42
      result[3] = v29 ^ v36 ^ v40 ^ v12 ^ v42



class AppParamsBuilder:
    base_url = "https://api.xiaoheihe.cn"
    def __init__(self, path: str):
        current_time = int(time.time())
        random_seed = str(current_time) + str(random.random())[:18]
        nonce = generate_md5(random_seed)
        self.path = path
        self.time = current_time
        self.nonce = nonce

    def build(self):

        hkey = AppSignGenerator.hkey(self.path, self.time, self.nonce)
        print(hkey)
        # https://api.xiaoheihe.cn/game/get_game_list_v3/?filter_tag=all&sort_type=heybox_wish&filter_platform=all&only_chinese=0&filter_release=all&filter_steam_deck=all&filter_version=all&filter_head=pc&show_dlc=0&filter_os=all&filter_family_share=all&filter_library=no&offset=0&limit=30&heybox_id=36331242&imei=712a5ff71b30482a&device_info=M2104K10AC&nonce=sYRgJfL252rFvEeUuVNJ5GlJPK8rAivP&hkey=BA05AF0C&os_type=Android&x_os_type=Android&x_client_type=mobile&os_version=13&version=1.3.335&build=883&_time=1726809839&dw=393&channel=heybox_xiaomi&x_app=heybox
        buildParams = {
            "filter_tag": "all",
            "sort_type": "heybox_wish",
            "filter_platform": "all",
            "only_chinese": "0",
            "filter_release": "all",
            "filter_steam_deck": "all",
            "filter_version": "all",
            "filter_head": "pc",
            "show_dlc": "0",
            "filter_os": "all",
            "filter_family_share": "all",
            "filter_library": "no",
            "offset": "0",
            "limit": "30",
            "heybox_id": "36331242",
            "imei": "712a5ff71b30482a",
            "device_info": "M2104K10AC",
            "nonce": self.nonce,
            "hkey": hkey,
            "os_type": "Android",
            "x_os_type": "Android",
            "x_client_type": "mobile",
            "os_version": "13",
            "version": "1.3.335",
            "build": "883",
            "dw": "393",
            "channel": "heybox_xiaomi",
            "x_app": "heybox",
            "_time": self.time,
        }

        # 转为 ?xx=xxx&xxx=xxx
        query = "&".join([f"{k}={v}" for k, v in buildParams.items()])
        return f"?{query}"
    def url(self):
        return f"{self.base_url}{self.path}{self.build()}"

        


api = AppParamsBuilder('/game/get_game_list_v3')
print(api.url())
