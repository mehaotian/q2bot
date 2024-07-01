import os
from pydantic import Extra, BaseModel
from pathlib import Path
from nonebot import get_driver


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

    steam_api_key = "CFBCDCA9ACBFDDACD0321DB2BA4BDBCB"



# 缓存目录
# cache_directory = Path() / "cache_image"
cache_dir = Path() / "cache_image"
cache_directory = Path(os.getenv('CACHE_DIR', cache_dir))
print('----- 图片缓存路径', cache_directory)
current_directory = Path(__file__).resolve().parent
# 静态资源路径
static_path = current_directory / "resource"

text_bg_path = current_directory / "resource" / "imgs"

sgin_bg_path = current_directory / "resource" / "sgin-bg-imgs"

# 从 NoneBot 配置中解析出的插件配置
plugin_config = Config.parse_obj(get_driver().config)
global_config = get_driver().config

if global_config.environment == 'dev':
    web_url = 'http://127.0.0.1:8080'
else:
    web_url = 'https://botapi.mehaotian.com'

# 签到基础点数
BASE = plugin_config.daily_sign_base

# 连续签到加成比例
MULTIPLIER = plugin_config.daily_sign_multiplier

# 最大幸运值
MAX_LUCKY = plugin_config.daily_sign_max_lucky

steam_base_url = 'http://api.steampowered.com'
