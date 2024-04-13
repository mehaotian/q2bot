from nonebot.log import logger
from fastapi import APIRouter
from src.api.core.hooks.data_hook import get_user_data
from ...core.utils.security import auth_user, get_current_username, get_pwd_hash
from ...core.utils.hashing import generate_code
from ...models.db import UserTable

from ..api import users
router = APIRouter()

logger.success(f'USER API 接口，加载成功')
print(users.login.value)

@router.get(users.login.value)
async def login():
    """
    注册用户
    """
    username = 'haotian'
    # 注册用户
    login_data = get_user_data(username= username)

    # 获取用户信息
    access_token = login_data.get('access_token')
    user = get_current_username(access_token)

    # 验证密码
    pass1 = '1234567'
    pass2 = '1234567'

    # 获取密码哈希
    pwd = get_pwd_hash(pass1)
    pwd2 = get_pwd_hash(pass2)

    # 检验错误密码
    auth = auth_user(pass1, pwd2)

    # 获取所有用户
    user_data = await UserTable.all().values()

    print('user', user)
    # await UserTable.filter(user_id=user)

    # 生成登录码
    code = generate_code()

    return {"message": "Hello, world!","data":{
        "pwd":pwd,
        **login_data
    },"user":user_data,"auth":auth,"code":code}
