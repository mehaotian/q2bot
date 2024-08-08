from nonebot import on_notice
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import Bot, GroupIncreaseNoticeEvent, MessageSegment, Message
from .welcome_utils.message_util import MessageBuild

from .config import pc, get_bg_file, get_wel_word

import time
from datetime import datetime, timedelta

# 全局变量，存储上次执行的时间
last_execution_time = None


# 插件元信息
__plugin_meta__ = PluginMetadata(
    name="群管理",
    description="对群的基本管理功能，如入群欢迎，公告管理等",
    usage="进群自动欢迎",
    config=pc,
)

# 进群通知指令
notice_handle = on_notice(priority=5, block=True)

# 进群通知
@notice_handle.handle()
async def GroupNewMember(bot: Bot, event: GroupIncreaseNoticeEvent):
    global last_execution_time

    bg_file = get_bg_file()
    try:
        greet_emoticon = MessageBuild.Image(
            bg_file, size=(300, 300), mode='RGBA')
        
        

        await bot.send_group_msg(group_id=event.group_id, message=Message(
            MessageSegment.at(event.user_id) + MessageSegment.text(f' {get_wel_word()}\n')))
        
        current_time = datetime.now()
        if last_execution_time is None or (current_time - last_execution_time) > timedelta(minutes=2):

            text = (
                f"活动参与地址：\nhttps://steamcommunity.com/groups/bigoc/announcements/detail/4369140095299610749\n"
                f'\n加steam组并按活动规则留言，即参与活动成功'
            )

            await bot.send_group_msg(group_id=event.group_id, message=Message(text))

            qa = (
                f"你可能会遇到如下问题，请参考：\n"
                f'1. 显示地区不可用，尝试换加速器或者节点，steam日常抽风 \n'
                f'2. 关注后找不到留言的地方，查看是否只关注了鉴赏组，而没关注steam组 \n'
                f'3. 留言将暂时隐藏，出现这个提示，第二天看一看，如果还这样，联系鹅子做记录，也算成功参与'
            )

            await bot.send_group_msg(group_id=event.group_id, message=Message(qa))

            # 更新上次执行的时间
            last_execution_time = current_time

    except Exception as e:
        print(e)
        pass
