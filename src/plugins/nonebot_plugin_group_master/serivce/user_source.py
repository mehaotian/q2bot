import os
from random import randint
import httpx
from datetime import date, timedelta
from nonebot.log import logger
# from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import Message, MessageSegment, GroupMessageEvent, Bot, ActionFailed
from typing import Optional
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
        msg_txt = MessageSegment.at(user_id=user_id)
        msg_txt += f"\n本群第 {sign_num} 位 签到完成\n"
        msg_txt += f"获得金币：+{data.today_gold} (总金币：{data.all_gold})\n"
        # msg_txt += f"获得牛力值：+{data.today_charm}（总牛力：{data.all_charm}）\n"
        msg_txt += f"累计签到次数：{data.sign_count}\n"
        msg_txt += f"连续签到次数：{data.days_count}\n"
        msg += MessageSegment.text(msg_txt)
    return msg


async def handle_is_supplement(user_id, group_id, sender):
    """
    补签信息获取
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
    # yesterday = today - timedelta(days=1)
    days_since_last_sign_in = (today - last_sign).days
    print('days_since_last_sign_in', days_since_last_sign_in)
    # 签到次数
    sign_count = sender_user.sign_count
    # 获取连续签到次数
    days_count = sender_user.days_count

    # 如果距离最近签到日期超过两天 ，今天没签到昨天也没签到，则则提示断签多少天
    if days_since_last_sign_in >= 2:
        return False, f'你已经超过{days_since_last_sign_in}天没有签到过了，无法补签，请先玩成今日签到'
    # 是否断签
    if sign_count == days_count:
        return False, '你没有断签，不需要补签'
    else:
        # 需要补签天数
        days = sign_count-days_count
        # 金币增加
        gold = sender_user.gold
        at = MessageSegment.at(user_id)

        if gold < 1000:
            return False, Message(f'金币不足，无法补签，补签最少需要1000金币，你的金币数量为{gold}个。')

        if sign_count < 10:
            return False, Message(f'签到天数小于10天，无法使用补签功能，你当前共签到{sign_count}天。')

        # 需要最低当前金币的50% 最高金币的80% ，且四舍五入
        use_gold = round(gold * (randint(50, 80) / 100))
        # print('gold',gold)
        # print('use_gold',use_gold)

        diff = days/(sign_count-1)
        # print('days',days)
        # print('sign_count',sign_count)
        # print('diff',diff)

        use_gold = round(use_gold * diff)

        return use_gold, f'你需要补签{days}天，消耗金币{use_gold}个（共 {gold}个），回复【1】补签，回复【2】取消补签。'


async def set_supplement(user_id, group_id, use_gold):
    """
    补签
    """
    sender_user, _ = await UserTable.get_or_create(
        user_id=user_id,
        group_id=group_id,
    )

    # 扣除签到金币
    sender_user.gold -= use_gold

    today = date.today()
    last_sign = sender_user.last_sign

    # 如果今天没签到，把最后签到日期设置为昨天
    if today != last_sign:
        sender_user.last_sign = today - timedelta(days=1)
    else:
        sender_user.last_sign = today

    # 补签
    # 签到次数
    sign_count = sender_user.sign_count
    # 获取连续签到次数
    sender_user.days_count = sign_count

    await sender_user.save(update_fields=['gold', 'last_sign', 'days_count'])

    return Message(f'补签成功，连续签到恢复为{sign_count}天，共签到{sign_count}天')


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
            # 如果 file 不是 http 或者https 开头的，那么就取 url
            if not file.startswith("http"):
                file = msg.data["url"]

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

async def get_users2signin(group_id: int):
    """
    获取签到用户的排行版数据
    """
    # 获取签到用户的排行版数据,获取前30个数据
    users = await UserTable.filter(group_id=group_id).order_by('-sign_count').limit(30).all()
    # users = await UserTable.filter(group_id=group_id).order_by('-sign_count').all()

    users_dict_list = [{"nickname": user.nickname, "avatar": user.avatar, "sign_count": user.sign_count} for user in users]
    # print('users', users)
    return users_dict_list

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
