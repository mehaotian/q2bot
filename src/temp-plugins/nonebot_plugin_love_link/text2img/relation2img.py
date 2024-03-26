from io import BytesIO
import os
import random
import requests
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageFilter
from nonebot.log import logger
import datetime
from datetime import date
import locale
from ..config import sgin_bg_path, static_path, cache_directory


def download_image(url, cache_path):
    """
    下载文件并缓存
    """
    # 如果缓存目录不存在，则创建
    if not os.path.exists(cache_directory):
        os.makedirs(cache_directory)

    if os.path.exists(cache_path):
        logger.debug(f"缓存文件已存在: {cache_path}")
        # 如果缓存文件已存在，直接加载并返回
        with open(cache_path, "rb") as file:
            return Image.open(BytesIO(file.read()))
    else:
        logger.debug(f"缓存文件不存在: {cache_path}")
        # 否则下载远程图片，并保存到缓存目录
        response = requests.get(url)
        if response.status_code == 200:
            with open(cache_path, "wb") as file:
                file.write(response.content)
            return Image.open(BytesIO(response.content))
        else:
            # 处理下载失败的情况
            return None


def add_rounded_corners(image, radius):
    # 创建与图像相同大小的透明图像
    circle = Image.new('L', (radius * 2, radius * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, radius * 2, radius * 2), fill=255)

    # 创建一个与图像相同大小的透明图像，用于蒙板
    alpha = Image.new('L', image.size, 255)

    # 将蒙板粘贴到圆角图像的中心
    w, h = image.size
    alpha.paste(circle.crop((0, 0, radius, radius)), (0, 0))
    alpha.paste(circle.crop((0, radius, radius, radius * 2)), (0, h - radius))
    alpha.paste(circle.crop((radius, 0, radius * 2, radius)), (w - radius, 0))
    alpha.paste(circle.crop((radius, radius, radius * 2,
                radius * 2)), (w - radius, h - radius))

    # 将蒙板应用到图像上
    image.putalpha(alpha)

    return image


def draw_trapezoid(bg_img, size=(250, 100), postion='left', offset=50):
    """
    梯形图片
    """
    img_width, img_height = size

    # 放大尺寸
    scale_width = img_width * 3
    scale_height = img_height * 3

    output_image = Image.new(
        "RGBA", (scale_width, scale_height), (255, 255, 255, 0))

    # 创建绘图对象
    draw = ImageDraw.Draw(output_image)

    # 定义半梯形的左下角、右下角和顶部坐标
    if postion == 'left':
        site = [(0, 0),
                (scale_width-offset, 0),
                (scale_width, scale_height),
                (0, scale_height)]
    else:
        site = [(0, 0),
                (scale_width, 0),
                (scale_width, scale_height),
                (offset, scale_height)]

    # 绘制半梯形
    draw.polygon(
        site,
        fill="black",
        outline="red",
        width=2
    )

    # 打开要应用遮罩的图像
    image = Image.open(bg_img)

    # 调整图像大小以与目标图像相匹配
    # image = image.resize((scale_width, scale_height))
    # 获取传入图片的宽度和高度
    original_width, original_height = image.size

    # 计算原始图像的宽高比
    aspect_ratio = original_width / original_height

    # 计算目标显示区域的宽高比
    target_aspect_ratio = scale_width / scale_height

    if aspect_ratio > target_aspect_ratio:
        # 如果原始图像较宽，则根据目标高度进行等比缩放
        new_width = int(scale_height * aspect_ratio)
        new_height = scale_height
    else:
        # 如果原始图像较高，则根据目标宽度进行等比缩放
        new_width = scale_width
        new_height = int(scale_width / aspect_ratio)

    # 缩放图片
    resized_image = image.resize(
        (new_width, new_height), Image.ANTIALIAS)

    # 计算图片在目标显示区域内的位置，使其居中
    x_offset = (scale_width - new_width) // 2
    y_offset = (scale_height - new_height) // 2
    new_image = Image.new(
        "RGBA", (scale_width, scale_height), (255, 255, 255, 0))
    # 将调整后的图片粘贴到输出图像中，以居中显示
    new_image.paste(resized_image, (x_offset, y_offset))
    

    blurred_image = new_image.filter(ImageFilter.GaussianBlur(radius=15))

    # 创建透明的黑色图像
    mask = Image.new("RGBA", new_image.size, (0, 0, 0, 128))

    # 合成图片和遮罩
    final_image = Image.alpha_composite(blurred_image.convert("RGBA"), mask)

    # 将左侧图像作为遮罩应用于目标图像
    masked_image = ImageChops.composite(
        final_image, output_image, output_image)

    # 缩小图像到所需的尺寸
    desired_size = (img_width, img_height)
    img = masked_image.resize(desired_size, Image.ANTIALIAS)
    return img


class TxtToImg:
    def __init__(self) -> None:
        pass

    def run(
        self,
        font_path="",
        user_bg_path="",
        sender_bg_path="",
        user=None,
        sender=None,
    ) -> bytes:
        """将文本转换为图片"""
        title_font = ImageFont.truetype(font_path, 32)
        date_font = ImageFont.truetype(font_path, 48)
        lines_space = 8

        image = Image.new("RGBA", (500, 300), (255, 255, 255, 255))

        left_img = draw_trapezoid(user_bg_path, postion='left')
        right_img = draw_trapezoid(sender_bg_path, postion='right')

        output_image = Image.new(
            "RGBA", (500, 200), (255, 255, 255, 0))

        output_image.paste(left_img, (0, 0))
        output_image.paste(right_img, (250, 0))

        overlay_image = output_image.convert("RGBA")

        image.paste(output_image, (0, 0), mask=overlay_image)

        img_byte = BytesIO()
        image.save(img_byte, format="PNG")

        return True, img_byte


def relation2img(user, sender):
    font_path = str(static_path / "KNMaiyuan-Regular.ttf")
    text = TxtToImg()

    user_bg_path = user.bg_img
    sender_bg_path = sender.bg_img

    if not user_bg_path:
        # 随机 1 -5
        num = random.randint(1, 5)

        user_bg_path = sgin_bg_path / f'bg-{num}.jpeg'
    if not sender_bg_path:
        # 随机 1 -5
        num = random.randint(1, 5)

        sender_bg_path = sgin_bg_path / f'bg-{num}.jpeg'

    return text.run(
        font_path=font_path,
        user_bg_path=user_bg_path,
        sender_bg_path=sender_bg_path,
        user=user,
        sender=sender,
    )
