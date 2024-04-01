from io import BytesIO
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from nonebot.log import logger
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


def adjust_image(image_path, target_width, target_height):
    """
    调整图片大小
    :param image_path: 图片路径
    :param target_width: 目标宽度
    :param target_height: 目标高度
    :return: 调整后的图片
    """
    # 打开图片
    img = Image.open(image_path)

    # 获取图片的原始宽度和高度
    original_width, original_height = img.size

    # 计算原始图像的宽高比
    aspect_ratio = original_width / original_height

    scaled_height = int(target_width / aspect_ratio)

    # 图片半高
    half_height = int(scaled_height // 2)

    # 缩放图片
    img = img.resize((target_width, scaled_height))

    # 创建一个新的RGBA图像，大小为目标显示区域的尺寸,作为处理图片再提
    new_img = Image.new("RGBA", (target_width, target_height))

    # 上图载体
    up_img = Image.new("RGBA", (target_width, scaled_height))
    up_img.paste(img, (0, 0))

    # 计算上部分裁剪区域的左上角和右下角坐标
    up_img = up_img.crop((0, 0, target_width, half_height))
    new_img.paste(up_img, (0, 0))

    # 下图载体
    down_img = Image.new("RGBA", (target_width, scaled_height))
    down_img.paste(img, (0, 0))

    # 计算下部分裁剪区域的左上角和右下角坐标
    down_img = down_img.crop(
        (0, half_height, target_width, scaled_height))
    new_img.paste(down_img, (0, int(target_height - half_height)))

    # 中图载体
    center_img = Image.new("RGBA", (target_width, scaled_height))
    center_img.paste(img, (0, 0))

    # 计算中部分裁剪区域的左上角和右下角坐标
    # 原图高于目标高度，中间需要补完
    if target_height > scaled_height:
        lower_center = half_height + 50
        center_img = center_img.crop(
            (0, half_height, target_width, lower_center))

        new_center_img = center_img.resize(
            (target_width, target_height - scaled_height))

        new_img.paste(new_center_img, (0, half_height))

    return new_img


def header_text(text_str, date_str, image, avatar_img):
    """
    绘制头部文字
    :param text: 文字
    :param image: 图片
    :return: 绘制后的图片
    """
    # 创建一个用于绘制的Draw对象
    draw = ImageDraw.Draw(image)

    # 创建一个红色的方形圆角框
    # 宽是 500  ，高是 100，居中显示
    box_width = 500
    margin = 80
    top = 40
    height = 100

    # 偏移 10 ，白色底层
    draw.rounded_rectangle(
        [(margin+10, top-10), (box_width-margin+10, height+top-10)],
        fill='#fff',
        outline='#4f562d',
        radius=10
    )

    # 偏移 10 ，绿色底层
    draw.rounded_rectangle(
        [(margin-10, top+40), (box_width-margin-10, height+top+40)],
        fill='#50b674',
        outline='#4f562d',
        radius=10
    )

    # 黄色正文
    draw.rounded_rectangle(
        [(margin, top), (box_width-margin, height+top)],
        fill='#f3d960',
        outline='#4f562d',
        radius=10
    )

    # 字体行距
    lines_space = 12

    # text_str 大于 13 个汉子，显示...
    if len(text_str) > 9:
        text_str = text_str[:9] + '...'

    text_str = f'@{text_str} 的逼话'
    content_font = ImageFont.truetype(font_path, 24)
    content_width, _ = content_font.getsize(text_str)
    left_margin = (box_width - content_width) / 2

    draw.text(xy=(left_margin, height+top+8), text=text_str,
              fill="#333", font=content_font, spacing=lines_space)
    draw.text(xy=(left_margin+1, height+top+7), text=text_str,
              fill="#fff", font=content_font, spacing=lines_space)

    top_font = ImageFont.truetype(font_path, 92)
    x = margin + 10
    y = top + 10

    text = date_str
    text_width, text_height = top_font.getsize(text)

    text_img = Image.new(
        "RGBA", (text_width, text_height+10), (255, 255, 255, 0))
    text_draw = ImageDraw.Draw(text_img)

    # 制作阴影效果
    # 描边效果
    text_draw.text(xy=(0, 3), text=text, fill="#f4362a",
                   font=top_font, spacing=lines_space)
    # 文字旋转

    text_draw.text(xy=(3, 0), text=text, fill="#fff",
                   font=top_font, spacing=lines_space)
    # 文字旋转
    rotated_text_img = text_img.rotate(10, expand=1)

    # 计算旋转后的文字应该被粘贴的位置
    paste_x = x + (text_width - rotated_text_img.width) / 2
    paste_y = y + (text_height - rotated_text_img.height) / 2
    image.paste(rotated_text_img, (int(paste_x),
                int(paste_y)), rotated_text_img)

    text = '逼话'
    bd_font = ImageFont.truetype(font_path, 78)
    bd_text_width, bd_text_height = top_font.getsize(text)

    bg_text_img = Image.new(
        "RGBA", (bd_text_width, bd_text_height+10), (255, 255, 255, 0))
    bg_text_draw = ImageDraw.Draw(bg_text_img)
    bg_text_draw.text(xy=(0, 3), text=text, fill="#fff",
                      font=bd_font, spacing=lines_space)
    bg_text_draw.text(xy=(3, 0), text=text, fill="#000",
                      font=bd_font, spacing=lines_space)

    image.paste(bg_text_img, (int(text_width + x + 15), int(y)), bg_text_img)

    # 渲染头像到 标题中间
    avatar_img = avatar_img.resize((60, 60))

    mask = Image.new('L', avatar_img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + avatar_img.size, fill=255)
    avatar_width, avatar_height = avatar_img.size
    top = int(top + 25)
    image.paste(avatar_img, ((box_width-avatar_width)//2, top), mask)
    # 创建一个边框
    draw = ImageDraw.Draw(image)
    left_x = (box_width-avatar_width)//2
    left_y = top
    right_x = left_x + avatar_width
    right_y = left_y + avatar_height
    draw.ellipse((left_x, left_y, right_x, right_y), outline='#333', width=1)

    # 保存图像
    return image


def content_text(data, image, position):
    """
    绘制内容文字
    :param data: 数据
    :param image: 图片
    :return: 绘制后的图片
    """
    x, y = position
    total_image_count = data.get('image_count', 0)
    total_face_count = data.get('face_count', 0)
    total_reply_count = data.get('reply_count', 0)
    total_at_count = data.get('at_count', 0)
    total_text_count = data.get('text_count', 0)
    total_recall_count = data.get('recall_count', 0)
    total_count = data.get('total_count', 0)

    text_data = (
        f'你叭叭打了 {total_text_count} 个字',
        f'库库发了 {total_image_count} 张图片',
        f'小表情发了 {total_face_count} 个',
        f'回复了其他人 {total_reply_count} 次',
        f'at 了别人 {total_at_count} 次',
        f'撤回了 {total_recall_count} 次消息',
        f'一共发送了 {total_count} 条消息，再接再厉！',
    )

    # 创建一个用于绘制的Draw对象
    width = 500
    margin = x
    text_img_width = width - margin * 2

    text_img_height = 40

    y += 5
    for index, text in enumerate(text_data):
        # 创建一个用于绘制的Draw对象
        text_image = Image.new("RGBA", (text_img_width, text_img_height))
        draw = ImageDraw.Draw(text_image)

        # # 字体行距
        lines_space = 12

        title_text = ImageFont.truetype(font_path, 20)

        text_width, text_height = title_text.getsize(text)
        text_x = (text_img_width - text_width) / 2
        text_y = (text_img_height - text_height) / 2
        draw.text(xy=(text_x, text_y), text=text, fill='#000',
                  font=title_text, spacing=lines_space)
        image.paste(text_image, (margin, y))
        y += text_img_height + 10


class TxtToImg:
    def __init__(self) -> None:
        pass

    def run(
        self,
        data={},
        date_str=""
    ) -> bytes:
        """将文本转换为图片"""
        bg_image_path = text_bg_path / f'bg-1.jpg'
        font = ImageFont.truetype(font_path, 14)
        lines_space = 8
        img_width = 500
        img_height = 620

        user = data.get('user', {})
        nickname = user.get('nickname', '')
        user_id = user.get('user_id', 0)

        bg_name = f'avatar_{user_id}.jpg'

        avatar_img = get_avatar_image(user.get('avatar', ''), bg_name)

        print(f"avatar_img: {avatar_img}")

        # 这是不要背景 ，纯文字
        image = Image.new("RGBA", (img_width, img_height), '#ffffff')

        background_image_path = Path("resource") / bg_image_path
        background_image = Image.open(background_image_path)

        logger.debug(f"background_image: {background_image}")

        # 创建一个新的RGBA图像，大小为目标显示区域的尺寸
        output_image = Image.new(
            "RGBA", (img_width, img_height), (255, 255, 255, 0))

        bg_img = adjust_image(background_image_path, img_width, img_height)

        # 将调整后的图片粘贴到输出图像中，以居中显示
        output_image.paste(bg_img, (0, 0))

        output_image = header_text(
            nickname, date_str, output_image, avatar_img)

        content_text(data, output_image, (80, 192))
        # output_image.paste(content_img, (80, 192))

        image.paste(output_image, (0, 0))

        img_byte = BytesIO()
        image.save(img_byte, format="PNG")

        return True, img_byte


def card2img(data={}, date_str=''):
    sayImg = TxtToImg()

    return sayImg.run(
        data=data,
        date_str=date_str
    )
