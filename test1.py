# import requests
# import httpx
# file_url = "https://multimedia.nt.qq.com.cn/download?appid=1407&fileid=Cgk0OTAyNzI2OTISFKir4QiltIMZGSif4ym92_TjH47rGJ7nBCD_CijZ0J_ei5mFA1CAvaMB&rkey=CAQSMDScGYKkZS_GUFiN5T3WErsz7SotARK1Bbs2b0L8QRzh0f1K5truwGID8b92nejylg&spec=0"
# headers = {
#     "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
#     # 添加其他需要的 headers...
# }
# response = httpx.get(file_url)
# if response.status_code == 200:
#     print(response.content)


import os
from pathlib import Path

# 缓存目录
cache_directory = Path() / "cache_image"

bg_name = f'11111_2222.jpg'

cache_path = os.path.join(cache_directory, bg_name)

print(cache_path)