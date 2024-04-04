from nonebot.log import logger
from fastapi import APIRouter
from ..api import users
router = APIRouter()

logger.success('USER API 接口，加载成功')

@router.get(users.sign_up.value)
async def sign_user():
    """
    注册用户
    """
    return {"message": "Hello, world!"}
