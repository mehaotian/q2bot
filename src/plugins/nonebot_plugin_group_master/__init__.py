
import locale
from nonebot import require
from nonebot.plugin import PluginMetadata
from .config import Config
from . import (
    welcome
)

from .serivce.data_source import handle_sign_in
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

