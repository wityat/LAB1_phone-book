import typing

from aiogram import types
from aiogram.dispatcher.filters import BoundFilter, CommandStart
from aiogram.dispatcher.filters.state import State
from aiogram.types import Message, CallbackQuery


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


class CustomStateFilter(BoundFilter):
    key = 'custom_state'

    def __init__(self, dispatcher, custom_state: State):
        self.state = custom_state
        self.dispatcher = dispatcher

    async def check(self, message: types.Message) -> typing.Optional[typing.Dict[str, typing.Any]]:
        # print("Состояние: ", self.custom_state.state if not isinstance(self.custom_state, str) else self.custom_state)
        current_state = await self.dispatcher.current_state().get_state()
        if '*' == self.state:
            return {"custom_state": self.state}
        elif isinstance(self.state, list):
            for state in self.state:
                if state.state == current_state:
                    return {"custom_state": state}
        elif current_state == self.state.state:
            return {"custom_state": self.state}
        return None
