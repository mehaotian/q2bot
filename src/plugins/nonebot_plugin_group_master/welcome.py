# python3
# -*- coding: utf-8 -*-
# @Time    : 2024-3-30 00:39
# @Author  : mehaoitan
# @Email   :  490272692@qq.com
# @File    : welcome.py
# @description: 群签到相关
# @Software: VS Code

from .utils import check_func_status
from .serivce.user_source import (
    create_user,
    handle_is_supplement,
    handle_sign_in,
    handle_change_bg,
    set_supplement,
    get_users2signin
)
from nonebot.log import logger
from nonebot.typing import T_State
from nonebot.adapters import MessageTemplate
from nonebot.adapters.onebot.v11 import (
    Bot,
    Event,
    Message,
    GroupMessageEvent,
    MessageSegment
)
from nonebot import on_fullmatch, on_command
# from PIL import Image
# from nonebot_plugin_htmlrender import (
#     template_to_pic,
# )
# from nonebot import require
# require("nonebot_plugin_htmlrender")
# 注意顺序，先require再 from ... import ...
# 注意顺序，先require再 from ... import ...
# 注意顺序，先require再 from ... import ...

# 指令集
commands = {
    "sign_in": "签到",
    "sign_in_bg": "签到背景",
    "sign_in_supplement": "补签"
}

# 签到
sign = on_fullmatch(commands["sign_in"], priority=5, block=False)
# 替换背景图
replace_bg = on_command(commands["sign_in_bg"], priority=5, block=False)
# 补签
supplement = on_fullmatch(
    commands["sign_in_supplement"], priority=5, block=False)
# 签到排行榜
sign_list = on_command("签到排行榜")



@sign.handle()
async def sign_in(bot: Bot, event: GroupMessageEvent):
    """
    签到
    """
    user_id = str(event.user_id)
    group_id = str(event.group_id)

    # 检查是否开启签到功能
    if not await check_func_status('签到', group_id):
        return await sign.finish('签到功能未开启')

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

    # 检查是否开启签到背景功能
    if not await check_func_status('签到', group_id):
        return await replace_bg.finish('签到背景功能未开启')

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


@supplement.handle()
async def supplement_sign_in(bot: Bot, state: T_State, event: GroupMessageEvent):
    """
    补签
    """
    user_id = str(event.user_id)
    group_id = str(event.group_id)
    if not await check_func_status('签到', group_id):
        await supplement.finish('补签功能未开启', at_sender=True)

    logger.debug(f"群 group_id: 用户 {user_id} 补签")
    is_ok, msg = await handle_is_supplement(user_id=user_id, group_id=group_id, sender=event.sender)
    # await bot.send(event=event, message=msg)
    # 阻止 got
    if not is_ok:
        await supplement.finish(msg, at_sender=True)

    at = MessageSegment.at(event.user_id)
    state['user_id'] = user_id
    state['group_id'] = group_id
    state['use_gold'] = is_ok
    state['reply_msg'] = at + Message(msg)


@supplement.got("date", prompt=MessageTemplate("{reply_msg}"))
async def _(bot: Bot, state: T_State, event: Event):
    """
    补签
    """
    message = event.get_message()
    msgdata = message.extract_plain_text().strip()

    if msgdata == "2":
        await supplement.finish('已经取消补签', at_sender=True)
    elif msgdata == "1":
        user_id = state['user_id']
        group_id = state['group_id']
        use_gold = state['use_gold']
        msg = await set_supplement(user_id=user_id, group_id=group_id, use_gold=use_gold)
        await supplement.finish(msg, at_sender=True)
    else:
        await supplement.finish('输入错误，已取消补签', at_sender=True)

@sign_list.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    # from pathlib import Path
    # gid = str(event.group_id)
    # users = await get_users2signin(group_id=gid)
    # # 将前三和后面的用户分开
    # users = users[:3], users[3:]
    # before_users, after_users = users

    # # 尝试安全地从 after_users 获取前三个用户，如果不存在则为 None
    # user1 = before_users[0] if len(before_users) > 0 else None
    # user2 = before_users[1] if len(before_users) > 1 else None
    # user3 = before_users[2] if len(before_users) > 2 else None
 
    # template_path = Path(__file__).parent / "templates"
    # template_name = "text.html"
    # # css_path = template_path / "mystyle.css"
    # # 设置模板
    # # 模板中本地资源地址需要相对于 base_url 或使用绝对路径
    # # 头部高 400 20内边距
    # pic = await template_to_pic(
    #     template_path=str(template_path),
    #     template_name=template_name,
    #     templates={
    #         "user1": user1,
    #         "user2": user2,
    #         "user3": user3,
    #         "after_users": after_users,
    #     },
    #     pages={
    #         "viewport": {"width": 600, "height": 420},
    #         "base_url": f"file://{str(template_path)}",
    #     },
    #     wait=2,
    # )

    # a = Image.open(io.BytesIO(pic))
    # img_byte = io.BytesIO()
    # a.save(img_byte, format="PNG")

    # await sign_list.finish(MessageSegment.image(pic))
    pass
