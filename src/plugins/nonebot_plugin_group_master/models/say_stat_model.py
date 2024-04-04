from pydantic import BaseModel
from datetime import date, datetime, timedelta

from tortoise import fields
from tortoise.models import Model

from nonebot.log import logger


class SayStatTable(Model):
    """
    逼王获取规则，每天凌晨0点统计
    如果当日发送消息数最多，且大于等于5条，则为逼王
    1. 获取当日发送消息数最多的用户
    2. 判断是否大于等于5条
    3. 每天只有一条数据，凌晨会统计前一天的逼王
    """
    # 自增 ID (Primary key)
    id = fields.IntField(pk=True, generated=True)
    # 用户id
    uid = fields.IntField()

    # 最长蝉联时间
    bking_time = fields.IntField(default=0)

    # 最后蝉联时间
    bking_last_time = fields.DatetimeField(auto_now=True)

    # 创建时间
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "say_stat_table"
        table_description = "逼王统计表"  # 可选

    @classmethod
    async def save_bking(cls, uid):
        """
        保存统计数据

        参数：
            - uid: 用户唯一ID
        """
        # 获取今天的日期
        today = datetime.now().date()
        # 获取昨天的日期
        yesterday = today - timedelta(days=1)
        # 获取明天的日期
        tomorrow = today + timedelta(days=1)

        # 查询昨天逼王统计数据
        bking_data = await cls.query_bking(yesterday, today)

        # 查询今天逼王统计数据
        today_bking_data = await cls.query_bking(today, tomorrow)

        # 如果今天不存在逼王数据
        if not today_bking_data:
            today_bking_data = await cls.create(uid=uid)

        # 查看是否有逼王数据
        print('bking_data', bking_data)

        if bking_data:
            bking_time = bking_data.bking_time
            # 查看今天逼王与昨天是否同一个人
            if bking_data.uid == uid:
                # 蝉联天数 + 1
                today_bking_data.bking_time = bking_time + 1
                await today_bking_data.save(update_fields=['bking_time'])

        return bking_data

    @classmethod
    async def query_bking(cls, start_time, end_time):
        """
        查询是否是逼王

        参数：
            - uid: 用户唯一ID
        """
        # 查询今天逼王
        bking_data = await cls.filter(created_at__gte=start_time, created_at__lt=end_time).first()

        return bking_data
