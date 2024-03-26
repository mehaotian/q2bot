import pandas as pd
import numpy as np
import json
from .config import path
import os


class Excel2Json():
    json_data = None
    def  __init__(self) -> None:
        try:
            # 读取 excel 文件
            file_path = os.path.join(path, '鸽子屋.xlsx')

            data = pd.read_excel(file_path,sheet_name='工作表1')

            json_data = data.to_json(orient='records')

            self.json_data = json.loads(json_data)

        except FileNotFoundError:
            # 处理文件未找到的情况
            print("找不到文件 '鸽子屋.xlsx'，请检查文件路径或提供正确的文件名。")
            self.json_data = None
        
def getJson ():
    return Excel2Json().json_data