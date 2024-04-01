from datetime import date, datetime
import os
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from collections import defaultdict
from .user_source import create_user
from ..models.user_model import UserTable
from ..models.say_model import SayTable
from ..text2img.say2img import say2img
from ..text2img.card2img import card2img
from ..utils import get_start_time,get_end_time
from ..utils.txt2img import txt2img


async def save_user_say(user_id: int, group_id: int, sender, data) -> Message:
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


    is_ok, say_img = card2img(data=total_data,date_str=date_str)
    if is_ok:
        return MessageSegment.image(file=say_img)
    else:
        return MessageSegment.at(user_id=user_id)+Message(msg)


async def get_say_list(group_id) -> list:
    """
    获取用户在指定时间段内的数据
    :param uid: 用户唯一ID
    :param start_time: 开始时间
    :return: 数据
    """
    now = datetime.now()
    # next_hour = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
    # # 获取当前小时的开始时间
    # start_time = now.replace(minute=0, second=0, microsecond=0)

    # 获取今天最早的时间段
    start_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    # 获取所有满足条件的记录
    says = await SayTable.filter(created_at__gte=start_time).values()

    # 使用字典进行分组
    grouped_says = defaultdict(list)
    for say in says:
        grouped_says[say['user_id']].append(say)

    # 对每个用户的记录进行聚合
    aggregated_says = []
    for user_id, user_says in grouped_says.items():
        total_image_count = sum(say['image_count'] for say in user_says)
        total_face_count = sum(say['face_count'] for say in user_says)
        total_reply_count = sum(say['reply_count'] for say in user_says)
        total_at_count = sum(say['at_count'] for say in user_says)
        total_text_count = sum(say['text_count'] for say in user_says)
        total_count = sum(say['total_count'] for say in user_says)
        total_recall_count = sum(say['recall_count'] for say in user_says)
        # 获取用户
        user = await UserTable.get(id=user_id)
        user_group_id = user.group_id
        # 筛选同一个群
        if user_group_id == group_id:
            user_dict = {k: v for k, v in user.__dict__.items()
                         if not k.startswith('_')}
            aggregated_says.append({
                'user_id': user_id,
                'total_image_count': total_image_count,
                'total_face_count': total_face_count,
                'total_reply_count': total_reply_count,
                'total_at_count': total_at_count,
                'total_text_count': total_text_count,
                'total_count': total_count,
                'total_recall_count': total_recall_count,
                "users": user_dict
            })

    # 排序 ，total_image_count + total_face_count +total_reply_count + total_at_count + total_text_count +total_recall_count ，从大到小
    aggregated_says.sort(key=lambda x: x['total_image_count'] + x['total_face_count'] + x['total_reply_count'] +
                         x['total_at_count'] + x['total_text_count'] + x['total_recall_count'], reverse=True)

    is_ok, img_file = say2img(data=aggregated_says)
    if is_ok:
        return MessageSegment.image(file=img_file)
    else:
        return Message("生成失败")
