# python3
# -*- coding: utf-8 -*-
# @Time    : 2024-3-30 00:39
# @Author  : mehaoitan
# @Email   :  490272692@qq.com
# @File    : say.py
# @description: 抽奖
# @Software: VS Code

from nonebot import (
    on_command,
    on_fullmatch
)
from nonebot.adapters.onebot.v11 import (
    Bot,
    MessageSegment,
    GroupMessageEvent,
)
from nonebot.log import logger
from .serivce.lottery_source import publish_lottery
from .utils import MsgText, At

# 查询自己指定时间逼话榜详情
lottery = on_command('抽奖', priority=1, block=True)
participate_in = on_fullmatch('参与抽奖', priority=1, block=True)

@lottery.handle()
async def lottery_handle(bot: Bot, event: GroupMessageEvent):
    """
    发布抽奖
        - /抽奖   # 查询所有参与且正在进行的抽奖
        - /抽奖 发布  # 发布抽奖 ，返回抽奖发布地址

    """
    msg = MsgText(event.json())
    params = msg.split(" ")
    gid = str(event.group_id)
    uid = str(event.user_id)

    # 如果第一个不存在或第一个参数不是 /抽奖 则返回错误
    if not params or params[0] != '/抽奖':
        return await bot.send(event, "指令错误, 示例：/抽奖 [操作指令]")
    
    # 一个参数直接查询信息
    if len(params) == 1:
        return await bot.send(event, "抽奖信息查询中，请稍后")
    
    # 指令
    command = params[1]
    # 合法指令
    command_list = ['发布']
    if command not in command_list:
        return await bot.send(event, f"抽奖操作指令错误，目前只支持：{command_list}")

    if command == 'help' or command == '帮助':
        msg = (
            f"抽奖指令帮助：\n"
            f"1. 查询已经参与且在进行中的抽奖\n"
            f"  - /抽奖\n"
            f"2. 发布抽奖\n"
            f" - /抽奖 发布\n"
        )
        return await bot.send(event=event, message=msg)

    # 查询
    if command == '发布':
        msg = await publish_lottery(uid=uid, gid=gid)
        return await bot.send(event, msg)
        

@participate_in.handle()
async def participate_in_handle(bot: Bot, event: GroupMessageEvent):
    pass