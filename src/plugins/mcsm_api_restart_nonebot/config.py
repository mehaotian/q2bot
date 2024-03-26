from nonebot import get_driver
from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    # 命令
    restart_nonebot_cmd: str = "重启nb"
    # mcsm的地址，格式如  http://127.0.0.1:23333
    restart_nonebot_host: str = ""  # 必填
    # 实例gid
    restart_nonebot_gid: str = ""  # 必填
    # 实例uid
    restart_nonebot_uid: str = ""  # 必填
    # api key
    restart_nonebot_key: str = ""  # 必填


driver = get_driver()
global_config = driver.config
pc = Config.parse_obj(global_config)
