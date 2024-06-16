import os
from pydantic import Extra, BaseModel
from pathlib import Path
from nonebot import get_driver


class Config(BaseModel, extra=Extra.ignore):
    """
    配置类
    """
    callback_notice: bool = True  # 是否在操作完成后在 QQ 返回提示
    ban_rand_time_min: int = 60  # 随机禁言最短时间(s) default: 1分钟
    ban_rand_time_max: int = 2591999  # 随机禁言最长时间(s) default: 30天: 60*60*24*30

current_directory = Path(__file__).resolve().parent

# 静态资源路径
static_path = current_directory / "resource"

text_bg_path = current_directory / "resource" / "imgs"

sgin_bg_path = current_directory / 'resource' / 'sgin-bg-imgs'

# 缓存目录
cache_dir = Path() / "roulette_cache_image"

# 获取 docker 地址
cache_directory = os.getenv('CACHE_DIR', cache_dir)

# 从 NoneBot 配置中解析出的插件配置
plugin_config = Config.parse_obj(get_driver().config)

# 获取配置
global_config = get_driver().config
