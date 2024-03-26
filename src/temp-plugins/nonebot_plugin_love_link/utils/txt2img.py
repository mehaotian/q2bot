from io import BytesIO
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from ..config import text_bg_path, static_path


def create_bordered_image(image, border_image, size=80):
    # 计算图片的宽度和高度
    image_width, image_height = image.size

    # 计算边角、边线和中间部分的大小
    border_width, border_height = border_image.size
    # middle_size = (image_width - 2 * size, image_height - 2 * size)

    # 切片边框素材，得到4个角、4个边线和中间部分的图像
    top_left = border_image.crop((0, 0, size, size))
    top_right = border_image.crop(
        (border_width - size, 0, border_width, size))
    bottom_left = border_image.crop(
        (0, border_height - size, size, border_height))
    bottom_right = border_image.crop(
        (border_height - size, border_height - size, border_width, border_height))
    top_line = border_image.crop(
        (size, 0, border_width - size, size))
    bottom_line = border_image.crop(
        (size, border_height - size, border_width - size, border_height))
    left_line = border_image.crop(
        (0, size, size, border_width - size))
    right_line = border_image.crop(
        (border_width - size, size, border_width, border_height - size))

    # 调整并放置4个边线的图像
    top_line = top_line.resize(
        (image_width - 2 * size, size))
    bottom_line = bottom_line.resize((image_width - 2 * size, size))
    left_line = left_line.resize((size, image_height - 2 * size))
    right_line = right_line.resize((size, image_height - 2 * size))

    # 创建新的图像对象，并将各个部分的图像粘贴到对应位置
    bordered_image = Image.new('RGBA', (image_width, image_height))

    bordered_image.paste(top_line, (size, 0))
    bordered_image.paste(
        bottom_line, (size, image_height - size))
    bordered_image.paste(left_line, (0, size))
    bordered_image.paste(right_line, (image_width - size, size))

    bordered_image.paste(top_left, (0, 0))
    bordered_image.paste(top_right, (image_width - size, 0))
    bordered_image.paste(bottom_left, (0, image_height - size))
    bordered_image.paste(bottom_right, (image_width -
                         size, image_height - size))

    return bordered_image


def get_msg_size(msg, font):
    """获取文字渲染后宽度"""
    size = []
    for t in msg:
        box = font.getbbox(t)
        size.append(box[2] - box[0])
    return size


def get_msg_height(msg, font):
    """获取文字渲染后高度"""
    size = []
    for t in msg:
        box = font.getbbox(t)
        size.append(box[3] - box[1])
    return size


class TxtToImg:
    def __init__(self) -> None:
        self.CHAR_SIZE = 50
        self.LINE_CHAR_COUNT = self.CHAR_SIZE * 2
        self.TABLE_WIDTH = 4

    def line_break(self, line: str) -> str:
        """将一行文本按照指定宽度进行换行"""
        ret = ""
        width = 0
        for c in line:
            if len(c.encode("utf8")) == 3:  # 中文
                if self.LINE_CHAR_COUNT == width + 1:  # 剩余位置不够一个汉字
                    width = 2
                    ret += "\n" + c
                else:  # 中文宽度加2，注意换行边界
                    width += 2
                    ret += c
            elif c == "\n":
                width = 0
                ret += c
            elif c == "\t":
                space_c = self.TABLE_WIDTH - width % self.TABLE_WIDTH  # 已有长度对TABLE_WIDTH取余
                ret += " " * space_c
                width += space_c
            else:
                width += 1
                ret += c
            if width >= self.LINE_CHAR_COUNT:
                ret += "\n"
                width = 0
        return ret if ret.endswith("\n") else ret + "\n"

    def run(
        self, text: str, font_size=16, font_path="", bg_image_path="", size=80
    ) -> bytes:
        """将文本转换为图片"""
        d_font = ImageFont.truetype(font_path, font_size)

        text = self.line_break(text)

        # 将字符串按换行符分割成列表
        lines = text.split("\n")
        # 获取长度最长的一项
        longest_line = max(lines, key=len)
        # 字数
        # num_words = len(longest_line)
        font_len = get_msg_size(longest_line, d_font)
        line_heights = []
        for line in lines:
            if len(line) == 0:
                font_heights = [d_font.getsize('\n')[1]]
            else:
                font_heights = get_msg_height(line, d_font)
            line_heights.append(max(font_heights))

        lines_space = 8
        img_width = sum(font_len) + 80
        img_height = sum(num + lines_space for num in line_heights) + 52

        if img_height < size*2:
            img_height = size*2

        # image = Image.new("RGBA", (img_width, img_height), '#333333')
        # 这是不要背景 ，纯文字
        image = Image.new("RGBA", (img_width, img_height), '#ffffff')

        if bg_image_path:

            background_image_path = Path("resource") / bg_image_path

            background_image = Image.open(background_image_path)

            # 获取原始图片的宽度和高度
            original_width, original_height = background_image.size

            # 计算缩放比例
            scale = img_width / original_width

            # 计算缩放后的高度
            target_height = int(original_height * scale)

            # 调整边框素材的尺寸
            background_image.thumbnail((img_width, target_height))

            bg = create_bordered_image(image, background_image, size=size)
            overlay_image = bg.convert("RGBA")

            image.paste(bg, (0, 0), mask=overlay_image)

        draw_table = ImageDraw.Draw(image)
        # draw_table.text(xy=(40, 40), text=text, fill="#ffffff",
        #                 font=d_font, spacing=lines_space)
        # 这是不要背景 纯文字
        draw_table.text(xy=(40, 40), text=text, fill="#000",
                        font=d_font, spacing=lines_space)
        img_byte = BytesIO()
        image.save(img_byte, format="PNG")
        # base64_str = "base64://" + base64.b64encode(img_byte.getbuffer()).decode()
        # return base64_str
        return img_byte


def txt2img(msg: str, font_size=16, bg_path="border-1.png", size=80):
    # font_path = str(Path() / "resource" / "KNMaiyuan-Regular.ttf")
    font_path = str(static_path / "KNMaiyuan-Regular.ttf")
    text = TxtToImg()

    # bg_path = text_bg_path / bg_path
    bg_path = ''

    return text.run(
        msg,
        font_size=font_size,
        font_path=font_path,
        bg_image_path=bg_path,
        size=size
    )


# async def main():
#     font_path = Path("src", "plugins", "nonebot_plugin_game_query", "msyh.ttc")
#     font_path = str(font_path)
#     msg = (
#         f'欢迎『牛爷爷』踏入江湖，江湖路漫漫，且行且珍惜！！欢迎『牛爷爷』踏入江湖，江湖路漫漫，且行且珍惜！！欢迎『牛爷爷』踏入江湖，江湖路漫漫，且行且珍惜！！\n'
#         f'◆ 等级：1级（1/100）\n'
#         f'◆ 称号：初入江湖\n'
#         f'◆ 金钱：0 金\n'
#         f'◆ 装备：小寡妇的红胖次\n'
#         f'◆ 天赋：牛子变大术\n'
#         f'◆ 状态：自由自在\n'
#         f'◆ 力量：5 \n'
#         f'◆ 敏捷：5\n'
#         f'◆ 智力：5\n'
#         f'◆ 体力：5\n'
#     )

#     txt_to_img = TxtToImg()
#     bg_path = Path("imgs", "1.png")
#     res = await txt_to_img.txt_to_img(msg, font_path=font_path, bg_image_path=bg_path)
#     with open("imgs/output.png", "wb") as f:
#         f.write(res)
