import nonebot
from nonebot.plugin import PluginMetadata
from .config import global_config, Config


from importlib import import_module

import_module('.models', __package__)
import_module('.core', __package__)


# su = global_config.superusers
# driver = nonebot.get_driver()


# @driver.on_bot_connect
# async def _(bot: nonebot.adapters.Bot):
#     pass


__plugin_meta__ = PluginMetadata(
    name="只因大冒险",
    description="Nonebot2 群管插件 插件",
    usage="只因大冒险，进化全靠吞",
    type="application",
    homepage="",
    config=Config,
    supported_adapters=None,
)


__usage__ = """
【初始化】：
  群管初始化 ：初始化插件

"""
__help_plugin_name__ = '简易群管'

__permission__ = 1
__help__version__ = '0.2.0'
