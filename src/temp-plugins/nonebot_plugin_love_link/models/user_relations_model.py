from pydantic import BaseModel

from random import randint
from datetime import date, timedelta

from tortoise import fields
from tortoise.models import Model

from nonebot.log import logger

from ..text2img.relation2img import relation2img

from ..utils.utils import use_item

# 导入插件方法
from nonebot_plugin_tortoise_orm import add_model

from .user_model import UserTable

#  添加模型
add_model("src.plugins.nonebot_plugin_love_link.models.user_relations_model")


class RelationData(BaseModel):
    """
    关系数据
    """
    # 关系
    relation: str
    # 最长关联天数
    relation_days: int
    # 最后关联时间
    last_relation: date
    # 连续关联天数
    streak: int


class UserRelationsTable(Model):
    # 自增 ID (Primary key)
    id = fields.IntField(pk=True, generated=True)
    # 用户 ID
    user_id = fields.IntField()
    # 群组 ID
    group_id = fields.IntField()
    # 关联用户ID
    relation_user_id = fields.IntField(default=0)
    # 关系
    relation = fields.CharField(max_length=255, default="")
    # 最长关联天数
    relation_days = fields.IntField(default=0)
    # 最后关联时间
    last_relation = fields.DateField(default=date(2000, 1, 1))
    # 连续关联天数
    streak = fields.IntField(default=0)

    class Meta:
        table = "user_relations_model"
        table_description = " 用户关系表"  # 可选

    @classmethod
    async def register_user_relation(cls, user_id: int, group_id: int, send_user_id: int, text):
        """
        注册用户关系
        :param user_id: 用户 ID
        :param group_id: 群组 ID
        :param send_user_id: 关联用户 ID
        :param text: 消息内容
        :return:
        """

        user, _ = await UserTable.get_or_create(
            user_id=user_id,
            group_id=group_id,
        )

        sender, _ = await UserTable.get_or_create(
            user_id=send_user_id,
            group_id=group_id,
        )

        _,msg = relation2img(user, sender)

        return False, msg

        # 自己的绑定关系
        status, uid = await cls.is_relation(user_id=user_id, group_id=group_id, sender_id=send_user_id)

        logger.debug(f"status 我: {status}")
        logger.debug(f"uid 我: {uid}")
        if uid != 0:
            sender_user = await UserTable.filter(user_id=uid, group_id=group_id).first()
            relation_user = await UserRelationsTable.filter(user_id=user_id, group_id=group_id).first()
            other_relation_user = await UserRelationsTable.filter(user_id=uid, group_id=group_id).first()
            if status == 1:  # 你已经绑定了对方
                return False, f'「{sender_user.nickname}」已经是你的{relation_user.relation}了，可不兴二婚啊！'
            elif status == 2:  # 你已经和xx绑定了关系
                return False, f'「{sender_user.nickname}」已经是你的{relation_user.relation}了，你这是想出轨吗？渣子～'
            elif status == 3:  # 对方已经和你绑定了关系
                return False, f'你已经是「{sender_user.nickname}」的{other_relation_user.relation}了，你忘了吗？'
            elif status == 4:  # 你已经被xx绑定了关系
                other_relation_user = await UserRelationsTable.filter(user_id=send_user_id, group_id=group_id).first()
                return False, f'「{sender_user.nickname}」已经是对方的{other_relation_user.relation}了，你没机会了呢！'
            elif status == 5:  # 其他人关联了我
                return False, f'你已经是「{sender_user.nickname}」的{other_relation_user.relation}了，你忘了吗？'
            elif status == 6:  # 其他人关联了对方
                return False, f'对方已经是「{sender_user.nickname}」的{other_relation_user.relation}了，抢一下？呵呵～'
            elif status == 0:  # 没有关联关系
                pass

        # 给自己绑定关系
        record, _ = await UserRelationsTable.get_or_create(
            user_id=user_id,
            group_id=group_id,
        )

        user = await UserTable.filter(user_id=user_id, group_id=group_id).first()
        sender = await UserTable.filter(user_id=send_user_id, group_id=group_id).first()

        success, success_rate = use_item(
            a_charm=user.charm,
            b_charm=sender.charm
        )

        print(f'绑定成功概率 {success_rate * 100:.2f}%')

        if not success:
            return False, f'你的魅力值不够，操作失败，成功率：{success_rate * 100:.2f}%'

        today = date.today()
        if record.last_relation == (today - timedelta(days=1)):
            record.streak += 1

        if record.streak > record.relation_days:
            record.relation_days = record.streak

        # 最后关联时间
        record.last_relation = today

        record.relation_user_id = send_user_id
        record.relation = text == '嫁' and '老公' or '老婆'

        await record.save(update_fields=["relation_user_id", "relation", "last_relation", "streak", "relation_days"])

        return True, RelationData(
            relation=record.relation,
            relation_days=record.relation_days,
            last_relation=record.last_relation,
            streak=record.streak,
        )

    @classmethod
    async def get_last_relation(cls, user_id: int, group_id: int, sender_user_id: int) -> date:
        """
        :说明: `get_last_sign`
        > 获取最近关联时间

        :参数:
          * `user_id: int`: 用户ID
          * `group_id: int`: 群ID

        :返回:
          - `date`: 关联日期
        """
        record, _ = await UserRelationsTable.get_or_create(
            group_id=group_id,
            user_id=user_id,
            relation_user_id=sender_user_id
        )
        return record.last_relation

    @classmethod
    async def is_relation(cls, user_id, sender_id, group_id) -> bool:
        """
        是否存在关系
        :param user_id: 用户 ID
        :return: bool
        """
        # 查询自己和对方是否已有关联关系
        user_relation = await UserRelationsTable.filter(
            user_id=user_id,
            group_id=group_id,
            last_relation=date.today(),
        ).first()

        sender_relation = await UserRelationsTable.filter(
            user_id=sender_id,
            group_id=group_id,
            last_relation=date.today(),
        ).first()

        if user_relation:
            if user_relation.relation_user_id == sender_id:
                # 我关联了对方
                return 1, sender_id
            else:
                # 我关联了别人
                return 2, user_relation.relation_user_id

        if sender_relation:
            if sender_relation.relation_user_id == user_id:
                # 对方关联了我
                return 3, sender_id
            else:
                # 对方关联了别人
                return 4, sender_relation.relation_user_id

        # 查询是否有其他人关联了我或对方
        others_relation_to_me = await UserRelationsTable.filter(
            relation_user_id=user_id,
            group_id=group_id,
            last_relation=date.today(),
        ).first()

        others_relation_to_sender = await UserRelationsTable.filter(
            relation_user_id=sender_id,
            group_id=group_id,
            last_relation=date.today(),
        ).first()

        if others_relation_to_me:
            # 其他人关联了我
            return 5, others_relation_to_me.user_id

        if others_relation_to_sender:
            # 其他人关联了对方
            return 6, others_relation_to_sender.user_id

        # 没有关联关系
        return 0, 0
