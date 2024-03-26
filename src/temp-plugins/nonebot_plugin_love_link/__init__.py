
from nonebot import on_regex, require, on_fullmatch
from nonebot.params import RegexGroup
from nonebot.adapters.onebot.v11 import (
    Bot,
    Event,
    MessageSegment,
    GroupMessageEvent,
    Message,
)
from nonebot.adapters import MessageTemplate
from nonebot.plugin import PluginMetadata
from nonebot.log import logger

from .utils.txt2img import txt2img

from .config import Config
from nonebot.typing import T_State

from .serivce.data_source import (
    create_user,
    handle_sign_in,
    handle_marriage,
    handle_query,
    is_query_love,
    user_handle_divorce_success,
    user_handle_divorce_error,
    handle_change_bg
)


require("nonebot_plugin_tortoise_orm")


__plugin_meta__ = PluginMetadata(
    name="nonebot_plugin_love_link",
    description="摸摸牛子",
    usage="",
    type="application",
    homepage="",
    config=Config,
    supported_adapters={"~onebot.v11"},
)

# 签到
sign = on_fullmatch("签到", priority=5, block=False)
# 嫁娶
marriageReg = r"^\s*(拔|拽|扯|薅|揪|抻|掏|拿|抓)\s*\[CQ:at,qq=(\d+)\]\s*$"
marriage = on_regex(marriageReg, priority=20, block=True)
# 查询
query = on_fullmatch("查询", priority=5, block=False)
# 离婚｜分手｜闹离婚｜结束｜不搞了
divorceReg = r"^\s*(自断牛牛|牛牛断开)\s*$"
divorce = on_regex(divorceReg, priority=20, block=True)

# 替换背景图
replace_bg = on_fullmatch("换背景", priority=5, block=False)


#  签到
@sign.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    user_id = int(event.user_id)
    group_id = int(event.group_id)
    logger.debug(f"群 group_id: 用户 {user_id} 签到")
    msg = await handle_sign_in(user_id, group_id, event.sender)
    # logger.debug(f"msg: {msg}")
    # await sign.finish(msg, at_sender=True)
    await risk_msg(bot=bot, event=event,  msg=msg)


# 嫁娶操作
@marriage.handle()
async def marriage_handle(bot: Bot, event: GroupMessageEvent, args=RegexGroup()):

    message = event.message

    # 获取消息内容
    text = message.extract_plain_text().strip()

    user_id = int(event.user_id)
    group_id = int(event.group_id)
    user = event.sender

    #  获取 at 用户的 qq
    to_user = [msg.data["qq"] for msg in message if msg.type == "at"]

    # 查询是否存在用户
    if send_user := to_user[0]:
        logger.debug(f"send_user: {send_user}")
        # 获取关联者用户信息
        result = await bot.call_api("get_group_member_info", group_id=group_id, user_id=send_user, no_cache=True)
        logger.debug(f"result: {result}")

        msg = await handle_marriage(
            bot=bot,
            user=user,
            user_id=user_id,
            send_user=result,
            group_id=group_id,
            text=text
        )
        await marriage.finish(msg, at_sender=True)
    else:
        return await marriage.finish("格式错误，你检查后重新输入指令", at_sender=True)

@query.handle()
async def query_handle(bot: Bot, event: GroupMessageEvent):
    """
    查询自己的信息
    """
    user_id = int(event.user_id)
    group_id = int(event.group_id)
    logger.debug(f"群 group_id: 用户 {user_id} 查询信息")
    msg = await handle_query(user_id, group_id, event.sender)
    # await sign.finish(msg, relpy=True)
    await risk_msg(bot=bot, event=event,  msg=msg)

# 分手
ok_text = '必须分开，这个没得考虑了，不行也得行，我过不下去了，我要分手，我要离婚，哼'


@divorce.handle()
async def _(state: T_State, event: GroupMessageEvent):
    message_id = event.message_id
    user_id = int(event.user_id)
    group_id = int(event.group_id)

    is_love = await is_query_love(user_id, group_id)

    # 没有绑定情侣
    if not is_love:
        await divorce.finish('你在想什么？你不是个单身狗吗？', at_sender=True)

    at = MessageSegment.reply(message_id)

    # 提问
    ask_text = (
        f'情缘充满曲折，不可多得，你确定真的要分开吗？\n\n'
        f'回复 「{ok_text}」 将结束你们的情缘,并扣除你100点魅力值。\n\n'
        f'回复 “我错了” 将取消本次操作，不过仍要扣除你10点魅力值，当做祸从口出的惩罚。\n\n'
        f'有些话不要随便说出口。'
    )

    img = txt2img(msg=ask_text)
    img_data = MessageSegment.image(file=img)
    state['reply_msg'] = Message(f'{at}{img_data}')
    state['user_id'] = user_id
    state['group_id'] = group_id


@divorce.got("msg",  prompt=MessageTemplate('{reply_msg}'))
async def handle_divorce(state: T_State, msg: Event):
    """
    分手
    """
    msgdata = msg.get_message()

    msgdata = msgdata.extract_plain_text().strip()
    # 同意
    if msgdata == ok_text:
        # await divorce.finish("你们已经分手了", at_sender=True)
        msg = await user_handle_divorce_success(user_id=state['user_id'], group_id=state['group_id'])
        await divorce.finish(msg, at_sender=True)

    # 不同意
    elif msgdata == "我错了":
        # await divorce.finish("你们还是好好过日子吧", at_sender=True)
        msg = await user_handle_divorce_error(user_id=state['user_id'], group_id=state['group_id'])
        await divorce.finish(msg, at_sender=True)
    else:
        send_count = state.get("send_count", 1)
        state["send_count"] = send_count + 1
        if send_count >= 3:
            await divorce.finish("错误次数过多，已取消")

        await divorce.reject("输入错误，请按照提示输入")


@replace_bg.handle()
async def _(bot: Bot, state: T_State, event: GroupMessageEvent):
    """
    替换背景图前置
    """
    user_id = int(event.user_id)
    group_id = int(event.group_id)

    state['user_id'] = user_id
    state['group_id'] = group_id
    await create_user(user_id, group_id, event.sender)



@replace_bg.got("bg", prompt="请发送一张图片")
async def _(bot: Bot, state: T_State, event: Event):
    """
    替换背景图
    """
    sender = event.sender

    logger.debug(f"sender: {sender}")

    message = event.get_message()
    logger.debug(f"message: {message}")
    msgdata = message.extract_plain_text().strip()

    if msgdata == '取消':
        await divorce.finish('已经取消替换背景图', at_sender=True)
    else:
        is_ok, msg = await handle_change_bg(
            bot=bot,
            user_id=state['user_id'],
            group_id=state['group_id'],
            message=message,
            sender=sender
        )
        if is_ok:
            await divorce.finish(msg, at_sender=True)
            return 
        else:
            send_count = state.get("send_count", 1)
            state["send_count"] = send_count + 1
            if send_count >= 3:
                await divorce.finish("错误次数过多，已取消")

            await divorce.reject(msg+'，输入「取消」中断当前操作')

    # await replace_bg.finish(msg, at_sender=True)


async def risk_msg(bot: Bot, event, msg, reply=False, at_sender=False):
    """
    被风控转为 图片发送
    :param bot: Bot 机器人对象
    :param event: 事件
    :param msg: 消息
    :param reply_id: 回复消息 ID
    :param at_id: at 用户 ID
    """
    try:
        # 未封控发送文本
        await bot.send(event=event, message=msg, reply_message=reply, at_sender=at_sender)

    except Exception as err:
        if "retcode=100" in str(err):
            # 风控尝试发送图片
            try:
                img = txt2img(msg=msg)
                img_data = MessageSegment.image(file=img)

                await bot.send(event=event, message=Message(img_data), reply_message=reply, at_sender=at_sender)

            except Exception as err:
                if "retcode=100" in str(err):
                    await bot.send(event, "消息可能被风控,无法完成发送!")
        else:
            await bot.send(event, f"发生了其他错误,报错内容为{err},请检查运行日志!")
