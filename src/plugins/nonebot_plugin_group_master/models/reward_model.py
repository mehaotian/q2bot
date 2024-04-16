import random
import string

from pydantic import BaseModel
from datetime import date, datetime, timedelta

from tortoise import fields
from tortoise.models import Model

from nonebot.log import logger
from .user_model import UserTable


class RewardTable(Model):
    """
    发起抽奖记录表
    """
    # 自增 ID (Primary key)
    id = fields.IntField(pk=True, generated=True)
    # 发起用户id
    uid = fields.CharField(max_length=255)
    # 发起用户所在群
    gid = fields.CharField(max_length=255)
    # 抽奖标题
    title = fields.CharField(max_length=255)
    # 抽奖内容
    content = fields.TextField()
    # 参与人数
    join_number = fields.IntField(default=0)

    # 抽奖类型 0 按时间开奖 1 按人数开奖
    type = fields.IntField(default=0)
    # 开奖时间 ，如果type 为1 ,未满足时按开奖时间
    open_time = fields.DatetimeField(null=True)
    # # 开奖人数
    # open_number = fields.IntField(default=0)

    # 中奖份数
    win_number = fields.IntField(default=0)
    # 抽奖状态 ，0 未开始，1 进行中，2 已结束
    status = fields.IntField(default=0)

    # 创建时间
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "reward_table"
        table_description = "发起抽奖记录表"  # 可选

    @classmethod
    async def create_reward(cls, uid: str, gid: str) -> list:
        """
        创建抽奖
        """
        # 生成一个6位的数字+字母的码，用于抽奖链接
        code = ''.join(random.choice(string.ascii_letters + string.digits)
                       for _ in range(6))
        user = await UserTable.filter(user_id=uid, group_id=gid).first()
        if user:
            user.login_key = code
            await user.save(update_fields=['login_key'])

        return user
