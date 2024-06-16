#!/usr/bin/env python
# -*- coding: utf-8 -*-
#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File    :   zhiyin_player.py
@Time    :   2024/06/14 13:20:47
@Author  :   haotian 
@Version :   1.0
@Desc    :   只因大冒险玩家模型
'''

from tortoise import fields
from tortoise.models import Model
from tortoise.exceptions import DoesNotExist

from nonebot.log import logger


class ZyPlayerTable(Model):
    # 自增 ID (Primary key)
    id = fields.IntField(pk=True, generated=True)
    # 游戏 ID
    game = fields.ForeignKeyField(
        'zhiyindb.ZyGameTable', related_name='game')
    # 用户 ID,外键关联用户
    user_id = fields.CharField(max_length=255, default="")
    # 群组 ID
    group_id = fields.CharField(max_length=255, default="")

    # 只因名字
    z_name = fields.CharField(max_length=255, default="")
    # 只因大小
    z_size = fields.IntField(default=1)
    # 只因等级
    z_level = fields.IntField(default=1)
    # 只因经验
    z_exp = fields.IntField(default=0)
    # 只因币
    z_coin = fields.IntField(default=0)
    # 只因体力
    z_power = fields.IntField(default=0)

    # 只因攻击
    z_attack = fields.IntField(default=0)
    # 只因防御
    z_defense = fields.IntField(default=0)
    # 只因速度
    z_speed = fields.IntField(default=0)
    # 只因暴击
    z_crit = fields.IntField(default=0)
    # 只因命中
    z_hit = fields.IntField(default=0)
    # 只因闪避
    z_dodge = fields.IntField(default=0)
    # 只因技能
    z_skill = fields.IntField(default=0)
    # 只因装备,额外加成
    z_equipment = fields.IntField(default=0)

    # 只因状态
    z_status = fields.IntField(default=0)

    # 只因称号, 额外加成
    z_title = fields.CharField(max_length=255, default="")

    # 玩家状态 0 未加入 1 游戏中
    status = fields.IntField(default=0)

    # 创建时间
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "zhiyin_player_table"
        table_description = "只因大冒险玩家表"

    @classmethod
    async def get_player(cls, game_id: str, gid: str, uid: str) -> 'ZyPlayerTable':
        """
        获取玩家
        参数：
            - gid: 群号
            - uid: 用户 ID
        返回：
            - ZyPlayerTable
        """
        # try:
        #     return await cls.get(game_id=game_id, group_id=gid, user_id=uid)
        # except DoesNotExist:
        #     # 创建玩家
        #     return await cls.create(game_id=game_id, group_id=gid, user_id=uid)
        record, _ = await cls.get_or_create(game_id=game_id, group_id=gid, user_id=uid)
        return record
