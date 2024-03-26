
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
    handle_query,
    handle_change_bg
)


require("nonebot_plugin_tortoise_orm")


__plugin_meta__ = PluginMetadata(
    name="nonebot_plugin_monopoly",
    description="大富翁",
    usage="",
    type="application",
    homepage="",
    config=Config,
    supported_adapters={"~onebot.v11"},
)

# 签到
sign = on_fullmatch("签到", priority=5, block=False)

#  签到
@sign.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    user_id = int(event.user_id)
    group_id = int(event.group_id)
    logger.debug(f"群 group_id: 用户 {user_id} 签到")
    msg = await handle_sign_in(user_id, group_id, event.sender)
    await risk_msg(bot=bot, event=event,  msg=msg)




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
