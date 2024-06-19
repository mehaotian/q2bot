from io import BytesIO
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from nonebot.log import logger
from itertools import islice
from ..config import text_bg_path, static_path

font_path = str(static_path / "KNMaiyuan-Regular.ttf")


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
    lower_center = half_height + 50
    center_img = center_img.crop((0, half_height, target_width, lower_center))

    new_center_img = center_img.resize(
        (target_width, target_height - scaled_height))

    new_img.paste(new_center_img, (0, half_height))

    return new_img


def header_text(text_str, image, textCount=None, top_text='TOP', top_title="榜单"):
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

    # if textCount:
    #     text_str = f'本月逼话 {textCount} 资格抽奖'

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

    text = top_text
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
    if textCount:
        text = '抽奖'
    else:
        text = top_title
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

    # 保存图像
    return draw


def content_text(data, index, height=40):
    """
    绘制内容文字
    :param data: 数据
    :param image: 图片
    :return: 绘制后的图片
    """
    user = data.get('users', {})
    nickname = user.get('nickname', '')
    # 获取总数
    total = data.get('total', 0)

    # 创建一个用于绘制的Draw对象
    width = 500
    margin = 80
    # 获取1的path
    bj1_path = text_bg_path / f'jp1.png'
    img_path = text_bg_path / f'jp0.png'

    if index < 3:
        img_path = text_bg_path / f'jp{index+1}.png'

    # 打开图片
    img = Image.open(img_path)
    # 将图片转换为"RGBA"模式
    img = img.convert("RGBA")

    box_img = Image.open(bj1_path)

    box_original_width, box_original_height = box_img.size
    # 计算奖牌原始图像的宽高比
    box_aspect_ratio = box_original_width / box_original_height
    box_height = height
    box_width = int(box_height * box_aspect_ratio)

    # 获取图片的原始宽度和高度
    original_width, original_height = img.size

    # 计算原始图像的宽高比
    aspect_ratio = original_width / original_height
    img_height = height

    if index == 1:
        img_height = height-5
    elif index == 2:
        img_height = height-10
    else:
        img_height = height

    img_width = int(img_height * aspect_ratio)

    img = img.resize((img_width, img_height))

    # 创建大小
    item_img = Image.new(
        "RGBA", (width - margin*2, height + 10), (255, 255, 255, 0))

    header_img = Image.new("RGBA", (box_width, box_height), (255, 255, 255, 0))

    x = (box_width - img_width) // 2
    y = (box_height - img_height) // 2
    header_img.paste(img, (x, y), img)

    item_img.paste(header_img, (0, 0))

    # 创建一个用于绘制的Draw对象
    draw = ImageDraw.Draw(item_img)

    # # 字体行距
    lines_space = 12

    size = 20 if index < 3 else 17
    title_text = ImageFont.truetype(font_path, size)

    text = nickname
    if index == 0:
        text = '[逼话王] ' + text
    sub_text = f'逼话 {total} 字'
    # 大于 13 个汉子，显示...
    if len(text) > 13:
        text = text[:13] + '...'
    if len(sub_text) > 19:
        sub_text = sub_text[:19] + '...'

    title_color = '#000' if index < 3 else '#666'

    draw.text(xy=(box_width + 10, 5), text=text, fill=title_color,
              font=title_text, spacing=lines_space)
    title_text = ImageFont.truetype(font_path, 15)
    draw.text(xy=(box_width + 10, 27), text=sub_text, fill="#666",
              font=title_text, spacing=lines_space)

    # 排行数字
    if index > 2:
        rank_text = ImageFont.truetype(font_path, 14)

        font_width, font_height = rank_text.getsize(str(index+1))
        font_x = (box_width - font_width) // 2
        font_y = (box_height - font_height) // 2
        draw.text(xy=(font_x, font_y-3), text=str(index+1), fill="#fff",
                  font=rank_text, spacing=lines_space)

    return item_img


class TxtToImg:
    def __init__(self) -> None:
        pass

    def run(
        self,
        data={},
        date_str='',
        textCount=None,
        top_text='TOP',
        top_title="榜单",
        title=""
    ) -> bytes:
        """将文本转换为图片"""
        bg_image_path = text_bg_path / f'bg-1.jpg'
        font = ImageFont.truetype(font_path, 14)
        if not title:
            title = f"{date_str}逼话排行榜"
        
        lines_space = 8
        img_width = 500
        # 最小基础高度，12条数据
        img_height = 870

        # 迭代次数
        lice = 15

        print('top_text', title)
        # 抽奖本月
        if top_title == '抽奖':
            if textCount and textCount > 0:
                data = [item for item in data if item.get('total', 0) >= textCount]
                lice = len(data)
            else:
                data = []

        # 活跃用户查询
        if top_text == '活跃':
            data = [item for item in data if item.get('total', 0) >= 0]
            lice = len(data)
            title += f'，共 {lice} 人'

        # 渲染列表的内容高度
        content_top = 192
        # 间距
        margin = 80
        # 单条内容高度
        content_height = 40
        margin_height = content_height + 10

        if lice > 12:
            lines_height = lice - 12
            img_height += (lines_height * margin_height)

        # 这是不要背景 ，纯文字
        image = Image.new("RGBA", (img_width, img_height), '#ffffff')

        background_image_path = Path("resource") / bg_image_path

        # 创建一个新的RGBA图像，大小为目标显示区域的尺寸
        output_image = Image.new(
            "RGBA", (img_width, img_height), (255, 255, 255, 0))

        bg_img = adjust_image(background_image_path, img_width, img_height)

        # 将调整后的图片粘贴到输出图像中，以居中显示
        output_image.paste(bg_img, (0, 0))

        for index, item in islice(enumerate(data), lice):
            content_img = content_text(item, index, content_height)
            output_image.paste(content_img, (margin, content_top), content_img)
            content_top += margin_height

        if len(data) < lice or lice == 0:
            draw = ImageDraw.Draw(output_image)
            text = '--- 虚位以待 ---'
            font_width, _ = font.getsize(text)
            draw.text(xy=((img_width-font_width)//2, content_top + 20), text=text, fill="#999",
                      font=font, spacing=lines_space)

        image.paste(output_image, (0, 0))



        header_text(text_str=title, image=image, textCount=textCount,
                    top_text=top_text, top_title=top_title)

        img_byte = BytesIO()
        image.save(img_byte, format="PNG")

        return True, img_byte


def say2img(data={}, date_str='', textCount=None, top_text='TOP', top_title="榜单", title=""):
    sayImg = TxtToImg()

    return sayImg.run(
        data=data,
        date_str=date_str,
        textCount=textCount,
        top_text=top_text,
        top_title=top_title,
        title=title
    )
