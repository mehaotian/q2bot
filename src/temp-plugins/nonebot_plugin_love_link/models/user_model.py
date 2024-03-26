import os
from pydantic import BaseModel

from random import randint
from datetime import date, timedelta
import requests

from tortoise import fields
from tortoise.models import Model

from nonebot.log import logger


from ..config import BASE, MAX_LUCKY, MULTIPLIER ,cache_directory


# 导入插件方法
from nonebot_plugin_tortoise_orm import add_model

#  添加模型
add_model("src.plugins.nonebot_plugin_love_link.models.user_model")


def download_image(url, cache_path):
    """
    下载文件并缓存
    """
    # 如果缓存目录不存在，则创建
    if not os.path.exists(cache_directory):
        os.makedirs(cache_directory)
    logger.debug(f"缓存文件不存在: {os.path.exists(cache_path)}")
    if not os.path.exists(cache_path):
        logger.debug(f"缓存文件不存在: {cache_path}")
        # 否则下载远程图片，并保存到缓存目录
        response = requests.get(url)
        if response.status_code == 200:
            with open(cache_path, "wb") as file:
                file.write(response.content)
        else:
            # 处理下载失败的情况
            return None

class SignData(BaseModel):
    """
    签到数据
    """

    # 累计金币
    all_gold: int
    # 今日金币
    today_gold: int
    # 累计签到次数
    sign_times: int
    # 连续签到次数
    streak: int
    # 累计魅力值
    all_charm: int
    # 今日魅力值
    today_charm: int


class UserTable(Model):
    # 自增 ID (Primary key)
    id = fields.IntField(pk=True, generated=True)
    # 用户 ID
    user_id = fields.IntField()
    # 群组 ID
    group_id = fields.IntField()
    # 昵称
    nickname = fields.CharField(max_length=255, default="")
    # 头像
    avatar = fields.CharField(max_length=255, default="")
    # 魅力值
    charm = fields.IntField(default=0)
    # 金币
    gold = fields.IntField(default=0)
    # 登录时间
    sign_times = fields.IntField(default=0)
    # 最后登录时间 
    last_sign = fields.DateField(default=date(2000, 1, 1))
    # 连续登录天数
    streak = fields.IntField(default=0)
    # 背景图地址
    bg_img = fields.CharField(max_length=255, default="")

    class Meta:
        table = "user_table"
        table_description = " 用户表"  # 可选 

    @classmethod
    async def init_user(cls, user_id: int, group_id: int, sender) -> "UserTable":
        record, _ = await UserTable.get_or_create(
            user_id=user_id,
            group_id=group_id,
        )
        # 假设 sender 可以是对象或字典
        if isinstance(sender, dict):
          # 如果 sender 是字典，直接从字典中获取 'card' 或 'nickname' 的值
          card_value = sender.get('card', None)
          nickname_value = sender.get('nickname', None)
        else:
          # 如果 sender 是对象，尝试从对象的属性中获取 'card' 或 'nickname' 的值
          card_value = getattr(sender, 'card', None)
          nickname_value = getattr(sender, 'nickname', None)
        # 如果不存在群名片，在使用qq昵称
        record.nickname = card_value or nickname_value
        record.avatar = f"https://q1.qlogo.cn/g?b=qq&nk={user_id}&s=640"
        await record.save(update_fields=["nickname", "avatar"])

        # 用户头像本地名称
        avator_name = f'avator_{user_id}.jpg'
        cache_path = os.path.join(cache_directory, avator_name)
        download_image(record.avatar, cache_path)

        return record

    @classmethod
    async def sign_in(
        cls,
        user_id: int,
        group_id: int,
    ) -> SignData:
        """
        :说明: `sign_in`
        > 添加签到记录

        :参数:
          * `user_id: int`: 用户ID
          * `group_id: int`: 群ID

        :返回:
          - `SignData`: 签到数据
        """
        record, _ = await UserTable.get_or_create(
            user_id=user_id,
            group_id=group_id,
        )

        today = date.today()
        if record.last_sign == (today - timedelta(days=1)):
            record.streak += 1

        record.last_sign = today

        # 金币增加
        gold_base = BASE + randint(-MAX_LUCKY, MAX_LUCKY)
        """基础金币"""

        today_gold = round(gold_base * (1 + record.streak * MULTIPLIER))
        """计算连续签到加成"""

        record.gold += today_gold
        if record.gold < 0:
            record.gold = 0

        record.sign_times += 1

        # 魅力值
        charm_base = 10 + randint(-MAX_LUCKY, MAX_LUCKY)
        """基础魅力值"""
        record.charm += charm_base
        if record.charm < 0:
            record.charm = 0

        await record.save(update_fields=["last_sign", "gold", "sign_times", "streak", "charm"])
        return SignData(
            all_gold=record.gold,
            today_gold=today_gold,
            sign_times=record.sign_times,
            streak=record.streak,
            all_charm=record.charm,
            today_charm=charm_base,
        )

    @classmethod
    async def get_last_sign(cls, user_id: int, group_id: int) -> date:
        """
        :说明: `get_last_sign`
        > 获取最近的签到日期

        :参数:
          * `user_id: int`: 用户ID
          * `group_id: int`: 群ID

        :返回:
          - `date`: 签到日期
        """
        record, _ = await UserTable.get_or_create(
            group_id=group_id,
            user_id=user_id,
        )
        return record.last_sign

    @classmethod
    async def get_gold(cls, user_id: int, group_id: int) -> int:
        """
        :说明: `get_gold`
        > 获取金币

        :参数:
          * `user_id: int`: 用户ID
          * `group_id: int`: 群ID

        :返回:
          - `int`: 当前金币数量
        """
        record, _ = await UserTable.get_or_create(
            group_id=group_id,
            user_id=user_id,
        )
        return record.gold

    @classmethod
    async def adjust_gold(cls, adjust: int, user_id: int, group_id: int) -> int:
        """
        :说明: `adjust_gold`
        > 调整金币

        :参数:
          * `adjust: int`: 调整金币数量 为正 则添加 为负 则减少
          * `user_id: int`: 用户ID
          * `group_id: int`: 群ID

        :返回:
          - `int`: 当前金币数量
        """
        record, _ = await UserTable.get_or_create(
            group_id=group_id,
            user_id=user_id,
        )
        record.gold += adjust
        await record.save(update_fields=["gold"])
        return record.gold
