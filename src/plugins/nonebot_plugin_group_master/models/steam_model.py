from tortoise import fields
from tortoise.models import Model
from tortoise.exceptions import DoesNotExist

# from .user_model import UserTable


class SteamTable(Model):

    # 自增 ID (Primary key)
    id = fields.IntField(pk=True, generated=True)
    # 用户qq
    user_id = fields.CharField(max_length=255)

    # steamid: 玩家的 Steam ID，这是一个唯一的数字，用于在 Steam 平台上标识玩家。
    steamid = fields.CharField(max_length=255)
    # # profileurl: 玩家的 Steam 社区资料的 URL。
    # profileurl = fields.CharField(max_length=255)
    # # 好友码
    # friendcode = fields.CharField(max_length=255)

    # # communityvisibilitystate: 社区可见状态，这个字段表示玩家的 Steam 社区资料的公开程度。
    # communityvisibilitystate = fields.IntField(default=0)
    # # profilestate: 资料状态，如果玩家设置了 Steam 社区资料，这个字段的值为 1。
    # profilestate = fields.IntField(default=0)
    # # personaname: 玩家的 Steam 昵称。
    # personaname = fields.CharField(max_length=255)
    # # commentpermission: 如果玩家允许其他人在其 Steam 社区资料上发表评论，这个字段的值为 1。
    # commentpermission = fields.IntField(default=0)
    # # profileurl: 玩家的 Steam 社区资料的 URL。
    # profileurl = fields.CharField(max_length=255)
    # # avatar: 玩家的 Steam 头像的 URL（小尺寸）。
    # avatar = fields.CharField(max_length=255)
    # # avatarmedium: 玩家的 Steam 头像的 URL（中等尺寸）。
    # avatarmedium = fields.CharField(max_length=255)
    # # avatarfull: 玩家的 Steam 头像的 URL（大尺寸）。
    # avatarfull = fields.CharField(max_length=255)
    # # avatarhash: 玩家的 Steam 头像的哈希值。
    # avatarhash = fields.CharField(max_length=255)
    # # lastlogoff: 玩家最后一次退出 Steam 的时间，这是一个 Unix 时间戳。
    # lastlogoff = fields.IntField(default=0)
    # # personastate: 玩家的在线状态，例如在线、离线、忙碌等。
    # personastate = fields.IntField(default=0)
    # # realname: 玩家的真实姓名，如果玩家在其 Steam 社区资料上公开了这个信息，这个字段就会有值。
    # realname = fields.CharField(max_length=255)
    # # primaryclanid: 玩家的主要 Steam 社区群组的 ID。
    # primaryclanid = fields.CharField(max_length=255)
    # # timecreated: 玩家的 Steam 账号创建时间，这是一个 Unix 时间戳。
    # timecreated = fields.IntField(default=0)
    # # personastateflags: 玩家的个人状态标志，这是一些关于玩家状态的额外信息。
    # personastateflags = fields.IntField(default=0)

    # 创建时间
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "steam_table"
        table_description = "steam 信息表"  # 可选

    @classmethod
    async def save_steam(cls, uid, steamid) -> "SteamTable":
        """
        保存 steam 数据
        :param uid: 用户唯一ID
        :param data: 数据
        """
        # instance, _ = await cls.get_or_create(user_id=uid)
        try:
            # 尝试获取一个已经存在的记录
            instance = await cls.get(user_id=uid)
            instance.steamid = steamid

            await instance.save(update_fields=['steamid'])
        except DoesNotExist:
            # 如果不存在，创建一个新的记录
            instance = await cls.create(user_id=uid, steamid=steamid)


       

        return instance
