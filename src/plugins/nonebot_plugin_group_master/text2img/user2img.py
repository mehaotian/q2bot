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
        nickname="",
        font_path="",
        bg_image_path="",
        data={},
        bg_name="",
    ) -> bytes:
        """将文本转换为图片"""
        title_font = ImageFont.truetype(font_path, 32)
        date_font = ImageFont.truetype(font_path, 48)
        lines_space = 8

        # 这是不要背景 ，纯文字
        image = Image.new("RGBA", (500, 760), '#ffffff')
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

        # 今天的日期
        locale.setlocale(locale.LC_TIME, 'zh_CN.UTF-8')
        today = date.today()

        # 获取月份和日期
        month_day = today.strftime("%m/%d")

        text_width, _ = draw_table.textsize(month_day, date_font)
        # 文字距离右边 20 的距离
        margin = img_width - text_width - 20

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

        draw_table.text(xy=(20, 330), text=f'{time_period}好', fill="#000",
                        font=date_font, spacing=lines_space)

        draw_table.text(xy=(margin, 330), text=f'{month_day}', fill="#000",
                        font=date_font, spacing=lines_space)

        max_length = 15
        if len(nickname) > max_length:
            nickname = nickname[:max_length - 3] + "..."
        draw_table.text(xy=(20, 400), text=f'{nickname}', fill="#ff4200",
                        font=title_font, spacing=lines_space)

        is_sgin = data.get("is_sgin", False)
        if is_sgin:
            draw_table.text(xy=(20, 450), text=f'今日已签到,么么哒～', fill="#6d786f",
                            font=title_font, spacing=lines_space)
        else:
            draw_table.text(xy=(20, 450), text=f'今日未签到,要不然签一个呢？', fill="#6d786f",
                            font=title_font, spacing=lines_space)

        sign_times = data.get("sign_times", 0)
        sgin_streak = data.get("sgin_streak", 0)
        logger.debug(f"data: {data}")

        draw_table.text(xy=(20, 500), text=f'连续签到：{sgin_streak} 天，累计：{sign_times} 天', fill="#6d786f",
                        font=title_font, spacing=lines_space)

        gold = data.get("gold", 0)
        draw_table.text(xy=(20, 550), text=f'拥有金币：{gold}', fill="#6d786f",
                        font=title_font, spacing=lines_space)

        charm = data.get("charm", 0)
        draw_table.text(xy=(20, 600), text=f'拥有魅力值：{charm}', fill="#6d786f",
                        font=title_font, spacing=lines_space)

        relation = data.get("relation", "")

        if relation:
            sender_name = data.get("sender_name", "")
            streak = data.get("streak", 0)

            draw_table.text(xy=(20, 650), text=f'今日群{relation}是「{sender_name}」', fill="#6d786f",
                            font=title_font, spacing=lines_space)
            draw_table.text(xy=(20, 700), text=f'你们已经连续在一起 {streak} 天了~！', fill="#6d786f",
                            font=title_font, spacing=lines_space)
        else:
            draw_table.text(xy=(20, 650), text=f'快去找个人做一日情侣吧~！', fill="#6d786f",
                            font=title_font, spacing=lines_space)

        img_byte = BytesIO()
        image.save(img_byte, format="PNG")

        return True, img_byte


def user2img(
    bg_path='',
    nickname="",
    data={},
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
        bg_name=bg_name,
        bg_image_path=bg_path,
        nickname=nickname,
        data=data,
    )
