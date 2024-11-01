#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File    :   player_flow.py
@Time    :   2024/06/21 16:09:14
@Author  :   haotian 
@Version :   1.0
@Desc    :   游戏玩家相关hook
'''
import random
from nonebot.adapters.onebot.v11 import (
    Bot,
    GroupMessageEvent,
)
from nonebot.matcher import Matcher


from ..models import ZyGameTable
from ..models import ZyPlayerTable
from ..config import plugin_config


class PlayerHook:
    bot: Bot = None
    event: GroupMessageEvent = None
    game = None
    group_id = ""
    user_id = ""
    game_id = ""

    def __init__(self, cmd: Matcher, bot: Bot, event: GroupMessageEvent, game: ZyGameTable, player: ZyPlayerTable):
        """
        注册用户，初始化玩家数据
        参数：
          - bot: Bot
          - event: GroupMessageEvent
        """
        self.cmd = cmd
        self.bot = bot
        self.event = event
        self.group_id = str(event.group_id)
        self.user_id = str(event.user_id)
        # 获取当前所在游戏数据
        self.game = game
        self.player = player

    async def run(self):
        """
        运行游戏
        """
        player = self.player
        z_base_gold = plugin_config.z_base_gold
        z_base_exp = plugin_config.z_base_exp

        # 加入一些随机性
        gold_increase = z_base_gold + random.randint(1, 10)  # 基础金币增加 0 到 3 的波动
        exp_increase = z_base_exp + random.randint(1, 5)    # 基础经验增加 0 到 5 的波动

        # 更新玩家金币和经验
        player.z_coin += gold_increase
        player.z_exp += exp_increase

        next_exp = self.total_exp_for_level(player.z_level)

        # 检查是否升级
        if player.z_exp >= next_exp:
            player.z_level += 1
            await self.cmd.send(message=f"恭喜你升级了，当前等级 {player.z_level}")

        next_exp = self.total_exp_for_level(player.z_level)
        await self.cmd.send(message=f"你获得了 {gold_increase} 金币和 {exp_increase} 经验，当前等级 {player.z_level}，升级还需 {player.z_exp}/{next_exp} 经验")
          
        await player.save(update_fields=['z_coin', 'z_exp', 'z_level'])

    def set_coin(self, coin: int = 0):
        """
        设置只因币
        参数：
          - coin: 金币数量
        """
        # pass
        print(self.player, coin)

    def total_exp_for_level(self, level: int):
        """
        计算达到某等级所需的总经验
        参数：
          - level: 等级
        返回：
          - 达到该等级所需的总经验
        """
        base_exp = 100  # 初始等级所需经验
        growth_rate = 1.1  # 每级递增系数
        total_exp = 0

        for lvl in range(1, level + 1):
            exp_for_current_level = base_exp * (growth_rate ** (lvl - 1))
            total_exp += int(exp_for_current_level)

        return total_exp
    
    def exp_to_next_level(self,lv: int):
        """
        计算到下一级所需的经验
        返回：
          - 当前等级进度（当前经验/到下一级经验）
          - 升级还需多少经验
        """
        # 当前等级所需总经验
        current_level_exp = self.total_exp_for_level(lv)
        # 下一等级所需总经验
        next_level_exp = self.total_exp_for_level(lv + 1)
        # 到下一级所需经验
        exp_for_next_level = next_level_exp - current_level_exp  

        return exp_for_next_level

    def update_length(self,player: ZyPlayerTable):
        """
        更新虚无坤长度
        参数：
          - player: 玩家数据
        """
        # 长度和等级挂钩，简单设定为每级加10单位长度
        player.length = player.level * 10
