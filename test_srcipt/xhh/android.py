import base64
import struct
import random
import time
from urllib.parse import urlparse
from checksum import checksum
from hash import sha1_hmac

# 随机生成 nonce
nonce_dict = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

def random_nonce() -> str:
    nonce = ''.join(random.choice(nonce_dict) for _ in range(32))
    return nonce

# 计算摘要
def calculate_digest(url: str, timestamp: int) -> bytes:
    secret = base64.b64encode(url.encode('utf-8')).decode('utf-8')
    return sha1_hmac(secret, timestamp)


# 计算最终 hkey
def calculate(url: str, timestamp: int = 0, nonce: str = '') -> str:
    timestamp = timestamp or int(time.time())
    nonce = nonce or random_nonce()

    parsed_url = urlparse(url)
    pathname = parsed_url.path
    u = '/' + '/'.join(filter(None, pathname.split('/'))) + '/'

    number_in_nonce = ''.join(filter(str.isdigit, nonce))
    ts = timestamp + len(number_in_nonce)
    digest = calculate_digest(u, ts)

    dict_str = '2345JKMNPQRT6789BCDFGHVWXY' + nonce.upper()
    rnd_pos = digest[19] & 0xf

    # Unpack 4-byte integer from digest starting at rnd_pos
    seed = struct.unpack('>I', digest[rnd_pos:rnd_pos + 4])[0] & 0x7fffffff

    key = ''
    for _ in range(5):
        c = seed % len(dict_str)
        seed //= len(dict_str)
        key += dict_str[c]

    # Calculate suffix
    key_slice = key[-4:]
    key_slice_ascii = [ord(c) for c in key_slice]
    suffix = str(checksum(key_slice_ascii)).zfill(2)

    return f"hkey={key}{suffix}&_time={timestamp}&nonce={nonce}"
