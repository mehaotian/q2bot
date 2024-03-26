from io import BytesIO
import os
import random
import requests
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
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


class TxtToImg:
    def __init__(self) -> None:
        pass

    def run(
        self,
        font_path="",
        bg_image_path="",
        nickname="",
        sign_num=1,
        today_gold=0,
        all_gold=0,
        today_charm=0,
        all_charm=0,
        bg_name="",
    ) -> bytes:
        """将文本转换为图片"""
        title_font = ImageFont.truetype(font_path, 32)
        date_font = ImageFont.truetype(font_path, 48)
        lines_space = 8

        # 这是不要背景 ，纯文字
        image = Image.new("RGBA", (500, 730), '#ffffff')
        tempurl = str(bg_image_path)
        if tempurl.startswith("http") or tempurl.startswith("https"):
            cache_path = os.path.join(cache_directory, bg_name)
            print(f"cache_path: {cache_path}")
            background_image = download_image(bg_image_path, cache_path)
            if not background_image:
                return False, '设置背景图失败，请重试'
        else:
            background_image_path = Path("resource") / bg_image_path
            background_image = Image.open(background_image_path)

        logger.debug(f"background_image: {background_image}")
        # 目标显示区域的尺寸
        img_width = 500
        img_height = 300

        # 创建一个新的RGBA图像，大小为目标显示区域的尺寸
        output_image = Image.new(
            "RGBA", (img_width, img_height), (255, 255, 255, 0))

       # 获取传入图片的宽度和高度
        original_width, original_height = background_image.size

        # 计算原始图像的宽高比
        aspect_ratio = original_width / original_height

        # 计算目标显示区域的宽高比
        target_aspect_ratio = img_width / img_height

        if aspect_ratio > target_aspect_ratio:
            # 如果原始图像较宽，则根据目标高度进行等比缩放
            new_width = int(img_height * aspect_ratio)
            new_height = img_height
        else:
            # 如果原始图像较高，则根据目标宽度进行等比缩放
            new_width = img_width
            new_height = int(img_width / aspect_ratio)

        # 缩放图片
        resized_image = background_image.resize(
            (new_width, new_height), Image.ANTIALIAS)

        # 计算图片在目标显示区域内的位置，使其居中
        x_offset = (img_width - new_width) // 2
        y_offset = (img_height - new_height) // 2

        # 将调整后的图片粘贴到输出图像中，以居中显示
        output_image.paste(resized_image, (x_offset, y_offset))

        image.paste(output_image, (0, 0))

        draw_table = ImageDraw.Draw(image)

        text_width, _ = draw_table.textsize('09/07', date_font)
        # 文字距离右边 20 的距离
        margin = img_width - text_width - 20
        # 今天的日期
        locale.setlocale(locale.LC_TIME, 'zh_CN.UTF-8')
        today = date.today()
        # 获取星期几（0表示星期一，1表示星期二，以此类推）
        weekday = today.strftime("%A")

        # 获取月份和日期
        month_day = today.strftime("%m/%d")

        draw_table.text(xy=(20, 330), text=f'{weekday}', fill="#000",
                        font=date_font, spacing=lines_space)
        draw_table.text(xy=(margin, 330), text=f'{month_day}', fill="#000",
                        font=date_font, spacing=lines_space)

        max_length = 13
        if len(nickname) > max_length:
            nickname = nickname[:max_length - 3] + "..."

        current_time = datetime.datetime.now().time()

        if current_time < datetime.time(12, 0):
            time_period = "上午"
        elif current_time < datetime.time(14, 0):
            time_period = "中午"
        elif current_time < datetime.time(18, 0):
            time_period = "下午"
        elif current_time < datetime.time(22, 0):
            time_period = "晚上"
        else:
            time_period = "凌晨"

        draw_table.text(xy=(20, 410), text=f'{time_period}好，{nickname}', fill="#000",
                        font=title_font, spacing=lines_space)

        draw_table.text(xy=(20, 470), text=f'本群第 {sign_num} 位签到完成', fill="#6d786f",
                        font=title_font, spacing=lines_space)
        draw_table.text(xy=(20, 520), text=f'今日签到获取金币：+{today_gold}', fill="#6d786f",
                        font=title_font, spacing=lines_space)
        draw_table.text(xy=(20, 570), text=f'今日签到获取魅力值：+{today_charm}', fill="#6d786f",
                        font=title_font, spacing=lines_space)
        draw_table.text(xy=(20, 620), text=f'你共持有金币：{all_gold}', fill="#6d786f",
                        font=title_font, spacing=lines_space)
        draw_table.text(xy=(20, 670), text=f'当前拥有魅力值：{all_charm}', fill="#6d786f",
                        font=title_font, spacing=lines_space)

        img_byte = BytesIO()
        image.save(img_byte, format="PNG")

        return True, img_byte


def sign_in_2_img(
        bg_path='',
        nickname="",
        sign_num=1,
        today_gold=0,
        all_gold=0,
        today_charm=0,
        all_charm=0,
        bg_name="",
):
    font_path = str(static_path / "KNMaiyuan-Regular.ttf")
    text = TxtToImg()
    if not bg_path:
        # 随机 1 -5
        num = random.randint(1, 5)

        bg_path = sgin_bg_path / f'bg-{num}.jpeg'

    return text.run(
        font_path=font_path,
        bg_image_path=bg_path,
        nickname=nickname,
        sign_num=sign_num,
        today_gold=today_gold,
        all_gold=all_gold,
        today_charm=today_charm,
        all_charm=all_charm,
        bg_name=bg_name,
    )
