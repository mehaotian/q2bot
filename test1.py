import httpx

# https://steamcommunity.com/profiles/76561198129564557/friends/add/
steam_key = "CFBCDCA9ACBFDDACD0321DB2BA4BDBCB"
steam_id = "76561198129564557"

# # 获取用户拥有的游戏
# owned_games_response = httpx.get(f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={steam_key}&steamid={steam_id}&format=json")
# # owned_games = owned_games_response.json().get('response').get('games')



# # 获取用户最近在玩的游戏
# recent_games_response = httpx.get(f"http://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v0001/?key={steam_key}&steamid={steam_id}&format=json")
# # recent_games = recent_games_response.json().get('response').get('games')

# print(recent_games_response.json())
# data = recent_games_response.json()
# # data = recent_games.json()

# # # 写入 json 文件中
# with open('owned_games.json', 'w',encoding='utf-8') as f:
#     f.write(str(data))



# 获取用户资料
# response = httpx.get(f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={steam_key}&steamids={steam_id}")

# data = response.json()

# with open('GetPlayerSummaries.json', 'w',encoding='utf-8') as f:
#     f.write(str(data))

# 获取好友列表
# response = httpx.get(f"http://api.steampowered.com/ISteamUser/GetFriendList/v0001/?key={steam_key}&steamid={steam_id}&relationship=friend")

# print(response)
# data = response.json()

# with open('GetFriendList.json', 'w',encoding='utf-8') as f:
#     f.write(str(data))

# 通过自定义url获取用户steam_id
# https://steamcommunity.com/id/2118263457
# customURL = "2118263457"

# response = httpx.get(f"http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key={steam_key}&vanityurl={customURL}")

# data = response.json()
# print(data)

# with open('GetFriendList.json', 'w',encoding='utf-8') as f:
#     f.write(str(data))


# GetPlayerSummaries：获取用户的公开信息，如个人资料名称、头像URL、在线状态等。

# URL: http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={API_KEY}&steamids={STEAM_ID}

# GetOwnedGames：获取用户拥有的游戏列表。

# URL: http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={API_KEY}&steamid={STEAM_ID}&format=json

# GetRecentlyPlayedGames：获取用户最近玩过的游戏列表。

# URL: http://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v0001/?key={API_KEY}&steamid={STEAM_ID}&format=json

# GetUserStatsForGame：获取用户在特定游戏中的统计数据。

# URL: http://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v0002/?appid={APP_ID}&key={API_KEY}&steamid={STEAM_ID}

# GetFriendList：获取用户的好友列表。

# URL: http://api.steampowered.com/ISteamUser/GetFriendList/v0001/?key={API_KEY}&steamid={STEAM_ID}&relationship=friend

# GetPlayerAchievements：获取用户在特定游戏中的成就。

# URL: http://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/?appid={APP_ID}&key={API_KEY}&steamid={STEAM_ID}


app_id = 250820 # SteamVR
# url = f"https://partner.steam-api.com/ISteamUser/GetFriendList/v1/?key={steam_key}&steamid={steam_id}&relationship=friends&format=json"
url = f"https://api.steampowered.com/ISteamWebAPIUtil/GetSupportedAPIList/v0001/?key={steam_key}"
response = httpx.get(url)

data = response.json()
print(data)

with open('GetSupportedAPIList.json', 'w',encoding='utf-8') as f:
    f.write(str(data))

# 获取当前ke用的所有公开api
# https://api.steampowered.com/ISteamWebAPIUtil/GetSupportedAPIList/v0001/?key=CFBCDCA9ACBFDDACD0321DB2BA4BDBCB