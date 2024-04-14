# python3
# -*- coding: utf-8 -*-
# @Time    : 2024-3-30 00:39
# @Author  : mehaoitan
# @Email   :  490272692@qq.com
# @File    : say.py
# @description: steam 操作
# @Software: VS Code

import re
from nonebot import (
    on_command
)
from nonebot.adapters.onebot.v11 import (
    Bot,
    MessageSegment,
    GroupMessageEvent,
)
from nonebot.log import logger
from .utils import MsgText, At
from .serivce.steam_source import bind_steam_user, get_steam_id, query_steam_user

# 查询自己指定时间逼话榜详情
steam = on_command('steam', priority=1, block=True)


@steam.handle()
async def steam_handle(bot: Bot, event: GroupMessageEvent):
    msg = MsgText(event.json())
    params = msg.split(" ")
    gid = str(event.group_id)
    uid = str(event.user_id)
    sender = event.sender

    # 如果第一个不存在或第一个参数不是 /steam 则返回错误
    if not params or params[0] != '/steam':
        return await bot.send(event, "指令错误, 示例：/steam [操作指令] [具体执行]")

    # 一个参数直接查询信息
    if len(params) == 1:
        await bot.send(event, "steam 信息查询中，请稍后")
        msg = await query_steam_user(user_id=uid)
        return await bot.send(event=event, message=msg)

    # 指令
    command = params[1]
    # 合法指令
    command_list = ['绑定', '查询', '更新', 'help', '帮助']
    if command not in command_list:
        return await bot.send(event, f"操作指令错误，目前只支持：{command_list}")

    if command == 'help' or command == '帮助':
        msg = (
            f"Steam 指令帮助：\n"
            f"1. 绑定 Steam 好友代码，所有后续命令都需要本次操作\n"
            f"  - /steam 绑定 [steam 好友代码]\n"
            f"2. Steam 基本信息查询，如 好友代码，邀请链接等\n"
            f" - /steam\n"
        )
        return await bot.send(event=event, message=msg)

    # 查询
    if command == '绑定':
        # return await bot.send(event, "查询")

        steamid = get_steam_id(params[2])

        print('steamid', steamid)

        if not steamid:
            return await bot.send(event=event, message=MessageSegment.at(uid) + " Steam 好友代码错误")

        msg = await bind_steam_user(group_id=gid, user_id=uid, sender=sender, steamid=steamid)

        await bot.send(event=event, message=msg)

    print(params)
    # s_title = msg.replace(' ', '').replace('头衔', '', 1)
    # sb = At(event.json())
    # gid = event.group_id
    # uid = event.user_id
