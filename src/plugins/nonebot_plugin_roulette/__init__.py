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
    
    # 获取游戏是否开始
    is_start = await GameHook.is_start(group_id=gid, user_id=uid)

    if not is_start:
        return await bot.send(event, '战局尚未开始')

    
    # 一个参数直接查询信息
    if len(params) == 1:
        return await GameHook.game_flowing(bot, event)

    

