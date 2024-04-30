import asyncio
from .hooks.game_hook import GameHook
from .utils import MsgText, At
from nonebot.adapters.onebot.v11 import (
    Bot,
    MessageSegment,
    GroupMessageEvent,
)
from nonebot import (
    on_command
)
import re
from importlib import import_module
import_module('.models', __package__)

# 开始战局
start_game = on_command('来一盘刺激的轮盘赌', priority=1, block=True)
# 手动结束战局
end_game = on_command('结束轮盘赌', priority=1, block=True)
# 参加战局
join_game = on_command('参与战局', priority=1, block=True)
# 开始游戏
start = on_command('开始游戏', priority=1, block=True)
# 使用卡片
use_card = on_command('使用卡片', priority=1, block=True)
# 跳过阶段
skip = on_command('pass', aliases={'跳过', '过'}, priority=1, block=True)
# 开枪阶段
pa = on_command('pa', aliases={'开枪', 'peng'}, priority=1, block=True)

# 查询当前流程
query = on_command('查询', priority=1, block=True)


@start_game.handle()
async def start_game_handle(bot: Bot, event: GroupMessageEvent):
    uid = str(event.user_id)
    gid = str(event.group_id)
    msg = MsgText(event.json())
    params = msg.split(" ")

    # 如果第一个不存在或第一个参数不是 /来一盘刺激的轮盘赌 则返回错误
    if not params or params[0] != '/来一盘刺激的轮盘赌':
        return await bot.send(event, "指令错误, 示例：/来一盘刺激的轮盘赌")

    msg = await GameHook.create_game(group_id=gid, user_id=uid)
    await bot.send(event, msg)


@end_game.handle()
async def end_game_handle(bot: Bot, event: GroupMessageEvent):
    uid = str(event.user_id)
    gid = str(event.group_id)
    msg = MsgText(event.json())
    params = msg.split(" ")

    # 如果第一个不存在或第一个参数不是 /结束轮盘赌 则返回错误
    if not params or params[0] != '/结束轮盘赌':
        return await bot.send(event, "指令错误, 示例：/结束轮盘赌")

    msg = await GameHook.close_game(group_id=gid, user_id=uid)
    await bot.send(event, msg)


@join_game.handle()
async def join_game_handle(bot: Bot, event: GroupMessageEvent):
    uid = str(event.user_id)
    gid = str(event.group_id)
    msg = MsgText(event.json())
    params = msg.split(" ")

    # 如果第一个不存在或第一个参数不是 /参与战局 则返回错误
    if not params or params[0] != '/参与战局':
        return await bot.send(event, "指令错误, 示例：/参与战局")

    msg = await GameHook.join_game(group_id=gid, user_id=uid)
    await bot.send(event, msg)


@start.handle()
async def start_handle(bot: Bot, event: GroupMessageEvent):
    uid = str(event.user_id)
    gid = str(event.group_id)
    msg = MsgText(event.json())
    params = msg.split(" ")

    # 如果第一个不存在或第一个参数不是 /开始游戏 则返回错误
    if not params or params[0] != '/开始游戏':
        return await bot.send(event, "指令错误, 示例：/开始游戏")

    # 获取游戏是否开始
    if start_msg := await GameHook.is_nostart_msg(group_id=gid, user_id=uid):
        return await bot.send(event, start_msg)

    # 是否存在游戏
    if game_msg := await GameHook.have_game(group_id=gid, user_id=uid):
        return await bot.send(event, game_msg)

    msg = await GameHook.start_game(group_id=gid, user_id=uid)
    await bot.send(event, msg)

    await GameHook.game_flowing(bot, event)


@query.handle()
async def query_handle(bot: Bot, event: GroupMessageEvent):
    uid = str(event.user_id)
    gid = str(event.group_id)
    msg = MsgText(event.json())
    params = msg.split(" ")

    # 如果第一个不存在或第一个参数不是 /开始游戏 则返回错误
    if not params or params[0] != '/查询':
        return await bot.send(event, "指令错误, 示例：/开始游戏")

    msg = await GameHook.query_info(group_id=gid, user_id=uid)
    await bot.send(event, msg)


@use_card.handle()
async def use_card_handle(bot: Bot, event: GroupMessageEvent):
    uid = str(event.user_id)
    gid = str(event.group_id)
    msg = MsgText(event.json())
    params = msg.split(" ")

    # 获取游戏是否开始
    is_start = await GameHook.is_start(group_id=gid, user_id=uid)

    if not is_start:
        return await bot.send(event, '战局尚未开始')

    # 如果第一个不存在或第一个参数不是 /开始游戏 则返回错误
    if not params or params[0] != '/使用卡片':
        return await bot.send(event, "指令错误, 示例：/使用卡片 [卡片名称]")

    if len(params) < 2:
        return await bot.send(event, "指令错误, 示例：/使用卡片 [卡片名称]")

    card_name = params[1]
    at_group = At(event.json())
    print(at_group)

    if msg := await GameHook.use_card(bot=bot, event=event, card_name=card_name, at_group=at_group):
        await bot.send(event, msg)


@skip.handle()
async def skip_handle(bot: Bot, event: GroupMessageEvent):
    uid = str(event.user_id)
    gid = str(event.group_id)
    msg = MsgText(event.json())
    params = msg.split(" ")
    # 获取游戏是否开始
    is_start = await GameHook.is_start(group_id=gid, user_id=uid)

    if not is_start:
        return await bot.send(event, '战局尚未开始')

    if msg := await GameHook.skip(bot=bot, event=event):
        await bot.send(event, msg)

@pa.handle()
async def pa_handle(bot: Bot, event: GroupMessageEvent):
    uid = str(event.user_id)
    gid = str(event.group_id)
    msg = MsgText(event.json())
    params = msg.split(" ")
    # 获取游戏是否开始
    is_start = await GameHook.is_start(group_id=gid, user_id=uid)

    if not is_start:
        return await bot.send(event, '战局尚未开始')
    

    aliases=['/开枪', '/peng','/pa']

    if not params or params[0] not in aliases:
        await bot.send(event=event,message='指令错误, 示例：/开枪 [@玩家]')
    
    at_group = At(event.json())
    if msg := await GameHook.shoot(bot=bot, event=event,at_group=at_group):
        await bot.send(event, msg)

