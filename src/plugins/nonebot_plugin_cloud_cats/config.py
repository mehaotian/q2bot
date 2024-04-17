import os
from pydantic import Extra, BaseModel
from pathlib import Path
from nonebot import get_driver

class Config(BaseModel, extra=Extra.ignore):
    """
    配置类
    """


current_directory = Path(__file__).resolve().parent

# 缓存目录
cache_dir = Path() / "cat_cache_image"

# 获取 docker 地址
cache_directory = os.getenv('CACHE_DIR', cache_dir)

# 静态资源路径
static_path = current_directory / "resource"

# text_bg_path = current_directory / "resource" / "imgs"


# 从 NoneBot 配置中解析出的插件配置
plugin_config = Config.parse_obj(get_driver().config)

# 获取配置
global_config = get_driver().config
