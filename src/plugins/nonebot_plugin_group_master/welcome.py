# python3
# -*- coding: utf-8 -*-
# @Time    : 2024-3-30 00:39
# @Author  : mehaoitan
# @Email   :  490272692@qq.com
# @File    : welcome.py
# @description: 群签到相关
# @Software: VS Code


from nonebot import on_fullmatch, on_command, on
from nonebot.adapters.onebot.v11 import (
    Bot,
    Event,
    Message,
    GroupMessageEvent,
    MessageSegment
)
from nonebot.adapters import MessageTemplate
from nonebot.typing import T_State

from nonebot.log import logger
from .serivce.user_source import (
    create_user,
    handle_sign_in,
    handle_change_bg
)

# 指令集
commands = {
    "sign_in": "签到",
    "sign_in_bg": "签到背景",
}

# 签到
sign = on_fullmatch(commands["sign_in"], priority=5, block=False)
# 替换背景图
replace_bg = on_command(commands["sign_in_bg"], priority=5, block=False)


@sign.handle()
async def sign_in(bot: Bot, event: GroupMessageEvent):
    """
    签到
    """
    user_id = str(event.user_id)
    group_id = str(event.group_id)
    logger.debug(f"群 group_id: 用户 {user_id} 签到")
    msg = await handle_sign_in(user_id, group_id, event.sender)
    await bot.send(event=event, message=msg)


@replace_bg.handle()
async def _(bot: Bot, state: T_State, event: GroupMessageEvent):
    """
    替换背景图前置
    """
    user_id = str(event.user_id)
    group_id = str(event.group_id)
    at = MessageSegment.at(event.user_id)
    
    state['user_id'] = user_id
    state['group_id'] = group_id
    state['reply_msg'] = Message(f'{at} 请发送一张图片替换签到背景，图片尽量清晰一些。')

    await create_user(user_id, group_id, event.sender)


@replace_bg.got("bg", prompt=MessageTemplate('{reply_msg}'))
async def _(bot: Bot, state: T_State, event: Event):
    """
    替换背景图
    """
    sender = event.sender

    logger.debug(f"sender: {sender}")

    message = event.get_message()
    logger.debug(f"message: {message}")
    msgdata = message.extract_plain_text().strip()

    if msgdata == '取消':
        await replace_bg.finish('已经取消替换背景图', at_sender=True)
    else:
        is_ok, msg = await handle_change_bg(
            bot=bot,
            user_id=state['user_id'],
            group_id=state['group_id'],
            message=message,
            sender=sender
        )
        if is_ok:
            await replace_bg.finish(msg, at_sender=True)
        else:
            send_count = state.get("send_count", 1)
            state["send_count"] = send_count + 1
            if send_count >= 3:
                await replace_bg.finish("错误次数过多，已取消", at_sender=True)

            await replace_bg.reject(msg+'，输入「取消」中断当前操作', at_sender=True)

    # await replace_bg.finish(msg, at_sender=True)
