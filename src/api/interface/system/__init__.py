from datetime import datetime, timedelta
import nonebot
from nonebot import get_bot
from nonebot.adapters.onebot.v11 import (
    Bot,
    Message,
    MessageSegment
)
from nonebot.log import logger
from fastapi import APIRouter
from pydantic import BaseModel
from tortoise.exceptions import OperationalError

from ...utils.responses import create_response
from ...models.db import UserTable, RewardTable

from ..api import sys
router = APIRouter()

logger.success(f'SYSTEM API 接口，加载成功')


class LotteryItem(BaseModel):
    # 用户id
    uid: str
    # 群id
    gid: str
    # 抽奖标题
    title: str
    # 抽奖内容
    content: str
    # 参与人数
    join_number: int
    # 抽奖类型 0 按时间开奖 1 按人数开奖
    type: int
    # 开奖时间 ，如果type 为1 ,未满足时按开奖时间
    open_time: str
    # 中奖份数
    win_number: int


@router.post(sys.lottery.value)
async def lottery(item: LotteryItem):
    """
    提交抽奖
    """

    bot: Bot = get_bot()

    # 将传入的时间字符串转换为 datetime 对象
    open_time = datetime.strptime(item.open_time, "%Y-%m-%d %H:%M")
    # 获取当前时间
    now = datetime.now()

    # 检查传入的时间是否大于当前时间
    if open_time <= now:
        return create_response(
            ret=1,
            message="选择开奖时间必须大于当前时间",
        )

    # 检查传入的时间是否小于五分钟
    if open_time - now < timedelta(minutes=5):
        return create_response(
            ret=1,
            message="你选择的开奖时间太近了，请选择大于5分钟的时间",
        )

    print(open_time)

    try:
        lottery = await RewardTable.create(
            uid=item.uid,
            gid=item.gid,
            title=item.title,
            content=item.content,
            join_number=item.join_number,
            type=item.type,
            open_time=item.open_time,
            win_number=item.win_number,
            status=1
        )
    except OperationalError as e:
        logger.error(f'创建抽奖失败: {e}')
        return create_response(
            ret=1,
            message="数据库操作失败，请稍后再试，或请联系鹅子处理",
        )

    if lottery:
        msg = (
            f' 抽奖创建成功\n',
            f'抽奖标题: {item.title}\n',
            f'抽奖内容: \n{item.content}' if item.content else '',
            f'抽奖类型: {"按时间开奖" if item.type == 0 else "按人数开奖"}\n',
            f'参与人数: {item.join_number}\n' if item.type == 1 else '',
            f'开奖时间: {item.open_time}\n',
            f'参与抽奖请回复 "参与抽奖"',
        )
        at = MessageSegment.at(user_id=int(item.uid))

        try:
            await bot.send_group_msg(group_id=int(item.gid), message=Message(at + msg))
        except Exception as e:
            logger.error(f'发送抽奖消息失败: {e}')
            return create_response(
                ret=0,
                message="发送抽奖消息失败，但是抽奖创建成功，去群里告知大家吧！",
            )
        return create_response(
            ret=0,
            message="创建抽奖成功，页面可以关闭了",
            data=item
        )

    return create_response(
        ret=1,
        message="数据库操作失败，请稍后再试，或请联系鹅子处理",
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
