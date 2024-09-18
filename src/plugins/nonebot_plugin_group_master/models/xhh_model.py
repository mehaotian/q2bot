from tortoise import fields
from tortoise.models import Model
from tortoise.exceptions import DoesNotExist

# from .user_model import UserTable


class XhhTable(Model):

    # 自增 ID (Primary key)
    id = fields.IntField(pk=True, generated=True)
    # 用户qq
    user_id = fields.CharField(max_length=255)
    # 小黑盒
    xhh_id = fields.CharField(max_length=255)
    # 创建时间
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "xhh_table"
        table_description = "小黑盒 信息表"  # 可选

    @classmethod
    async def create_xhh_info(cls, uid, xid) -> "XhhTable":
        """
        创建小黑盒信息
        """
        user = await cls.get_or_none(user_id=uid)

        if user:
            await cls.filter(user_id=uid).update(xhh_id=xid)
            return user
        else:
            return await cls.create(user_id=uid, xhh_id=xid)
