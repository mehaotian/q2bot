
import locale
from nonebot import require
from nonebot.plugin import PluginMetadata
from .config import Config
from . import (
    welcome,
    say,
)

from .serivce.user_source import handle_sign_in

# 设置本地化
locale.setlocale(locale.LC_TIME, 'zh_CN.UTF-8')

print(locale.getlocale())


require("nonebot_plugin_tortoise_orm")

__plugin_meta__ = PluginMetadata(
    name="nonebot_plugin_monopoly",
    description="多功能群管",
    usage=f"",
    type="application",
    homepage="",
    config=Config,
    supported_adapters={"~onebot.v11"},
)

