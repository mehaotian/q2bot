from pydantic import BaseModel, Extra
from pathlib import Path

class Config(BaseModel, extra=Extra.ignore):
    """Plugin Config Here"""


path = Path() / "data" / "play_game"
path.mkdir(exist_ok = True, parents = True)
# 文档分享链接
# 鸽子屋
# document_url = 'https://docs.qq.com/sheet/DQXpTb3hFaWdYWVZP'
# 鹅子屋
# document_url = 'https://docs.qq.com/sheet/DSFRpdmt3V1RDUlVU'
document_url = 'https://docs.qq.com/smartsheet/DSFRpdmt3V1RDUlVU'
# 此值每一份腾讯文档有一个,需要手动获取
# local_pad_id = '300000000$AzSoxEigXYVO'
local_pad_id = '300000000$HTivkwWTCRUT'