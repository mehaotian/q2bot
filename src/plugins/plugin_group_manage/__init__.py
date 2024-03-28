from nonebot import on_notice
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import Bot, GroupIncreaseNoticeEvent, MessageSegment, Message
from .welcome_utils.message_util import MessageBuild

from .config import pc, get_bg_file, get_wel_word

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
    bg_file = get_bg_file()

    try:
        greet_emoticon = MessageBuild.Image(
            bg_file, size=(300, 300), mode='RGBA')
        await bot.send_group_msg(group_id=event.group_id, message=Message(
            MessageSegment.at(event.user_id) + MessageSegment.text(f' {get_wel_word()}\n') + greet_emoticon))
    except Exception as e:
        print(e)
        pass
