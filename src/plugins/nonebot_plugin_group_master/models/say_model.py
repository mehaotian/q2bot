import datetime
import os
from pydantic import BaseModel

from random import randint
from datetime import date, timedelta, datetime

from tortoise import fields
from tortoise.models import Model

from nonebot.log import logger


class sayData(BaseModel):
    """
    签到数据
    """


class SayTable(Model):
    # 自增 ID (Primary key)
    id = fields.IntField(pk=True, generated=True)
    # 来自UserTable的外键，关联具体用户
    user = fields.ForeignKeyField(
        'default.UserTable', related_name='says', on_delete=fields.CASCADE)
    # 文字消息的发送次数
    text_count = fields.IntField(default=0)
    # 图片消息的发送次数
    image_count = fields.IntField(default=0)
    # 表情消息的发送次数
    face_count = fields.IntField(default=0)
    # 回复别人消息的次数
    reply_count = fields.IntField(default=0)
    # @别人的次数
    at_count = fields.IntField(default=0)
    # 总条数，每发送一条记录一次
    total_count = fields.IntField(default=0)
    # 撤回次数
    recall_count = fields.IntField(default=0)
    # 创建时间
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "say_table"
        table_description = "会话表"  # 可选

    @classmethod
    async def save_says(cls, uid, data) -> "SayTable":
        """
        保存回话数据，每小时保存一次
        :param uid: 用户唯一ID
        :param data: 数据
        """
        print('uid',uid)
        print('data',data)
        # 获取当前时间，并调整到下一个整点
        now = datetime.now()
        next_hour = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
        # 获取当前小时的开始时间
        current_hour = now.replace(minute=0, second=0, microsecond=0)

        print(current_hour)
        # 查找指定用户在当前小时内的数据
        say = await cls.filter(user_id=uid, created_at__gte=current_hour, created_at__lt=next_hour).first()
        print(say)
        # # 如果没有数据则新增
        if not say:
            say = await cls.create(user_id=uid, **data)
        else:
            # 获取 data 中所有的keys
            keys = data.keys()
            new_data = {}
            print('keys',keys)
            # 更新数据
            for key in keys:
                # 获取data中的值
                value = data.get(key)
                # 获取say中的值
                say_value = getattr(say, key)
                # 更新数据
                new_data[key] = value + say_value

            await cls.filter(id=say.id).update(**new_data)

    @classmethod
    async def query_says(cls, uid, start_time) -> "SayTable":
        """
        查询用户在指定时间段内的数据
        :param uid: 用户唯一ID
        :param start_time: 开始时间
        :param end_time: 结束时间
        """
        # 结束时间为当前时间
        end_time = datetime.now()

        return await cls.filter(user_id=uid, created_at__gte=start_time, created_at__lt=end_time).all()
      
        