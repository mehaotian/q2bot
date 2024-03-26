from pydantic import BaseModel, Extra
from pathlib import Path

class Config(BaseModel, extra=Extra.ignore):
    """Plugin Config Here"""


path = Path() / "data" / "play_game"
path.mkdir(exist_ok = True, parents = True)
document_url = 'https://docs.qq.com/sheet/DQXpTb3hFaWdYWVZP'
# 此值每一份腾讯文档有一个,需要手动获取
local_pad_id = '300000000$AzSoxEigXYVO'