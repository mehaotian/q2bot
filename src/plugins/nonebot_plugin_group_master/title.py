# python3
# -*- coding: utf-8 -*-
# @Time    : 2024-3-30 00:39
# @Author  : mehaoitan
# @Email   :  490272692@qq.com
# @File    : say.py
# @description: 修改头衔
# @Software: VS Code

import re
from nonebot import (
    on_command
)
from nonebot.adapters.onebot.v11 import (
    Bot,
    GroupMessageEvent,
)
from nonebot.log import logger


from .serivce.user_source import change_s_title

from .utils import MsgText, At
from .config import global_config
# 获取超级管理员
su = global_config.superusers
# 查询自己指定时间逼话榜详情
title = on_command('头衔', priority=1, block=True)

@title.handle()
async def change_title(bot: Bot, event: GroupMessageEvent):
    """
    /头衔 @user  xxx  给某人头衔
    """
    # msg = str(event.get_message())
    msg = MsgText(event.json())
    s_title = msg.replace(' ', '').replace('头衔', '', 1)
    sb = At(event.json())
    gid = event.group_id
    uid = event.user_id
    if not sb or (len(sb) == 1 and sb[0] == uid):
       msg = await change_s_title(bot, gid, uid, s_title)
       await bot.send(event=event, message=msg)
    elif sb:
        if 'all' not in sb:
            if uid in su or (str(uid) in su):
                for qq in sb:
                    await change_s_title(bot, gid, int(qq), s_title)
            else:
                # await fi(matcher, '超级用户才可以更改他人头衔，更改自己头衔请直接使用【头衔 xxx】')
                await bot.send(event=event, message='超级用户才可以更改他人头衔，更改自己头衔请直接使用【/头衔 xxx】')
        else:
            # await fi(matcher, '不能含有@全体成员')
            await bot.send(event=event, message='不能含有@全体成员')

