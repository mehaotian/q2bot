import httpx
from ..config import steam_base_url, global_config


class SteamApi:
    steam_key = global_config.steam_api_key
    base_url = steam_base_url

    def __init__(self):
        raise

    @classmethod
    async def post(cls, url, data, v=1):
        request_url = cls.base_url + url + f"/v000{v}/"
        request_data = {
            "key": cls.steam_key,
            **data
        }
        response = httpx.post(request_url, data=request_data)
        return response.json()

    @classmethod
    async def get(cls, url, data, v=1):
        request_url = cls.base_url + url + f"/v000{v}/"
        print('------', request_url)
        request_data = {
            "key": cls.steam_key,
            **data
        }

        print('------', request_data)
        response = httpx.get(request_url, params=request_data)
        print('------', response)
        return response.json()


class ISteamUser(SteamApi):
    def __init__(self):
        super().__init__()

    @classmethod
    async def ResolveVanityURL(cls, data):
        """
        通过自定义url获取steamid
        参数：
            - data.id: 自定义url
        返回：
            - response: json 数据
        """

        try:
            res = await cls.get(url="/ISteamUser/ResolveVanityURL", data=data)
            return res["response"]
        except Exception as e:
            print('------', e)
            return None


# 使用示例
# steam_user = SteamUser('your_steam_key')
# response = steam_user.ResolveVanityURL('get', {'vanityurl': 'your_vanity_url'})
