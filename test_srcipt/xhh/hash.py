import hashlib
import hmac
import struct

def md5(data: str) -> bytes:
    """生成MD5哈希"""
    h = hashlib.md5()
    h.update(data.encode('utf-8'))
    return h.digest()

def sha1(data: str) -> bytes:
    """生成SHA-1哈希"""
    h = hashlib.sha1()
    h.update(data.encode('utf-8'))
    return h.digest()

def sha1_hmac(secret: str, timestamp: int) -> bytes:
    """生成HMAC-SHA1哈希，带有时间戳的结构打包"""
    secret_bytes = secret.encode('utf-8')
    packed_timestamp = struct.pack('>Q', timestamp)  # 将时间戳打包为 64-bit 大端格式
    h = hmac.new(secret_bytes, packed_timestamp, hashlib.sha1)
    return h.digest()
