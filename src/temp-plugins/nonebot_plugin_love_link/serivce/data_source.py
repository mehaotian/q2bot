from datetime import date
import os
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import Message, MessageSegment, GroupMessageEvent, Bot
import requests

from ..models.user_model import UserTable
from ..models.user_relations_model import UserRelationsTable
from ..text2img.signin2img import sign_in_2_img
from ..text2img.user2img import user2img

from ..config import  cache_directory



async def create_user(user_id: int, group_id: int, sender) -> Message:
    # 查询是否存在用户
    user_exists = await UserTable.filter(user_id=user_id, group_id=group_id).first()

    # 不存在则创建用户
    if not user_exists:
        logger.debug(f"user_exists: Flase")
        await UserTable.init_user(user_id=user_id, group_id=group_id,  sender=sender)


async def handle_sign_in(user_id: int, group_id: int, sender) -> Message:
    """
     签到处理
    :param user_id: 用户 ID
    :param group_id: 群组 ID
    :return: 签到结果
    """

    msg = Message()
    await create_user(user_id, group_id, sender)

    sender_user, _ = await UserTable.get_or_create(
        user_id=user_id,
        group_id=group_id,
    )

    last_sign = await UserTable.get_last_sign(user_id, group_id)
    # 判断是否已签到
    today = date.today()
    logger.debug(f"last_sign: {last_sign}")
    logger.debug(f"today: {today}")

    if today == last_sign:
        msg += Message("你今天已经签到了，不要贪心噢。")
        return msg

    # 签到名次
    sign_num = await UserTable.filter(group_id=group_id, last_sign=today).count() + 1

    # 设置签到
    data = await UserTable.sign_in(
        user_id=user_id,
        group_id=group_id,
    )

    bg_img = sender_user.bg_img or ''
    is_ok, sign_img_file = sign_in_2_img(
        nickname=sender_user.nickname,
        sign_num=sign_num,
        today_gold=data.today_gold,
        all_gold=data.all_gold,
        today_charm=data.today_charm,
        all_charm=data.all_charm,
        bg_path=bg_img,
        bg_name=f'{user_id}_{group_id}.jpg',
    )
    if is_ok:
        msg = MessageSegment.image(file=sign_img_file)
    else:
        msg_txt = f"本群第 {sign_num} 位 签到完成\n"
        msg_txt += f"获得金币：+{data.today_gold} (总金币：{data.all_gold})\n"
        msg_txt += f"获得魅力值：+{data.today_charm}（总魅力：{data.all_charm}）\n"
        msg_txt += f"累计签到次数：{data.sign_times}\n"
        msg_txt += f"连续签到次数：{data.streak}\n"
        msg += MessageSegment.text(msg_txt)
    return msg


async def handle_marriage(bot: Bot, user, user_id: int, group_id: int, send_user, text) -> Message:
    """
    处理婚姻
    :param bot: Bot 机器人对象
    :param user: 用户对象
    :param user_id: 用户 ID
    :param group_id: 群组 ID
    :param send_user: 关联用户对象
    :param text: 消息
    """

    # 创建自己的用户数据
    await create_user(user_id, group_id, dict(user))

    send_user_id = int(send_user['user_id'])

    # 创建对方的用户数据
    await create_user(send_user_id, group_id, send_user)

   

    is_status, msgData = await UserRelationsTable.register_user_relation(user_id=user_id, send_user_id=send_user_id, group_id=group_id, text=text)

    return MessageSegment.image(file=msgData)

    # 绑定错误信息  
    if not is_status:
        return Message(msgData)

      # 需要at对方
    at = MessageSegment.at(send_user_id)
    msg_text = ''
    if text == "嫁":
        msg_text += f"\n今天你的群老公是 {at} 哦~！🫶🫶🫶"
    elif text == "娶":
        msg_text += f"\n今天你的群老婆是 {at} 哦~！🫶🫶🫶"
    else:
        msg_text += f"\n你咋那么多事？"
        return Message(msg_text)

    if msgData.streak > 1:
        msg_text += f"\n你们已经连续 {msgData.streak} 天在一起了~！"
    if msgData.relation_days > 1:
        msg_text += f"\n你们最长在一起 {msgData.relation_days} 天！"

    return Message(msg_text)


async def handle_change_bg(bot: Bot, user_id: int, group_id: int, message: Message, sender):
    """
    换背景
    :param user_id: 用户 ID
    :param group_id: 群组 ID
    """
    user, _ = await UserTable.get_or_create(
        user_id=user_id,
        group_id=group_id,
    )

    file = None  # 初始化为 None
    for msg in message:
        if msg.type == "image":
            file = msg.data["file"]
            logger.debug(f"file: {file}")
            break  # 找到file后，中断for循环

    if file is not None:
        result = await bot.call_api("get_image", file=file)
        logger.debug(f"result: {result}")
        file_url = result["url"]
        if file_url:
            user.bg_img = file_url
            await user.save(update_fields=['bg_img'])
            # 将背景保存在本地
            bg_name = f'{user_id}_{group_id}.jpg'
            cache_path = os.path.join(cache_directory, bg_name)
            response = requests.get(file_url)
            if response.status_code == 200:
                with open(cache_path, "wb") as file:
                    file.write(response.content)
            return True, '背景替换成功'
        else:
            return False, Message("换背景失败,请重新发送图片")
    else:
        return False, Message("输入错误，请发送图片")


async def handle_query(user_id: int, group_id: int, sender) -> Message:
    """
    查询用户信息
    :param user_id: 用户 ID
    :param group_id: 群组 ID
    :return: 查询结果
    """
    # 不存在则创建用户
    await create_user(user_id, group_id, sender)


    # 获取信息
    user, _ = await UserTable.get_or_create(
        user_id=user_id,
        group_id=group_id,
    )

    data = {}

    data['gold'] = user.gold  # 金币
    data['charm'] = user.charm  # 魅力值
    data['sign_times'] = user.sign_times  # 累计签到次数
    data['sgin_streak'] = user.streak  # 连续签到次数

    # 今日是否签到
    last_sign = await UserTable.get_last_sign(user_id, group_id)
    today = date.today()

    data['is_sgin'] = True if today == last_sign else False

    relations = await UserRelationsTable.filter(
        user_id=user_id,
        group_id=group_id,
        last_relation=date.today(),
    ).first()

    if relations and relations.relation_user_id:
        sender = await UserTable.filter(user_id=relations.relation_user_id, group_id=group_id).first()

        data['relation'] = relations.relation
        data['relation_user_id'] = relations.relation_user_id
        data['relation_days'] = relations.relation_days
        data['streak'] = relations.streak
        data['sender_name'] = sender.nickname

    bg_img = user.bg_img or ''

    is_ok, sign_img_file = user2img(
        bg_name=f'{user_id}_{group_id}.jpg',
        nickname=user.nickname,
        data = data,
        bg_path = bg_img,
    )

    msg = Message()
    msg_txt = ''

    if is_ok:
        msg = MessageSegment.image(file=sign_img_file)
    else:
        msg_txt += (
            f'金币：{data["gold"]}\n'
            f'魅力值：{data["charm"]}\n'
            f'累计签到次数：{data["sign_times"]}\n'
            f'连续签到次数：{data["sgin_streak"]}\n'
        )
        if data["is_sgin"]:
            msg_txt += f"\n今日已签到\n"
        else:
            msg_txt += f"\n今日未签到\n"

        if 'relation_user_id' in data:
            msg_txt += f"\n你今天的群{data['relation']}是「{data['sender_name']}」"
            if data["streak"] > 1:
                msg_txt += f"\n你们已经连续 {data['streak']} 天在一起了~！"
            if data["relation_days"] > 1:
                msg_txt += f"\n你们最长在一起 {data['relation_days']} 天！"

        msg += MessageSegment.text(msg_txt)

    return msg

async def user_handle_divorce_success(user_id: int, group_id: int) -> Message:
    """
    分手成功
    :param user_id: 用户 ID
    :param group_id: 群组 ID
    :return: 查询结果
    """
    # 获取信息
    user, _ = await UserTable.get_or_create(
        user_id=user_id,
        group_id=group_id,
    )

    # 查询是否存在关联用户
    relations, _ = await UserRelationsTable.get_or_create(
        user_id=user_id,
        group_id=group_id,
        last_relation=date.today(),
    )
    relations_user_id = relations.relation_user_id

    relations.relation_user_id = 0

    # 因为是主动提出的，所以要减 100 魅力值
    user.charm -= 100
    if user.charm < 0:
        user.charm = 0

    # 需要通知对方
    at = MessageSegment.at(relations_user_id)

    await user.save(update_fields=['charm'])
    await relations.save(update_fields=['relation_user_id'])

    msg_txt = f"你和 {at} 已经分手了！扣除你 100 魅力值！"

    return Message(msg_txt)


async def user_handle_divorce_error(user_id: int, group_id: int) -> Message:
    """
    分手失败
    :param user_id: 用户 ID
    :param group_id: 群组 ID
    :return: 查询结果
    """
    user, _ = await UserTable.get_or_create(
        user_id=user_id,
        group_id=group_id,
    )

    user.charm -= 10
    if user.charm < 0:
        user.charm = 0

    await user.save(update_fields=['charm'])

    msg_txt = f"苦海无涯你，回头是岸！扣除你 10 魅力值！"

    return Message(msg_txt)


async def is_query_love(user_id: int, group_id: int) -> bool:
    """
    是否有情侣
    :param user_id: 用户 ID
    :param group_id: 群组 ID
    :return: 查询结果
    """
    # 查询是否存在用户
    user_exists = await UserRelationsTable.filter(
        user_id=user_id,
        group_id=group_id,
        last_relation=date.today(),
    ).first()

    # 不存在则创建用户
    if user_exists:
        return True
    else:
        return False
