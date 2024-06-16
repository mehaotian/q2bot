#!/usr/bin/env python
# -*- coding: utf-8 -*-
#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File    :   zhiyin_game.py
@Time    :   2024/06/14 13:20:29
@Author  :   haotian 
@Version :   1.0
@Desc    :   只因大冒险游戏模型
'''


from tortoise import fields
from tortoise.models import Model
from tortoise.exceptions import DoesNotExist
from nonebot.log import logger


class ZyGameTable(Model):
    # 自增 ID (Primary key)
    id = fields.IntField(pk=True, generated=True)
    # 用户 ID
    user_id = fields.CharField(max_length=255, default="")
    # 群组 ID
    group_id = fields.CharField(max_length=255, default="")
    # 游戏天数
    days = fields.IntField(default=0)
    # 游戏人数
    players_count = fields.IntField(default=0)

    # 游戏状态 , 0 游戏未进行 1 游戏进行中
    status = fields.IntField(default=0)


    # 创建时间
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "zhiyin_game_table"
        table_description = "只因大冒险游戏表"
        
    @classmethod
    async def create_game(cls, gid: str):
        """
        创建默认游戏游戏
        参数：
            - gid: 群号
        返回：
            - CatGameTable
        """
        try:
            record = await cls.create(group_id=gid,status=0)
            return record
        except Exception as e:
            logger.error(f"创建游戏失败：{e}")
            return None

    @classmethod
    async def get_game(cls, gid: str):
        """
        获取游戏
        参数：
            - gid: 群号
        返回：
            - CatGameTable
        """
        try:
            record = await cls.get(group_id=gid)
            return record            
        except DoesNotExist:
            return None

    