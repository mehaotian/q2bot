#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File    :   game_hook.py
@Time    :   2024/04/22 18:52:39
@Author  :   haotian 
@Version :   1.0
@Desc    :   游戏主体钩子数据逻辑处理
'''

from nonebot.adapters.onebot.v11 import (
    Bot,
    Message,
    GroupMessageEvent,
    MessageSegment,
)

from ..models.zhiyin_game import ZyGameTable
from ..models.zhiyin_player import ZyPlayerTable


class GameHook:
    def __init__(self):
        pass

    @classmethod
    async def switch_game(cls, gid: str, type: int) -> Message:
        """
        开关游戏
        参数：
            - gid: 群号
        返回：
            - Message
        """
        # 获取游戏是否存在
        record = await ZyGameTable.get_game(gid)
        print(record.status)

        if not record:
            # 创建游戏
            await ZyGameTable.create(group_id=gid, status=1)
            record = await ZyGameTable.get_game(gid)

        if record.status == type:
            msg = "只因大冒险已经开启了,请勿重复操作" if type == 1 else "只因大冒险已经关闭了，请勿重复操作"
            return Message(MessageSegment.text(msg))

        record.status = type
        await record.save(update_fields=['status'])
        if type == 0:
            msg = "只因大冒险已关闭"
        else:
            msg = "只因大冒险已开启"

        return Message(MessageSegment.text(msg))

    @classmethod
    async def join_game(cls, gid: str, uid: str) -> Message:
        """
        加入游戏
        参数：
            - gid: 群号
        返回：
            - Message
        """
        # 获取游戏是否存在
        # is_game = await cls.check_game(gid)
        if not (game := await cls.check_game(gid)):
            msg = "只因大冒险未开启"
            return Message(msg)
        else:
            # 获取玩家
            player = await ZyPlayerTable.get_player(game_id=game.id, gid=gid, uid=uid)
            if player.status == 1:
                return Message(MessageSegment.text("你已身在局中，无需再次入局！"))

            player.status = 1
            await player.save(update_fields=['status'])
            return Message(MessageSegment.text("以身入局，胜天半子，只因大冒险开启!!"))

    async def check_game(gid: str) -> bool:
        """
        检查游戏是否开启
        参数：
            - gid: 群号
        返回：
            - bool
        """
        record = await ZyGameTable.get_game(gid)
        if record and record.status == 1:
            return record
        return None

    @classmethod
    async def check_player(cls, gid: str, uid: str) -> bool:
        """
        检查玩家是否在游戏中
        参数：
            - gid: 群号
            - uid: 用户 ID
        返回：
            - bool
        """
        game = await cls.check_game(gid)
        if not game:
            return False
        player = await ZyPlayerTable.get_player(game_id=game.id, gid=gid, uid=uid)
        if player and player.status == 1:
            return True
        return False
    
    async def have_player(bot: Bot, event: GroupMessageEvent):
        """
        是否加入游戏
        参数：
            - bot: Bot
            - event: GroupMessageEvent
        """
        gid = str(event.group_id)
        uid = str(event.user_id)
        return await GameHook.check_player(gid, uid)
    
