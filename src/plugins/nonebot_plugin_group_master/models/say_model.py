import datetime
from pydantic import BaseModel
from nonebot.log import logger

from random import randint
from datetime import date, timedelta, datetime
from collections import defaultdict
from tortoise import fields
from tortoise.models import Model

from .user_model import UserTable


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
        logger.debug('uid', uid)
        # 获取当前时间，并调整到下一个整点
        now = datetime.now()
        next_hour = (now + timedelta(hours=1)).replace(minute=0,
                                                       second=0, microsecond=0)
        # 获取当前小时的开始时间
        current_hour = now.replace(minute=0, second=0, microsecond=0)

        # 查找指定用户在当前小时内的数据
        say = await cls.filter(user_id=uid, created_at__gte=current_hour, created_at__lt=next_hour).first()
        # # 如果没有数据则新增
        if not say:
            say = await cls.create(user_id=uid, **data)
        else:
            # 获取 data 中所有的keys
            keys = data.keys()
            new_data = {}
            print('keys', keys)
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
    async def query_says(cls, uid, start_time, end_time) -> "SayTable":
        """
        查询用户在指定时间段内的数据
        :param uid: 用户唯一ID
        :param start_time: 开始时间
        :param end_time: 结束时间
        """
        # 结束时间为当前时间
        return await cls.filter(user_id=uid, created_at__gte=start_time, created_at__lt=end_time).all()

    @classmethod
    async def get_the_charts(cls, group_id, start_time,end_time) -> dict:
        """
        获取指定群指定时间之后所有用户的排行信息
        """
        # 获取一个时间段
        # 获取所有满足条件的记录
        says = await SayTable.filter(created_at__gte=start_time,created_at__lte=end_time).values()

        # 使用字典进行分组
        grouped_says = defaultdict(list)
        for say in says:
            grouped_says[say['user_id']].append(say)

        # 对每个用户的记录进行聚合
        aggregated_says = []
        for user_id, user_says in grouped_says.items():
            total_image_count = sum(say['image_count'] for say in user_says)
            total_face_count = sum(say['face_count'] for say in user_says)
            total_reply_count = sum(say['reply_count'] for say in user_says)
            total_at_count = sum(say['at_count'] for say in user_says)
            total_text_count = sum(say['text_count'] for say in user_says)
            total_count = sum(say['total_count'] for say in user_says)
            total_recall_count = sum(say['recall_count'] for say in user_says)

            total = total_image_count + total_face_count + total_reply_count + total_at_count + total_text_count +total_recall_count

            # 获取用户
            user = await UserTable.get(id=user_id)
            user_group_id = user.group_id
            # 筛选同一个群
            if user_group_id == group_id:
                user_dict = {k: v for k, v in user.__dict__.items()
                             if not k.startswith('_')}
                
                aggregated_says.append({
                    'user_id': user_id,
                    'total_image_count': total_image_count,
                    'total_face_count': total_face_count,
                    'total_reply_count': total_reply_count,
                    'total_at_count': total_at_count,
                    'total_text_count': total_text_count,
                    'total_count': total_count,
                    'total_recall_count': total_recall_count,
                    'total': total,
                    "users": user_dict
                })

        # 排序，从大到小
        aggregated_says.sort(key=lambda x: x['total'] , reverse=True)

        return aggregated_says
