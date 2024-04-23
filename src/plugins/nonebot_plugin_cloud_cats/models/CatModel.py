#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File    :   CatGameModels.py
@Time    :   2024/04/17 21:38:25
@Author  :   haotian 
@Version :   1.0
@Desc    :   猫咪模型
'''

# from pydantic import BaseModel

import random
from tortoise import fields
from tortoise.models import Model

from nonebot.log import logger


class CatTable(Model):
    # 自增 ID (Primary key)
    id = fields.IntField(pk=True, generated=True)
     # 外键关联猫咪
    game = fields.ForeignKeyField(
        'catdb.CatGameTable', related_name='game', on_delete=fields.CASCADE)
    # 群组 ID ，使用str ，int容易超过范围
    group_id = fields.CharField(max_length=255, default="")
    # 猫咪名称
    name = fields.CharField(max_length=255, default="")
    # 猫咪年龄
    age = fields.IntField(default=0)
    # 猫咪体重
    weight = fields.IntField(default=0)
    # 猫咪形象
    image = fields.CharField(max_length=255, default="")
    # 猫咪性格 ，0 安静 1 活泼 2 乖巧 3 调皮 4 狡猾 5 懒惰 6 爱睡觉 7 爱吃 8 爱玩耍 9 爱撒娇
    character = fields.IntField(default=0)
    # 猫咪品种
    breed = fields.CharField(max_length=255, default="")
    # 猫咪性别
    sex = fields.CharField(max_length=255, default="")
    # 猫咪状态 , 0 禁用中 1 游戏进行中 2 死亡
    status = fields.IntField(default=0)
   
    # 创建时间
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "cat_table"
        table_description = "猫咪表"

    @classmethod
    async def create_cat(cls, game_id: str,gid:str):
        """
        创建猫咪
        参数：
            - gid: 群号
        返回：
            - CatTable
        """
        try:
            record = await cls.create(game_id=game_id)

            # 群组 ID
            record.group_id = gid
            # 猫咪名称
            record.name = ""
            # 年龄
            record.age = 0
            # 体重 单位 克
            record.weight = 85
            # 形象
            record.image = ""
            # attributes = ['安静', '活泼', '乖巧', '调皮', '狡猾', '懒惰', '爱睡觉', '爱吃', '爱玩耍', '爱撒娇']
            # random_attribute = random.choice(attributes)
            random_number = random.randint(0, 9)
            # 性格
            record.character = random_number
            # 品种
            record.breed = ""
            # 性别
            sex_number = random.randint(0, 1)
            record.sex = sex_number

            # 状态
            record.status = 1
            await record.save(update_fields=['group_id','name','age','weight','image','character','breed','sex','status'])
            return record
        except Exception as e:
            logger.error(f"创建猫咪失败：{e}")
            return None
        
    @classmethod
    async def get_cat_list(cls, game_id: str):
        """
        获取猫咪列表
        参数：
            - gid: 群号
        返回：
            - list
        """
        record = await cls.filter(game_id=game_id).values()
        return record