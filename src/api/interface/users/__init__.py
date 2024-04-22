import httpx
from nonebot.log import logger
from fastapi import APIRouter
from pydantic import BaseModel
# 解密信息
import hashlib
import base64
from Crypto.Cipher import AES
import json

from ...utils.responses import create_response
# from src.api.core.hooks.data_hook import get_user_data
# from ...core.utils.security import auth_user, get_current_username, get_pwd_hash
# from ...core.utils.hashing import generate_code
# from ...models.db import UserTable

from ..api import users
router = APIRouter()

logger.success(f'USER API 接口，加载成功')

# @router.post()
# async def


class QQAuth(BaseModel):
    code: str


@router.post(users.qqauth.value)
async def qq_auth(item: QQAuth):
    """
    注册用户
    """
    print('qq_auth', item)

    if item.code:
        appid = '1112291169'
        secret = 'SEMzYKEO1EQQiY3w'
        url = f'https://api.q.qq.com/sns/jscode2session?appid={appid}&secret={secret}&js_code={item.code}&grant_type=authorization_code'
        res = httpx.get(url)
        try:
            jsondata = res.json()
        except httpx.HTTPStatusError as e:
            jsondata = None

        if jsondata:
            return create_response(data=jsondata, message='success')

    return create_response(ret=1, message='error')


class UserItem(BaseModel):
    signature: str
    rawData: str
    session_key: str
    iv:str
    encryptedData:str



def check_signature(rawData, session_key, signature):
    if not rawData:
        return True
    # 使用相同的算法计算出签名
    hash_string = rawData + session_key
    hash_object = hashlib.sha1(hash_string.encode())
    signature2 = hash_object.hexdigest()
    print('signature2',signature2)
    print('signature',signature)
    # 比对 signature 与 signature2
    return signature == signature2

def decrypt_data(encryptedData, session_key, iv):
    # 对称解密秘钥 aeskey = Base64_Decode(session_key)
    aeskey = base64.b64decode(session_key)

    # 对称解密算法初始向量 为Base64_Decode(iv)
    iv = base64.b64decode(iv)

    # 对称解密使用的算法为 AES-128-CBC
    cipher = AES.new(aeskey, AES.MODE_CBC, iv)

    # 对称解密的目标密文为 Base64_Decode(encryptedData)
    encryptedData = base64.b64decode(encryptedData)

    # 解密数据
    decrypted = json.loads(cipher.decrypt(encryptedData).decode())

    return decrypted


@router.post(users.get_user.value)
async def get_user(item: UserItem):

    if check_signature(item.rawData, item.session_key, item.signature):
        user_info = decrypt_data(item.encryptedData, item.session_key, item.iv)
        print(user_info)
        return create_response(data=user_info, message='success')
    else:
        print("数据签名验证失败")
        return create_response(ret=1, message='error')
    # print(item)

# @router.get(users.login.value)
# async def login():
#     """
#     注册用户
#     """
#     username = 'haotian'
#     # 注册用户
#     login_data = get_user_data(username= username)

#     # 获取用户信息
#     access_token = login_data.get('access_token')
#     user = get_current_username(access_token)

#     # 验证密码
#     pass1 = '1234567'
#     pass2 = '1234567'

#     # 获取密码哈希
#     pwd = get_pwd_hash(pass1)
#     pwd2 = get_pwd_hash(pass2)

#     # 检验错误密码
#     auth = auth_user(pass1, pwd2)

#     # 获取所有用户
#     user_data = await UserTable.all().values()

#     print('user', user)
#     # await UserTable.filter(user_id=user)

#     # 生成登录码
#     code = generate_code()

#     return {"message": "Hello, world!","data":{
#         "pwd":pwd,
#         **login_data
#     },"user":user_data,"auth":auth,"code":code}
