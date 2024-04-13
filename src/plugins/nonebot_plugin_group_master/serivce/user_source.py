import os
import httpx
from datetime import date
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import Message, MessageSegment, GroupMessageEvent, Bot ,ActionFailed
from typing import Union, Optional
from ..models.user_model import UserTable
from ..text2img.signin2img import sign_in_2_img

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

    bg_img = sender_user.bg_img or ''

    # TODO 暂时注释测试用，如果发现无限签到，那准时这的问题
    if today == last_sign:
        # 获取签到图片
        is_ok, sign_img_file = sign_in_2_img(
            nickname=sender_user.nickname,
            bg_path=bg_img,
            user_id=user_id,
            group_id=group_id,
            data=dict(sender_user),
            is_sign=True
        )
        if is_ok:
            msg += MessageSegment.image(file=sign_img_file)
            return msg
        # 处理图片生成失败的情况
        msg += Message("你今天已经签到了，明天再来吧！")
        return msg
    

    # 签到名次
    sign_num = await UserTable.filter(group_id=group_id, last_sign=today).count() + 1

    # 设置签到
    data = await UserTable.sign_in(
        user_id=user_id,
        group_id=group_id,
    )


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
        msg_txt = MessageSegment.at(user_id = user_id)
        msg_txt += f"\n本群第 {sign_num} 位 签到完成\n"
        # msg_txt += f"获得金币：+{data.today_gold} (总金币：{data.all_gold})\n"
        # msg_txt += f"获得牛力值：+{data.today_charm}（总牛力：{data.all_charm}）\n"
        msg_txt += f"累计签到次数：{data.sign_count}\n"
        msg_txt += f"连续签到次数：{data.days_count}\n"
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
        print(f"file: {file}")
        # TOTO 现在能直接拿到可显示的图片地址，不需要调用api
        # result = await bot.call_api("get_image", file=file)
        # logger.debug(f"result: {result}")
        # file_url = result["url"]
        file_url = file
        if file_url:
            user.bg_img = file_url
            await user.save(update_fields=['bg_img'])
            # 将背景保存在本地
            bg_name = f'{user_id}_{group_id}.jpg'
            os.makedirs(cache_directory, exist_ok=True)
            cache_path = os.path.join(cache_directory, bg_name)
            response = httpx.get(file_url)
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
async def change_s_title(bot: Bot, gid: int, uid: int, title: Optional[str]):
    """
    改头衔
    # TODO pc 协议目前不支持修改头衔
    :param bot: bot
    :param gid: 群号
    :param uid: 用户号
    :param s_title: 头衔
    """
    try:
        await bot.set_group_special_title(
            group_id=gid,
            user_id=uid,
            special_title=title,
            duration=-1,
        )
        return f'头衔修改成功：{title}'
    except ActionFailed:
        logger.info('权限不足')
        return '头衔修改失败：权限不足'
  