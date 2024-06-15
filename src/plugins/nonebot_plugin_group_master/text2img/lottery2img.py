from io import BytesIO
import os
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from nonebot.log import logger
import datetime
from datetime import date
from ..config import text_bg_path, static_path, cache_directory
from ..utils import download_image

font_path = str(static_path / "KNMaiyuan-Regular.ttf")


def get_avatar_image(tempurl, bg_name):
    """
    获取头像文件流
    """
    # 如果是网络图片，下载到本地，否则直接打开
    if tempurl.startswith("http") or tempurl.startswith("https"):
        cache_path = os.path.join(cache_directory, bg_name)
        print(f"cache_path: {cache_path}")
        background_image = download_image(tempurl, cache_path)
        print(f"background_image: {background_image}")
        if not background_image:
            return False
        return background_image


class TxtToImg:
    def __init__(self) -> None:
        pass

    def run(
        self,
        user=None,
    ) -> bytes:
        """
        将文本转换为图片
        :param font_path: 字体路径
        :param bg_image_path: 背景图片路径
        :param nickname: 昵称
        :param sign_num: 签到次数
        :param bg_name: 背景图片名称
        :param data: 签到用户数据
        """
        # --- 获取头像 ---
        user = user.get('users', {})
        print(f"user: {user}")
        nickname = user.get('nickname', '')
        user_id = user.get('user_id', 0)

        bg_name = f'avatar_{user_id}.jpg'

        avatar_img = get_avatar_image(user.get('avatar', ''), bg_name)

        print(f"avatar_img: {avatar_img}")

        # --- 制作背景图 ---
        bg_image_path = text_bg_path / f'lottery.jpg'
        img_width = 500

        background_image_path = Path("resource") / bg_image_path
        # 打开图片
        background_image = Image.open(background_image_path)

        # 获取图片的原始宽度和高度
        original_width, original_height = background_image.size

        # 计算原始图像的宽高比
        aspect_ratio = original_width / original_height

        img_height = int(img_width / aspect_ratio)

        # 缩放图片
        img = background_image.resize((img_width, img_height))

        # 创建一个新的RGBA图像，大小为目标显示区域的尺寸,作为处理图片再提
        new_img = Image.new("RGBA", (img_width, img_height))
        new_img.paste(img, (0, 0))

        # 主背景图载体
        image = Image.new("RGBA", (img_width, img_height), (255, 255, 255, 0))

        # 将调整后的图片粘贴到输出图像中，以居中显示
        image.paste(new_img, (0, 0))

        # --- 添加头像 ---
        avatar_img = avatar_img.resize((160, 160))

        avatar_mask = Image.new('L', avatar_img.size, 0)
        avatar_draw = ImageDraw.Draw(avatar_mask)
        avatar_draw.ellipse((0, 0) + avatar_img.size, fill=255)
        avatar_width, avatar_height = avatar_img.size

        top = 90
        # 将头像粘贴到输出图像中，以居中显示
        image.paste(avatar_img, ((img_width-avatar_width)//2, 90), avatar_mask)
        draw = ImageDraw.Draw(image)
        left_x = (img_width-avatar_width)//2
        left_y = top
        right_x = left_x + avatar_width
        right_y = left_y + avatar_height
        draw.ellipse((left_x, left_y, right_x, right_y),
                     outline='#fff', width=10)

        # --- 添加文字 ---
        text_str = f'@{nickname}'
        # 如果长度超过8 ，则截取7个并...
        if len(text_str) > 8:
            text_str = text_str[:7] + '...'

        text_height = 350
        lines_space = 8
        content_font = ImageFont.truetype(font_path, 48)
        content_width, _ = content_font.getsize(text_str)
        left_margin = (img_width - content_width) / 2

        draw.text(xy=(left_margin, text_height), text=text_str,
                  fill="#333", font=content_font, spacing=lines_space)
        draw.text(xy=(left_margin+1, text_height), text=text_str,
                  fill="#fff", font=content_font, spacing=lines_space)

        # --- 中奖文字 ---
        text_str = '喜中逼话奖！'
        content_font = ImageFont.truetype(font_path, 35)
        content_width, _ = content_font.getsize(text_str)
        left_margin = (img_width - content_width) / 2
        draw.text(xy=(left_margin+1, text_height + 215), text=text_str,
                  fill="#fff", font=content_font, spacing=lines_space)
        
        # --- 免责声明 ---
        text_str = '本次抽奖最终解释权归鹅子所有，请私聊抽奖者领取奖品'
        content_font = ImageFont.truetype(font_path, 20)
        content_width, _ = content_font.getsize(text_str)
        left_margin = (img_width - content_width) / 2
        draw.text(xy=(left_margin+1, img_height - 50), text=text_str,
                  fill="#fff", font=content_font, spacing=lines_space)


        img_byte = BytesIO()
        image.save(img_byte, format="PNG")

        return True, img_byte


def lottery2img(user):

    # 字体路径
    font_path = str(static_path / "KNMaiyuan-Regular.ttf")
    # 签到图片获取实例
    text = TxtToImg()

    try:
        is_ok, sign_img_file = text.run(user=user)
        return is_ok, sign_img_file
    except Exception as e:
        logger.error(f"抽奖图片生成失败: {e}")
        return False, None
