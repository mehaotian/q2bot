import random
import string

from pydantic import BaseModel

from tortoise import fields
from tortoise.models import Model

from nonebot.log import logger
from .reward_model import RewardTable
from .user_model import UserTable


class JoinLotteryTable(Model):
    """
    发起抽奖记录表
    """
    # 自增 ID (Primary key)
    id = fields.IntField(pk=True, generated=True)
    # 外键与 reward 关联
    reward = fields.ForeignKeyField(
        'default.RewardTable', related_name='reward', on_delete=fields.CASCADE)
    user = fields.ForeignKeyField(
        'default.UserTable', related_name='user', on_delete=fields.CASCADE)
    # 参与用户id，与 user 关联
    # uid = fields.IntField(default=0)
    # 状态：0 未中奖 1 已中奖 2 未中奖，3 已领奖 5 已取消 6 禁止参与
    status = fields.IntField(default=0)
    # 中奖码
    win_code = fields.CharField(max_length=255, default="")
    # 中奖 cdk
    cdk = fields.CharField(max_length=255, default="")
    # 描述，如果被禁止参与 ，需要给出理由
    desc = fields.TextField(default="")

    # 创建时间
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "join_lottery_table"
        table_description = "加入抽奖表"  # 可选

    @classmethod
    async def join(cls, reward_id: int, uid: str) -> int:
        """
        参与抽奖
            返回 1 已经参与过 2 参与成功 3 参与失败
        """
        # 获取当前用户时候中奖
        user_record = await cls.filter(user_id=uid, reward_id=reward_id).first()

        if user_record:
            return 1
        else:
            # 获取抽奖信息
            reward = await RewardTable.get(id=reward_id)
            try:
                # 创建抽奖记录
                await cls.create(reward=reward, user_id=uid)
            except Exception as e:
                logger.error(f"创建抽奖记录失败：{e}")
                return 3

            return 2

    @classmethod
    async def get_user_list(cls, rid: int) -> list:
        """
        获取当前抽奖参与用户
        """
        user_list = await cls.filter(reward_id=rid).values()
        return user_list

    @classmethod
    async def get_user(cls, rid: int) -> dict:
        """
        获取当前抽奖参与用户
        """
        lottery_users = await JoinLotteryTable.filter(reward_id=rid).prefetch_related("user")

        # 创建一个列表来存储用户信息
        users_info = []

        # 对于每个抽奖用户，获取他们的 UserTable 记录
        for lottery_user in lottery_users:
            user_info = await UserTable.get(id=lottery_user.user_id)
            # user_dict = {k: v for k, v in user_info.__dict__.items()
            #              if not k.startswith('_')}
            # lottery_dict = {
            #     k: v for k, v in lottery_user.__dict__.items() if not k.startswith('_')}
            # lottery_dict['user'] = user_dict
            lottery_user.user = user_info
            users_info.append(lottery_user)

        return users_info
