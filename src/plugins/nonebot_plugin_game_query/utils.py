import json
from .config import *

# 小黑盒爬虫
def hey_box(page: int):
    # {str((page - 1) * 30)}
    url = f"https://api.xiaoheihe.cn/game/web/all_recommend/games/?os_type=web&version=999.0.0&show_type=discount&limit=30&offset="
    json_page = json.loads(other_request(url, headers=header).text)
    result_list = json_page["result"]["list"]
    result = []
    for i in result_list:
        price = i.get("price", {})
        heybox_price = i.get("heybox_price", {})
        is_lowest = price.get("is_lowest", 0) or heybox_price.get("is_lowest", 0)
        lowest_stat = "是史低哦" if is_lowest == 1 else "不是史低哦"
        discount = str(price.get("discount", "")) or str(heybox_price.get("discount", ""))
        
        new_lowest = price.get("new_lowest", " ")
        gameinfo = {
            "appid": str(i["appid"]),
            "链接": f"https://store.steampowered.com/app/{str(i['appid'])}",
            "图片": i["game_img"],
            "标题": i["game_name"],
            "原价": str(price["initial"]),
            "当前价": str(price["current"]),
            "平史低价": str(price.get("lowest_price", "无平史低价格信息")),
            "折扣比": discount,
            "是否史低": lowest_stat,
            "是否新史低": "好耶!是新史低!" if new_lowest == 1 else "不是新史低哦",
            "截止日期": price.get("deadline_date", "无截止日期信息"),
        }
        result.append(gameinfo)

    return result

# 消息主体拼接
def mes_creater(result, gamename):
    mes_list = []
    print(result[0].get("平台", ""))
    if result[0].get("平台", "") == "":
        content = f"    ***数据来源于小黑盒官网***\n***默认展示小黑盒steam促销页面***"
        for i in range(len(result)):
            mes = (
                f"[CQ:image,file={result[i]['图片']}]\n{result[i]['标题']}\n原价:¥{result[i]['原价']} \
                当前价:¥{result[i]['当前价']}(-{result[i]['折扣比']}%)\n平史低价:¥{result[i]['平史低价']} {result[i]['是否史低']}\n链接:{result[i]['链接']}\
                \n{result[i]['截止日期']}(不一定准确,请以steam为准)\n{result[i]['是否新史低']}\nappid:{result[i]['appid']}".strip()
                .replace("\n ", "")
                .replace("    ", "")
            )
            data = {"type": "node", "data": {
                "name": "sbeam机器人", "uin": "2854196310", "content": mes}}
            mes_list.append(data)
    else:
        content = f"***数据来源于小黑盒官网***\n游戏{gamename}搜索结果如下"
        for i in range(len(result)):
            if "非steam平台" in result[i]["平台"]:
                mes = f"[CQ:image,file={result[i]['其他平台图片']}]\n{result[i]['标题']}\n{result[i]['平台']}\n{result[i]['链接']} (请在pc打开,在手机打开会下载小黑盒app)".strip().replace(
                    "\n ", ""
                )
            elif "免费" in result[i]["原价"]:
                mes = mes = (
                    f"[CQ:image,file={result[i]['图片']}]\n{result[i]['标题']}\n原价:{result[i]['原价']}\n链接:{result[i]['链接']}\nappid:{result[i]['appid']}".strip(
                    )
                    .replace("\n ", "")
                    .replace("    ", "")
                )
            elif result[i]["折扣比"] == "当前无打折信息":
                mes = (
                    f"[CQ:image,file={result[i]['图片']}]\n{result[i]['标题']}\n{result[i]['折扣比']}\n当前价:¥{result[i]['当前价']} \
                        平史低价:¥{result[i]['平史低价']}\n链接:{result[i]['链接']}\nappid:{result[i]['appid']}".strip()
                    .replace("\n ", "")
                    .replace("    ", "")
                )
            else:
                mes = (
                    f"[CQ:image,file={result[i]['图片']}]\n{result[i]['标题']}\n原价:¥{result[i]['原价']} 当前价:¥{result[i]['当前价']}\
                        (-{result[i]['折扣比']}%)\n平史低价:¥{result[i]['平史低价']} {result[i]['是否史低']}\n链接:{result[i]['链接']}\n\
                            {result[i]['截止日期']}\n{result[i]['是否新史低']}\nappid:{result[i]['appid']}".strip()
                    .replace("\n ", "")
                    .replace("    ", "")
                )
            data = {"type": "node", "data": {
                "name": "sbeam机器人", "uin": "2854196310", "content": mes}}
            mes_list.append(data)
    announce = {"type": "node", "data": {
        "name": "sbeam机器人", "uin": "2854196310", "content": content}}
    mes_list.insert(0, announce)
    return mes_list