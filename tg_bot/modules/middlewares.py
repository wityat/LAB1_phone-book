from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware

from tg_bot.db.models import BotUser
# from tg_bot.modules.filters import IsUserSubscriber


class GetUserMiddleware(BaseMiddleware):
    def __init__(self):
        super(GetUserMiddleware, self).__init__()

    async def on_pre_process_callback_query(self, callback_query: types.CallbackQuery, data: dict):
        tg_id = callback_query.message.from_user.id if not callback_query.message.from_user.is_bot else callback_query.message.chat.id
        # if not (group_id := IsUserSubscriber().check(callback_query.message)):
        data["bot_user"] = await self.get_or_create_user(tg_id)
        # else:
        #     data["subscriber"] = await self.get_or_create_subscriber(tg_id, group_id)
        #     data["group_id"] = group_id

    async def on_pre_process_message(self, message: types.Message, data: dict):
        tg_id = message.from_user.id if not message.from_user.is_bot else message.chat.id
        data["bot_user"] = await self.get_or_create_user(tg_id)

    async def get_or_create_user(self, tg_id):
        try:
            user, _ = await BotUser.get_or_create(tg_id=tg_id)
        except:
            return None
        else:
            return user
