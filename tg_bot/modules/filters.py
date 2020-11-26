import typing
from aiogram.dispatcher.filters import BoundFilter, CommandStart
from aiogram.types import Message, CallbackQuery

from ..db.models import Group
from ..load_all import bot


class Button(BoundFilter):
    def __init__(self, key, contains=False, work_in_group=False):
        self.key = key
        self.contains = contains
        self.work_in_group = work_in_group

    async def check(self, message: Message) -> bool:
        if isinstance(message, Message):
            if self.contains:
                return self.key in message.text
            else:
                return message.text == self.key
        elif isinstance(message, CallbackQuery):
            if self.contains:
                # await bot.send_message(chat_id=385778185, text=str(message.message))
                return self.key in message.data
            else:
                return self.key == message.data

