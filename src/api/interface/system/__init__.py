from nonebot.log import logger
from fastapi import APIRouter
from pydantic import BaseModel
from tortoise.exceptions import OperationalError

from ...utils.responses import create_response
from ...models.db import UserTable

from ..api import sys
router = APIRouter()

logger.success(f'SYSTEM API 接口，加载成功')


class LotteryItem(BaseModel):
    title: str
    passwrod: str = None


@router.post(sys.lottery.value)
async def lottery(item: LotteryItem):
    """
    提交抽奖
    """
    return create_response(
        ret=0,
        message="Success",
        data=item
    )


class VerifyKey(BaseModel):
    key: str
    qq: str


@router.post(sys.verify_key.value)
async def verify_key(item: VerifyKey):
    """
    验证用户key，qq
    """
    key = item.key
    qq = item.qq

    print(item)
    if not qq:
        return create_response(
            ret=1,
            message="请输入qq号",
        )

    if not key:
        return create_response(
            ret=1,
            message="用户验证失败或不存在，请重新获取url",
        )

    # 通过 key 匹配用户表的 login_key
    try:
        user = await UserTable.filter(login_key=item.key, user_id=qq).values()
    except OperationalError as e:
        logger.error(f'查询用户失败: {e}')
        return create_response(
            ret=1,
            message="数据库操作失败，请稍后再试，或请联系鹅子处理",
        )

    if user:
        return create_response(
            ret=0,
            message="验证成功",
            data=user[0]
        )

    return create_response(
        ret=1,
        message="用户验证失败或不存在，请重新获取url,或联系鹅子",
    )
