# 随机
import random
from datetime import date, datetime, timedelta
import os
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from collections import defaultdict
from .user_source import create_user
from ..models.user_model import UserTable
from ..models.say_model import SayTable
from ..models.say_stat_model import SayStatTable
from ..text2img.say2img import say2img
from ..text2img.card2img import card2img
from ..text2img.lottery2img import lottery2img
from ..utils import get_start_time, get_end_time
from ..utils.txt2img import txt2img


async def save_user_say(user_id: str, group_id: str, sender, data) -> Message:
    """
    保存用户说的话
    :param user_id: 用户 ID
    :param group_id: 群组 ID
    :param msg: 用户说的话
    :param data: 会话消息

    :return: 用户信息
    """
    await create_user(user_id, group_id, sender)

    sender_user, _ = await UserTable.get_or_create(
        user_id=user_id,
        group_id=group_id,
    )

    # 获取用户id ,来自不同群和不同用户
    uid = sender_user.id

    await SayTable.save_says(uid, data)


async def get_user_say(date_str: str, user_id: str, group_id: str) -> Message:
    """
    获取用户会话
    :param date_str: 日期字符串
    :param user_id: 用户 ID
    :param group_id: 群组 ID

    :return: 用户信息
    """
    # 开始查询日期
    start_date = get_start_time(date_str)
    end_date = get_end_time(date_str)

    print('start_date', start_date)
    print('end_date', end_date)
    # 查询用户数据
    user = await UserTable.get_user_says(user_id, group_id)
    # 获取用户字典
    user_dict = {k: v for k, v in user.__dict__.items()
                 if not k.startswith('_')}
    says = await SayTable.query_says(uid=user.id, start_time=start_date, end_time=end_date)

    # 数据集
    total_data = {
        'image_count': 0,
        'face_count': 0,
        'reply_count': 0,
        'at_count': 0,
        'text_count': 0,
        'total_count': 0,
        'recall_count': 0,
        'user': user_dict
    }

    for say in says:
        total_data['image_count'] += say.image_count
        total_data['face_count'] += say.face_count
        total_data['reply_count'] += say.reply_count
        total_data['at_count'] += say.at_count
        total_data['text_count'] += say.text_count
        total_data['total_count'] += say.total_count
        total_data['recall_count'] += say.recall_count

    is_ok, say_img = card2img(data=total_data, date_str=date_str)
    if is_ok:
        return MessageSegment.image(file=say_img)
    else:
        return '生成错误'


async def get_say_list(date_str: str, group_id: str) -> list:
    """
    获取用户在指定时间段内的数据
    :param date_str: 日期字符串
    :param uid: 用户唯一ID
    :param start_time: 开始时间
    :return: 数据
    """
    # 开始查询日期
    start_date = get_start_time(date_str)
    end_date = get_end_time(date_str)

    print('逼话开始时间 start_date', start_date)
    print('逼话结束时间 end_date', end_date)
    aggregated_says = await SayTable.get_the_charts(group_id, start_date, end_date)

    is_ok, img_file = say2img(data=aggregated_says, date_str=date_str)
    if is_ok:
        return MessageSegment.image(file=img_file)
    else:
        return Message("生成失败")


async def get_lottery_month(group_id: str, textCount: int = 2000,time='本周') -> Message:
    """
    获取用户在指定时间段内的数据
    :param date_str: 日期字符串
    :param uid: 用户唯一ID
    :param start_time: 开始时间
    :return: 数据
    """
    # 开始查询日期
    start_date = get_start_time(time)
    end_date = get_end_time(time)

    aggregated_says = await SayTable.get_the_charts(group_id, start_date, end_date)

    is_ok, img_file = say2img(data=aggregated_says,
                              date_str=time, textCount=textCount,top_title="抽奖", title=f"{time}逼话 {textCount} 抽奖资格")
    # return Message("生成成功"), aggregated_says

    if is_ok:
        return MessageSegment.image(file=img_file), aggregated_says
    else:
        return Message("生成失败"), None


async def lottery_user(data, textCount):
    """
    本月逼话摇奖
    :param data: 数据
    :param textCount: 逼话保底
    :return: 用户信息
    """
    # 获取符合要求逼话的用户
    data = [item for item in data if item.get('total', 0) >= textCount]

    if not data and len(data) == 0:
        return '没有符合要求的用户'

    # 从 data 中随机一个数据出来
    user = random.choice(data)
    print('user', user)
    is_ok, file = lottery2img(user=user)
    if is_ok:
        user_me = user.get('users', None)
        if user_me:
            user_id = user_me.get('user_id', None)
            if user_id:
                at = MessageSegment.at(user_id)
                return at + MessageSegment.image(file=file)
        return '好像抽到一个不存在的人，请重新抽奖'

    else:
        return '可能是因为网络波动，抽奖发生错误，请重新抽奖'
        # msg = (
        #     f"恭喜"
        #     f"用户：{user.get('nickname', '未知')}, "
        # )


async def get_today_active(group_id: str,):
    """
    获取今日活跃用户
    """
    # 开始查询日期
    start_date = get_start_time('今日')
    end_date = get_end_time('今日')

    aggregated_says = await SayTable.get_the_charts(group_id, start_date, end_date)

    is_ok, img_file = say2img(data=aggregated_says, textCount= 0,
                              date_str='今日', top_text='活跃', top_title="榜单", title="今日活跃排行")

    if is_ok:
        return MessageSegment.image(file=img_file)
    else:
        return Message("生成失败")


async def get_say_total(group_id: str):
    """
    获取用户在指定时间段内的数据
    :param date_str: 日期字符串
    :param uid: 用户唯一ID
    :param start_time: 开始时间
    :return: 数据
    """

    now = datetime.now()
    # 获取今天最早的时间段
    yesterday = now - timedelta(days=1)
    start_time = datetime(yesterday.year, yesterday.month, yesterday.day)
    end_time = datetime(now.year, now.month, now.day)

    # 记录查询开始的时间
    query_start_time = datetime.now()

    # 获取排行榜
    aggregated_says = await SayTable.get_the_charts(group_id, start_time, end_time)

    print('aggregated_says', aggregated_says)

    # 记录查询结束的时间
    query_end_time = datetime.now()

    # 计算查询的执行时间
    query_execution_time = query_end_time - query_start_time
    logger.info(f"排行榜查询执行时间：{query_execution_time.total_seconds()* 1000} 秒")

    # 新逼王
    # new_bking = aggregated_says[0]
    if aggregated_says:
        new_bking = aggregated_says[0]

        new_bking_uid = new_bking['user_id']

        await SayStatTable.save_bking(new_bking_uid)

        return group_id

    return None
