# python3
# -*- coding: utf-8 -*-
# @Time    : 2024-3-30 00:39
# @Author  : mehaoitan
# @Email   :  490272692@qq.com
# @File    : say.py
# @description: 逼话排行榜
# @Software: VS Code

import re
from nonebot import (
    on_message,
    on_fullmatch,
    on_command,
    on_notice,
    on_regex
)
from nonebot.adapters.onebot.v11 import (
    Bot,
    Message,
    GroupMessageEvent,
    MessageSegment,
    NoticeEvent,
    ActionFailed,
)
from nonebot.internal.matcher import Matcher

from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER
from nonebot.permission import SUPERUSER

from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.log import logger
from nonebot import require
from .utils import MsgText, Reply, check_func_status, check_message_legality


try:
    scheduler = require("nonebot_plugin_apscheduler").scheduler
except Exception:
    scheduler = None

from .serivce.say_source import get_say_list, save_user_say, get_user_say, get_say_total, get_lottery_month, lottery_user, get_today_active
from .models.user_model import UserTable

# 监听用户消息
run_say = on_message(priority=1, block=False)

# 消息撤回
recall_run = on_notice(priority=1, block=False)

# 逼话排行榜
say_reg = r"^(今日|昨天|前天|本周|上周|本月|上月|今年|去年|全部)逼话排行榜|^逼话排行榜$"
say = on_regex(say_reg, priority=1, block=False)

# 查询自己指定时间逼话榜详情
query_me_reg = r"^(今日|昨天|前天|本周|上周|本月|上月|今年|去年|全部)逼话$"
query_me = on_regex(query_me_reg, priority=1, block=False)


# 逼话限定抽奖
bihua_kaijiang = on_command("逼话开奖", rule=to_me(
), permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER, priority=9, block=True)

# 今日活跃
today_active = on_regex("^今日活跃$", permission=SUPERUSER |
                        GROUP_ADMIN | GROUP_OWNER, priority=9, block=True)


# 更新用户昵称
update_nickname = on_fullmatch("更新", priority=1, block=False)


@say.handle()
async def say_handle(bot: Bot, event: GroupMessageEvent):
    # 获取消息内容
    text = event.message.extract_plain_text().strip()

    # 获取群组ID
    group_id = str(event.group_id)

    # 获取用户ID
    user_id = str(event.user_id)

    if not await check_func_status('逼话榜', group_id):
        return await say.finish('逼话功能未开启')

    # 获取匹配的月份或日期
    match = re.match(say_reg, text)
    logger.debug(f'match：{match}')
    if match:
        date = match.group(1)
        if not date:
            date = "今日"
        await bot.send(event=event, message=f"{date}逼话排行榜正在准备中，请稍后...")

        msg = await get_say_list(date_str=date, group_id=group_id)
        await bot.send(event=event, message=msg)


@bihua_kaijiang.handle()
async def bihua_kaijiang_handle(bot: Bot, event: GroupMessageEvent):
    # 获取消息内容
    # 获取群组ID
    group_id = str(event.group_id)

    if not await check_func_status('逼话榜', group_id):
        return await bihua_kaijiang.finish('逼话功能未开启')

    msg = MsgText(event.json())
    msg = re.sub(' +', ' ', msg)
    params = msg.split(" ")

    if len(params) >= 3:
        time = params[1]
        lt_reg = r"^(今日|昨天|前天|本周|上周|本月|上月|今年|去年|全部)$"
        if not re.match(lt_reg, time):
            return await bot.send(event, f"喵叽提醒：逼话开奖时间错误")

        command = params[2]

        if command == '查询':
            # count =  params[3]
            # 如果 params[3] 不存在则返回
            if len(params) < 4:
                return await bot.send(event, f"喵叽提醒：请输入查询字数")
            count = params[3]

            if not count.isdigit():
                return await bot.send(event, f"喵叽提醒：逼话保底数字错误")
            textCount = int(count)
            await bot.send(event, f"{time}逼话抽奖资格查询中,保底为： {textCount}，请稍后...")

            msg, data = await get_lottery_month(group_id=group_id, textCount=textCount, time=time)

            return await bot.send(event=event, message=msg)

        if not command.isdigit():
            return await bot.send(event, f"喵叽提醒：逼话保底数字错误")

        textCount = int(command)
        await bot.send(event=event, message=f"抽奖封箱，资格查询中,保底为： {textCount}，请稍后...")

        msg, data = await get_lottery_month(group_id=group_id, textCount=textCount, time=time)

        await bot.send(event=event, message=msg)
        await bot.send(event=event, message=f"抽奖资格已生成，摇奖中，请稍后...")

        user_msg = await lottery_user(data=data, textCount=textCount)
        await bot.send(event=event, message=user_msg)

    else:
        return await bot.send(event, f"喵叽提醒：逼话摇奖指令错误")


@query_me.handle()
async def query_me_handle(bot: Bot, event: GroupMessageEvent):
    # 获取消息内容
    text = event.message.extract_plain_text().strip()

    # 获取群组ID
    group_id = str(event.group_id)

    if not await check_func_status('逼话榜', group_id):
        return await query_me.finish('逼话功能未开启')

    # 获取用户ID
    user_id = str(event.user_id)

    # 获取匹配的月份或日期
    match = re.match(query_me_reg, text)
    logger.debug(f'match：{match}')
    if match:
        date = match.group(1)
        # await get_says(date_str=date, group_id=group_id, user_id=user_id)
        await bot.send(event=event, message=f"{date}逼话正在准备中，请稍后...")
        msg = await get_user_say(date_str=date, user_id=user_id, group_id=group_id)

        # 查询指定时间的逼话排行榜
        await bot.send(event=event, message=msg)


@today_active.handle()
async def today_active_handle(bot: Bot, event: GroupMessageEvent):
    """
    查询今日活跃用户
    """
    # 获取消息内容
    # 获取群组ID
    group_id = str(event.group_id)

    if not await check_func_status('逼话榜', group_id):
        return await today_active.finish('逼话功能未开启')

    msg = MsgText(event.json())
    msg = re.sub(' +', ' ', msg)
    params = msg.split(" ")

    await bot.send(event=event, message=f"今日活跃逼友查询中，请稍后...")

    msg = await get_today_active(group_id=group_id)

    await bot.send(event=event, message=msg)


@update_nickname.handle()
async def update_nickname_handle(bot: Bot, event: GroupMessageEvent):
    # 获取用户消息
    user_id = str(event.user_id)
    group_id = str(event.group_id)

    if not await check_func_status('逼话榜', group_id):
        return await update_nickname.finish('逼话功能未开启')

    # 准备信息
    msg = MessageSegment.at(user_id)

    try:
        user = await bot.get_group_member_info(group_id=group_id, user_id=user_id, no_cache=True)

        print(user)
        event.sender.nickname = user['nickname']
        event.sender.card = user['card']
        await bot.send(event=event, message=Message(msg + MessageSegment.text("\n您的数据更新中，请稍后...")))
        record = await UserTable.init_user(user_id=user_id, group_id=group_id, sender=event.sender)
        relpy_msg = MessageSegment.reply(event.message_id)
        await bot.send(event=event, message=Message(relpy_msg + MessageSegment.text(f"更新成功")))
    except Exception as e:
        logger.error(f"更新用户信息失败，{repr(e)}")
        await bot.send(event=event, message=Message(msg + MessageSegment.text(" 数据更新失败！")))



# 创建一个字典来记录每个用户的消息撤回次数
user_revoke_count = {}

# 打断+1
interrupt = {
    "words":'',
    "count":0
}

@run_say.handle()
async def saying_handle(bot: Bot,  matcher: Matcher, event: GroupMessageEvent, state: T_State):
    gid = str(event.group_id)
    uid = str(event.user_id)
    # 是否回复
    rp = Reply(event.json())
    # 获取经验
    # msg = await game.add_exp(event)
    # 获取用户消息
    message = event.get_message()
    msgdata = message.extract_plain_text().strip()

    is_words_ok = await check_message_legality(gid=gid, cmd=matcher, msg=msgdata)

    if not is_words_ok:
        print('消息被撤回')
        # 撤回消息 ，如果消息中出现黑名单中的关键词，则撤回消息
        await bot.delete_msg(message_id=event.message_id)

        # 更新用户的消息撤回次数
        if uid not in user_revoke_count:
            user_revoke_count[uid] = 0
        user_revoke_count[uid] += 1

        # 如果用户的消息撤回次数达到三次，则禁言一分钟
        if user_revoke_count[uid] >= 3:
            try:
                await bot.set_group_ban(group_id=event.group_id, user_id=event.user_id, duration=60)
                print(f"用户 {uid} 被禁言一分钟")
                # 重置用户的消息撤回次数
                user_revoke_count[uid] = 0
                await bot.send(event=event, message=f"您因为发送违规消息超过3次，已被禁言一分钟", at_sender=True)
            except ActionFailed as e:
                print(f"禁言失败: {e}")
        return
    
    # 打断+1 
    if msgdata == interrupt["words"]:
        interrupt["count"] += 1
        if interrupt["count"] >= 3:
            await bot.send(event=event, message=MessageSegment.text(f"哎嗨，可恶的复读机，打断你～"))
            interrupt["count"] = 0

    interrupt["words"] = msgdata

    if not await check_func_status('逼话榜', gid):
        return

    imagesCount = 0
    facesCount = 0
    replyCount = 0
    at_user_ids = []
    textCount = len(msgdata)
    # 每条记录
    total_count = 0
    for msg in message:
        # if msg.type == "reply":
        #     replyCount += 1
        if msg.type == "image":
            imagesCount += 1
        if msg.type == "face":
            facesCount += 1
        if msg.type == "at":
            user_id = msg.data.get('qq', None)
            if user_id:
                # 如果存在则不插入
                if user_id not in at_user_ids:
                    at_user_ids.append(user_id)

    if rp:
        replyCount += 1

    total_count += 1

    user_id = str(event.user_id)
    group_id = str(event.group_id)
    sender = event.sender

    # 构建消息体
    data = {
        'image_count': imagesCount,
        'face_count': facesCount,
        'reply_count': replyCount,
        'at_count': len(at_user_ids),
        'text_count': textCount,
        'total_count': total_count
    }

    if textCount > 100:
        msg = MessageSegment.reply(event.message_id) + \
            MessageSegment.text(
                f"当前内容疑似恶意刷屏，不计入逼话！如果是故意刷屏，将取消所有逼话抽奖资格，正常聊天则不受影响。")
        return await bot.send(event=event, message=msg)

    await save_user_say(user_id, group_id, sender, data)


@recall_run.handle()
async def recall_handle(bot: Bot, event: NoticeEvent):
    # message = event.get_message()
    # 被操作
    user_id = str(event.user_id)
    # 操作者
    if hasattr(event, 'operator_id'):
        operator_id = str(event.operator_id)
    else:
        operator_id = None

    message_type = event.notice_type
    user_id = str(event.user_id)
    group_id = str(event.group_id)
    recall_count = 0

    if message_type == "group_recall":
        if user_id == operator_id:
            recall_count += 1
            data = {
                "recall_count": recall_count
            }
            user = await bot.get_group_member_info(group_id=group_id, user_id=user_id)
            await save_user_say(user_id=user_id, group_id=group_id, sender=user, data=data)


async def post_scheduler():
    """
    统计昨天逼王
    """
    # 正经交流群 qq 号 ，目前写死
    group_id = '596464232'
    logger.info("开始执行定时任务,统计昨日逼王")
    await get_say_total(group_id=group_id)

try:
    scheduler.add_job(
        post_scheduler,
        "cron",
        hour=0,
        minute=0,
        second=5,
        id="everyday_00_00_05",
        replace_existing=True
        # post_scheduler, "interval", minutes=2, id="every_2_minutes"
    )
except ActionFailed as e:
    logger.warning(f"定时任务添加失败，{repr(e)}")
