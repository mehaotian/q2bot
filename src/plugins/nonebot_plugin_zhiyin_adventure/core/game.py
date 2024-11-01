#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File    :   game.py
@Time    :   2024/04/18 00:33:47
@Author  :   haotian 
@Version :   1.0
@Desc    :   游戏主体
'''
from nonebot import (
    on_fullmatch,
    on_regex,
    on_message
)
from nonebot.adapters.onebot.v11 import (
    Bot,
    GroupMessageEvent,
)
from nonebot.matcher import Matcher
from nonebot.rule import to_me
from nonebot.log import logger

from ..models import ZyPlayerTable
from ..hooks.game_hook import GameHook
from ..hooks.player_hook import PlayerHook

# 创建游戏
gameReg = r"^\s*(开启|关闭)只因大冒险\s*$"
game = on_regex(gameReg, rule=to_me(), priority=20, block=True)

# 加入游戏
join_game = on_fullmatch("加入只因世界", rule=to_me(), priority=20, block=True)


# 监听用户消息
run_game = on_message(priority=0, rule=GameHook.have_player, block=False)


@game.handle()
async def game_handle(bot: Bot, event: GroupMessageEvent):
    gid = str(event.group_id)

    msgdata = event.get_message()
    msgdata = msgdata.extract_plain_text().strip()

    # 如果包含 开启
    if "开启" in msgdata:
        msgdata = 1
    else:
        msgdata = 0
    print(msgdata)
    msg = await GameHook.switch_game(gid, msgdata)

    await bot.send(event=event, message=msg)


@join_game.handle()
async def join_game_handle(bot: Bot, matcher: Matcher, event: GroupMessageEvent):
    gid = str(event.group_id)
    uid = str(event.user_id)
    msg = await GameHook.join_game(gid=gid, uid=uid)

    await matcher.send(message=msg, at_sender=True)


@run_game.handle()
async def run_game_handle(bot: Bot, matcher: Matcher, event: GroupMessageEvent):
    uid = str(event.user_id)
    gid = str(event.group_id)
    game = await GameHook.check_game(str(event.group_id))
    player_data = await ZyPlayerTable.get_player(game_id=game.id, gid=gid, uid=uid)

    player = PlayerHook(cmd=matcher,bot=bot, event=event, game=game, player=player_data)
    # 运行游戏,角色金币 经验等增加
    await player.run()
