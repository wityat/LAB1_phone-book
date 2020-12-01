from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from aiogram.dispatcher.filters import CommandStart
from aiogram.utils.deep_linking import get_start_link

from ...db.models import BotUser, PhoneBookRow
from ...load_all import dp, bot
from . import texts, keyboards

from ...modules.filters import Button
from ...modules.edit_or_send_message import edit_or_send_message


async def menu(message: types.Message):
    await edit_or_send_message(bot, message, text=texts.menu(), kb=keyboards.menu())


@dp.message_handler(CommandStart(), state="*")
async def start(message: types.Message, state: FSMContext, bot_user: BotUser):
    await menu(message)


@dp.callback_query_handler(Button("menu"), state="*")
async def menu_(callback: types.CallbackQuery, bot_user: BotUser):
    await menu(callback.message)
    await callback.answer()


@dp.callback_query_handler(Button("all"), state="*")
async def all_(callback: types.CallbackQuery, bot_user: BotUser):
    all_rows = "\n\n".join([str(row) async for row in PhoneBookRow.all()])
    await edit_or_send_message(bot, callback, text=all_rows, kb=keyboards.menu())
    await callback.answer()


@dp.callback_query_handler(Button("find"), state="*")
async def find_(callback: types.CallbackQuery, bot_user: BotUser):
    await edit_or_send_message(bot, callback, text=texts.find(), kb=keyboards.find())
    await callback.answer()


@dp.callback_query_handler(Button("find:", True), state="*")
async def find_(callback: types.CallbackQuery, bot_user: BotUser):
    await edit_or_send_message(bot, callback, text=texts.find(), kb=keyboards.find())
    await callback.answer()


@dp.message_handler(state="*")
async def any_message(message: types.Message, state: FSMContext, bot_user: BotUser):
    await message.delete()


@dp.callback_query_handler(state="*")
async def any_callback(callback: types.CallbackQuery, bot_user: BotUser):
    await callback.answer(texts.maintenance())
