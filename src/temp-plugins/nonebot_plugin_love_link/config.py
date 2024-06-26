from nonebot import get_driver
from pydantic import Extra, BaseModel
from pathlib import Path

class Config(BaseModel, extra=Extra.ignore):
    """
    配置类
    """
    # 签到基础点数
    daily_sign_base: int = 100

    # 连续签到加成比例
    daily_sign_multiplier: float = 0.2

    # 最大幸运值
    daily_sign_max_lucky: int = 10

current_directory =  Path(__file__).resolve().parent

# 缓存目录
cache_directory = Path() / "cache_image"

# 静态资源路径
static_path = current_directory / "resource"

text_bg_path = current_directory / "resource" / "imgs"

sgin_bg_path = current_directory / "resource" / "sgin-bg-imgs" 

# 从 NoneBot 配置中解析出的插件配置
plugin_config = Config.parse_obj(get_driver().config)

# 签到基础点数
BASE = plugin_config.daily_sign_base

# 连续签到加成比例
MULTIPLIER = plugin_config.daily_sign_multiplier

# 最大幸运值
MAX_LUCKY = plugin_config.daily_sign_max_lucky


