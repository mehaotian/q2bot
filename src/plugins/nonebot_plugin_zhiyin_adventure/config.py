import os
from pydantic import Extra, BaseModel
from pathlib import Path
from nonebot import get_driver


class Config(BaseModel, extra=Extra.ignore):
    """
    配置类
    """
    # 基础设置
    z_base_gold = 5  # 每次聊天的基础金币
    z_base_exp = 10  # 每次聊天的基础经验

current_directory = Path(__file__).resolve().parent

# 静态资源路径
static_path = current_directory / "resource"

text_bg_path = current_directory / "resource" / "imgs"

sgin_bg_path = current_directory / 'resource' / 'sgin-bg-imgs'

# 缓存目录
cache_dir = Path() / "roulette_cache_image"

# 获取 docker 地址
cache_directory = os.getenv('CACHE_DIR', cache_dir)

# 获取配置
global_config = get_driver().config
# 从 NoneBot 配置中解析出的插件配置
plugin_config = Config.parse_obj(global_config)


