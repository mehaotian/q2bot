from datetime import date
import os
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import Message, MessageSegment, GroupMessageEvent, Bot
import requests

from ..models.user_model import UserTable
from ..text2img.signin2img import sign_in_2_img
from ..text2img.user2img import user2img

from ..config import cache_directory


async def create_user(user_id: int, group_id: int, sender) -> Message:
    """
    创建用户
    :param user_id: 用户 ID
    :param group_id: 群组 ID
    :return: 用户信息
    """
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
        msg += Message("你今天已经签到了，明天再来吧！")
        return msg

    # 签到名次
    sign_num = await UserTable.filter(group_id=group_id, last_sign=today).count() + 1

    # 设置签到
    data = await UserTable.sign_in(
        user_id=user_id,
        group_id=group_id,
    )

    bg_img = sender_user.bg_img or ''

    # 获取签到图片
    is_ok, sign_img_file = sign_in_2_img(
        nickname=sender_user.nickname,
        sign_num=sign_num,
        bg_path=bg_img,
        user_id=user_id,
        group_id=group_id,
        data=dict(data),
    )

    if is_ok:
        msg = MessageSegment.image(file=sign_img_file)
    else:
        msg_txt = f"本群第 {sign_num} 位 签到完成\n"
        msg_txt += f"获得金币：+{data.today_gold} (总金币：{data.all_gold})\n"
        msg_txt += f"获得牛力值：+{data.today_charm}（总牛力：{data.all_charm}）\n"
        msg_txt += f"累计签到次数：{data.sign_times}\n"
        msg_txt += f"连续签到次数：{data.streak}\n"
        msg += MessageSegment.text(msg_txt)
    return msg


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

    return ''
