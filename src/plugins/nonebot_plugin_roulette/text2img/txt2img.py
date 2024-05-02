from io import BytesIO
import base64
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
# from .config import text_bg_path
from ..config import static_path
font_path = str(static_path / "KNMaiyuan-Regular.ttf")


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
    def __init__(self, linewidth=20) -> None:
        self.CHAR_SIZE = linewidth
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

        if ret.endswith("\n ") or ret.endswith("\n"):  # 如果最后一个元素是空字符或者换行符
            ret = ret[:-1]  # 移除最后一个字符
        return ret

    def run(
        self, text: str, font_size=16, margin=40
    ) -> bytes:
        """将文本转换为图片"""
        d_font = ImageFont.truetype(font_path, font_size)

        text = self.line_break(text)

        # 将字符串按换行符分割成列表
        lines = text.split("\n")
        # 获取长度最长的一项
        # longest_line = max(lines, key=len)
        longest_line = 0
        # font_len = 0
        print('lines:', lines)
        # 字数
        # 获取实际最长行的宽度
        for line in lines:
            if len(line) == 0:
                continue
            max_lens = get_msg_size(line, d_font)
            max_lens = sum(max_lens)
            if max_lens >= longest_line:
                longest_line = max_lens

        font_len = longest_line

        line_heights = []

        max_line_height = 0
        lines_space = 8
        for line in lines:
            if len(line) == 0:
                line = '\n'
            font_heights = d_font.getsize(line)[1]
            if max_line_height < font_heights:
                font_heights = font_heights
            line_heights.append(font_heights)

        img_width = font_len + margin*2
        img_height = sum(line_heights) + margin*2 + \
            lines_space*len(lines) - len(lines)*2

        image = Image.new("RGBA", (img_width, img_height), '#333333')

        draw_table = ImageDraw.Draw(image)
        draw_table.text(xy=(margin, margin), text=text,
                        fill="#ffffff", font=d_font, spacing=lines_space)

        img_byte = BytesIO()
        image.save(img_byte, format="PNG")

        return img_byte


def txt2img(msg: str, font_size=16, margin=15,width=20):
    text = TxtToImg(linewidth=width)
    return text.run(
        msg,
        font_size=font_size,
        margin=margin
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
