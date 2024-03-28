from pydantic import BaseModel, Extra
from pathlib import Path
import random


class Config(BaseModel, extra=Extra.ignore):
    command_manager: dict = {
        'welcome': '欢迎',
    }


# 获取图片资源地址
re_img_path = Path() / 'resource' / 'imgs'

# 背景图片
# bg_file = re_img_path / 'bg.jpg'

# 进群随机问候语
greetings = [
    "等你好久啦！你终于来了~",
    "欢迎新朋友的加入！快跟大家打个招呼吖~",
    "这可让你来着了，整个群的小伙伴都在等你呢~",
    "欢迎欢迎，麦克风给你，说两句？",
]

# 匹配词库

# 随机返回欢迎语
def get_wel_word() -> str:
    return random.choice(greetings)

# 随机返回背景 图片
def get_bg_file() -> Path:
    # 定义图片文件的扩展名
    image_extensions = {".jpg", ".jpeg", ".png", ".gif"}
    # 获取目录下所有图片文件
    image_files = [f for f in re_img_path.glob('*') if f.suffix.lower() in image_extensions and f.is_file()]
    random_image_file = random.choice(image_files)
    return random_image_file

pc = Config()
