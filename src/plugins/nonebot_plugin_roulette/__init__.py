from nonebot import require
from .config import global_config
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
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from nonebot.log import logger
from importlib import import_module
import_module('.models', __package__)


scheduler_db_url = global_config.scheduler_db_url
# 定时任务
try:
    scheduler = require("nonebot_plugin_apscheduler").scheduler
except Exception:
    scheduler = None

# 开始战局
start_game_aliases = ['创建战局', '想跟姐妹来一场愉悦の拼刺刀嘛',
                      '想不想来一场刺激的对枪运动', 'created', 'c']
start_game = on_command(start_game_aliases[0],  aliases=set(
    start_game_aliases[1:]), priority=1, block=True)
# 手动结束战局
end_game_aliases = ['结束轮盘赌', '都踏马别玩啦', '有内奸终止交易', 'end', 'e']
end_game = on_command(
    end_game_aliases[0], aliases=set(end_game_aliases[1:]), priority=1, block=True)
# 参加战局
join_game_aliases = ['参与战局', '我也要玩', '我要参加入', '都别动让我来', 'join', 'j']
join_game = on_command(join_game_aliases[0], aliases=set(
    join_game_aliases[1:]), priority=1, block=True)
# 开始游戏
start_aliases = ['开始战局', '轮盘启动', '预备开始', 'start', 's']
start = on_command(start_aliases[0], aliases=set(
    start_aliases[1:]), priority=1, block=True)
# 使用卡片
use_card_aliases = ['使用卡片', '使用卡牌', '就你了', '吃我一招', '使用', '用卡', 'use', 'u']
use_card = on_command(use_card_aliases[0], aliases=set(
    use_card_aliases[1:]), priority=1, block=True)
# 跳过阶段
skip_aliases = ['跳过', 'pass','skip', '过']
skip = on_command(skip_aliases[0], aliases=set(skip_aliases[1:]), priority=1, block=True)
# 开枪阶段
pa_aliases = ['开枪','shoot' ,'peng', 'pa', 'p']
pa = on_command(pa_aliases[0], aliases=set(pa_aliases[1:]), priority=1, block=True)

# 查询当前流程
query_aliases = ['查询', '查看', 'q']
query = on_command(query_aliases[0], aliases=set(
    query_aliases[1:]), priority=1, block=True)

# 帮助
game_help_aliases = ['帮助', 'help', 'h']
game_help = on_command(game_help_aliases[0], aliases=set(
    game_help_aliases[1:]), priority=1, block=True)

# 获取个人信息
get_info_aliases = ['我的信息', '我的', '我', 'info', 'i']
get_info = on_command(get_info_aliases[0], aliases=set(
    get_info_aliases[1:]), priority=1, block=True)

@start_game.handle()
async def start_game_handle(bot: Bot, event: GroupMessageEvent):
    uid = str(event.user_id)
    gid = str(event.group_id)
    msg = MsgText(event.json())
    msg = re.sub(' +', ' ', msg)
    params = msg.split(" ")

    print(params[1])

    if not params or params[0][1:] not in start_game_aliases:
        return await bot.send(event, f"指令错误, 示例：/{start_game_aliases[0]}")
    

    # 筹码
    chips = 200
    if len(params) > 1:
        chips = params[1]
        if not chips.isdigit():
            return await bot.send(event, f"喵叽提醒：筹码必须是数字")
        chips = int(chips)

    # 玩家数量
    player_count = 5
    if len(params) > 2:
        player_count = params[2]
        if not player_count.isdigit():
            return await bot.send(event, f"喵叽提醒：玩家数量必须是数字")
        player_count = int(player_count)

    msg = await GameHook.create_game(group_id=gid, user_id=uid,chips=chips,player_count=player_count)
    await bot.send(event, msg)


@end_game.handle()
async def end_game_handle(bot: Bot, event: GroupMessageEvent):
    uid = str(event.user_id)
    gid = str(event.group_id)
    msg = MsgText(event.json())
    params = msg.split(" ")

    # 如果第一个不存在或第一个参数不是 /结束轮盘赌 则返回错误
    if not params or params[0][1:] not in end_game_aliases:
        return await bot.send(event, f"指令错误, 示例：/{end_game_aliases[0]}")

    msg = await GameHook.close_game(group_id=gid, user_id=uid)
    await bot.send(event, msg)


@join_game.handle()
async def join_game_handle(bot: Bot, event: GroupMessageEvent):
    uid = str(event.user_id)
    gid = str(event.group_id)
    msg = MsgText(event.json())
    params = msg.split(" ")

    # 如果第一个不存在或第一个参数不是 /参与战局 则返回错误
    if not params or params[0][1:] not in join_game_aliases:
        return await bot.send(event, f"指令错误, 示例：/{join_game_aliases[0]}")

    msg = await GameHook.join_game(group_id=gid, user_id=uid)
    await bot.send(event, msg)


@start.handle()
async def start_handle(bot: Bot, event: GroupMessageEvent):
    uid = str(event.user_id)
    gid = str(event.group_id)
    msg = MsgText(event.json())
    params = msg.split(" ")

    # 如果第一个不存在或第一个参数不是 /开始游戏 则返回错误
    if not params or params[0][1:] not in start_aliases:
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
    if not params or params[0][1:] not in query_aliases:
        return await bot.send(event, f"指令错误, 示例：/{query_aliases[0]}")

    if len(params) == 1:
        msg = await GameHook.query_info(group_id=gid, user_id=uid)
        return await bot.send(event, msg)

    # 指令
    command = params[1]
    # 合法指令
    # command_list = ['流程']
    if command == '流程':
        return await GameHook.game_flowing(bot, event)


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
    if not params or params[0][1:] not in use_card_aliases:
        return await bot.send(event, f"指令错误, 示例：/{use_card_aliases[0]} [卡片名称]")

    if len(params) < 2:
        return await bot.send(event, f"指令错误, 示例：/{use_card_aliases[0]} [卡片名称]")

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
    
    if not params or params[0][1:] not in skip_aliases:
        await bot.send(event=event, message=f'指令错误, 示例：/{skip_aliases[0]}')

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

    if not params or params[0][1:] not in pa_aliases:
        await bot.send(event=event, message='指令错误, 示例：/开枪 [@玩家]')

    at_group = At(event.json())
    if msg := await GameHook.shoot(bot=bot, event=event, at_group=at_group):
        await bot.send(event, msg)

@get_info.handle()
async def get_info_handle(bot: Bot, event: GroupMessageEvent):
    uid = str(event.user_id)
    gid = str(event.group_id)
    msg = MsgText(event.json())
    params = msg.split(" ")

    # 如果第一个不存在或第一个参数不是 /开始游戏 则返回错误
    if not params or params[0][1:] not in get_info_aliases:
        return await bot.send(event, f"指令错误, 示例：/{get_info_aliases[0]}")

    msg = await GameHook.get_info(group_id=gid, user_id=uid)
    await bot.send(event, msg)


@game_help.handle()
async def game_help_handle(bot: Bot, event: GroupMessageEvent):
    uid = str(event.user_id)
    gid = str(event.group_id)
    msg = MsgText(event.json())
    params = msg.split(" ")

    # 如果第一个不存在或第一个参数不是 /开始游戏 则返回错误
    if not params or params[0][1:] not in game_help_aliases:
        return await bot.send(event, f"指令错误, 示例：/{game_help_aliases[0]}")

    if len(params) == 1:
        msg = (
            f"首先，感谢您游玩喵叽群轮盘赌小游戏，为了更好的游玩体验，请阅读以下游戏说明：\n"
            f"1. 【/h 1】 查看注意事项\n"
            f"2. 【/h 2】 查看游戏流程\n"
            f"3. 【/h 3】 查看卡片效果\n"
            f"4. 【/h 4】 查看游戏命令\n"
        )
        return await bot.send(event=event, message=msg)
    # 指令
    command = params[1]
    # 合法指令
    # command_list = ['流程']
    if command == '1':
        msg = GameHook.game_help_rule()
        return await bot.send(event=event, message=msg)
    if command == '2':
        msg = GameHook.game_help_flowing()
        return await bot.send(event=event, message=msg)
    if command == '3':
        msg = GameHook.game_help_card()
        return await bot.send(event=event, message=msg)
    if command == '4':
        msg = GameHook.game_help_instruct()
        return await bot.send(event=event, message=msg)
    


# 设置定时任务持久化
try:
    scheduler.add_jobstore(SQLAlchemyJobStore(
        url=scheduler_db_url), 'roulettedbsql')
    logger.success('轮盘赌 Jobstore 持久化成功')
except Exception as e:
    logger.error(f'轮盘赌 Jobstore 持久化失败: {e}')
