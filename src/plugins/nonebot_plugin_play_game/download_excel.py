# -*- coding: UTF-8 -*-
import json
import os
import re
import time
from datetime import datetime
from time import sleep
import click
import pandas as pd
import requests
from bs4 import BeautifulSoup
from .config import path


class TengXunDocument():

    def __init__(self, document_url, local_pad_id, cookie_value):
        # excel文档地址
        self.document_url = document_url
        # 此值每一份腾讯文档有一个,需要手动获取
        self.localPadId = local_pad_id
        self.headers = {
            'content-type': 'application/x-www-form-urlencoded',
            'Cookie': cookie_value
        }

    def get_now_user_index(self):
        """
        # 获取当前用户信息,供创建下载任务使用
        :return:
            # nowUserIndex = '4883730fe8b94fbdb94da26a9a63b688'
            # uid = '144115225804776585'
            # utype = 'wx'
        """
        response_body = requests.get(url=self.document_url, headers=self.headers, verify=False)
        parser = BeautifulSoup(response_body.content, 'html.parser')
        global_multi_user_list = re.findall(re.compile('window.global_multi_user=(.*?);'), str(parser))
        if global_multi_user_list:
            user_dict = json.loads(global_multi_user_list[0])
            print(user_dict)
            return user_dict['nowUserIndex']
        return False

    def export_excel_task(self, export_excel_url):
        """
        导出excel文件任务,供查询文件数据准备进度
        :return:
        """
        body = {
            'docId': self.localPadId, 'version': '2'
        }

        res = requests.post(url=export_excel_url,
                                      headers=self.headers, data=body, verify=False)
        data = res.json()
        if data['ret'] != 0:
            print('导出excel文件任务失败')
            return False

        operation_id = res.json()['operationId']
        return operation_id



    def download_excel(self, check_progress_url, file_name):
        """
        下载excel文件
        :return:
        """
        # 拿到下载excel文件的url
        start_time = time.time()
        file_url = ''
        while True:
            res = requests.get(url=check_progress_url, headers=self.headers, verify=False)
            progress = res.json()['progress']
            if progress == 100:
                file_url = res.json()['file_url']
                break
            elif time.time() - start_time > 30:
                print("数据准备超时,请排查")
                break
        if file_url:
            self.headers['content-type'] = 'application/octet-stream'
            res = requests.get(url=file_url, headers=self.headers, verify=False)
            # 到处路径
            file_path = os.path.join(path, file_name)
            print('+++',file_path)
            with open(file_path, 'wb') as f:
                f.write(res.content)
            print('下载成功,文件名: ' + file_name)
        else:
            print("下载文件地址获取失败, 下载excel文件不成功")


if __name__ == '__main__':
    # excel文档地址
    document_url = 'https://docs.qq.com/sheet/DQXpTb3hFaWdYWVZP'
    # 此值每一份腾讯文档有一个,需要手动获取
    local_pad_id = '300000000$AzSoxEigXYVO'
    # 打开腾讯文档后,从抓到的接口中获取cookie信息
    cookie_value = 'RK=mJBhiAdaNL; ptcz=b1530ddde136597ba3aa475c56610b86c260260a988a70be3e26daa7ff8b4f6f; pac_uid=1_490272692; iip=0; pgv_pvid=3438197087; o_cookie=490272692; tvfe_boss_uuid=9a362a0a7cb3012f; Qs_lvt_323937=1646925951%2C1646926044%2C1646926112%2C1677465460; Qs_pv_323937=1103086212578679300%2C3210383779049036300%2C3523104024217180000%2C3786009731175991300; _clck=0|1|fbd|0; fqm_pvqid=874d527b-ed06-4555-8a0f-85e572fa9e68; pgv_info=ssid=s6487206782; fqm_sessionid=d6ab485a-3c50-43e7-95c2-e45a97fca5be; traceid=b8aef0c620; TOK=b8aef0c620a6cca4; hashkey=b8aef0c6; uin=o0490272692; rv2=8009E0B62ACBD85C98C2F11F9F952D8164018C7E057D6C9F52; property20=F07A572EE35E56733ABCDA51151D31C444AAEB4BCA94C2050175F1C7D0AA9427344D982E14F77152; ES2=45f64f414c6f8046; optimal_cdn_domain=docs2.gtimg.com; low_login_enable=1; skey=@1ZpZLjDK8; luin=o0490272692; p_uin=o0490272692; p_luin=o0490272692; lskey=00010000dab45994cc649af1d6cf4edfe3642f6306b307a29f8c024ed8b0381aeb30829b617f77410634131b; pt4_token=bHsGf*1EyPFtkR6jI91ecw2zRlwjpbwmaYuIo1UO1-k_; p_skey=*SdjXLCKFUOW17BvblvMG0T-YgQv9T9QsweezgpkEDA_; p_lskey=0004000039fbcd2f2e90b801dcc4338ccd4ec12c3aa48a4ef29f7c988abf79fa15d781916514330faa6927ca; uid=144115210339728583; utype=qq; vfwebqq=fc5aedab276aa9b990d284bcc5b4ed5fab59f4462b76a522b4639aef89d5cefe89df6419d94b9fa7; DOC_QQ_APPID=101458937; DOC_QQ_OPENID=E2587F4C8EFDA67A72F4A6BA6B335E05; env_id=gray-no3; gray_user=true; DOC_SID=560daaae54164a98a5cce4b95dae0be45f42f62de993429d8cbcd7a21ac120c1; SID=560daaae54164a98a5cce4b95dae0be45f42f62de993429d8cbcd7a21ac120c1; uid_key=EOP1mMQHGixsVktCV3VBSm00RXNobHRuVG4yYmx1cktXbCthbDRabnRvN3Z0Q3AyTHFjPSJIr%2FpTFV0bsVIteLGWfwWhDyUoOh29VnJMNiXOzG1h%2FhRueRtPe7AI0UteSeA2esPBbhIxRT9WaL7mr1lIydf6yIk5MSFxK7UmKJHc0qkG; loginTime=1695359310151; backup_cdn_domain=docs2.gtimg.com; adtag=doc_list_new; fingerprint=2a3731faa1f249d890c1013ec86fbf0469; adtag=doc_list_new; clean_env=0'
    tx = TengXunDocument(document_url, local_pad_id, cookie_value)
    now_user_index = tx.get_now_user_index()
    # 导出文件任务url
    export_excel_url = f'https://docs.qq.com/v1/export/export_office?u={now_user_index}'
    # 获取导出任务的操作id
    operation_id = tx.export_excel_task(export_excel_url)
    check_progress_url = f'https://docs.qq.com/v1/export/query_progress?u={now_user_index}&operationId={operation_id}'
    file_name = f'鹅子屋.xlsx'
    tx.download_excel(check_progress_url, file_name)