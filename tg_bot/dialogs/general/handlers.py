from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from aiogram.dispatcher.filters import CommandStart
from aiogram.utils.deep_linking import get_start_link
from tortoise.exceptions import DoesNotExist

from ...db.exceptions import ValidateError
from ...db.models import BotUser, PhoneBookRow
from ...load_all import dp, bot
from . import texts, keyboards, actions

from ...modules.filters import Button
from ...modules.edit_or_send_message import edit_or_send_message

from enum import Enum


class Find(Enum):
    easy = 1
    hard = 2


class GetDataEasy(StatesGroup):
    me = State()


class GetDataHard(StatesGroup):
    first_name = State()
    last_name = State()
    phone = State()
    birth_date = State()


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
    all_rows = rows_to_str(await PhoneBookRow.all())
    await edit_or_send_message(bot, callback, text=all_rows, kb=keyboards.menu())
    await callback.answer()


@dp.callback_query_handler(Button("find") | Button("add") | Button("del") | Button("change"), state="*")
async def set_action(callback: types.CallbackQuery, state: FSMContext, bot_user: BotUser):
    await state.update_data({"action": callback.data})
    await edit_or_send_message(bot, callback, text=texts.get_data(), kb=keyboards.get_data())
    await callback.answer()


@dp.callback_query_handler(Button("get_data:", True), state="*")
async def get_data(callback: types.CallbackQuery, state: FSMContext, bot_user: BotUser):
    get_data_way = callback.data.slpit(":")[-1]
    if get_data_way == "easy":
        await edit_or_send_message(bot, callback, text=texts.get_data_easy())
        await GetDataEasy.me.set()
    elif get_data_way == "hard":
        await GetDataHard.first_name.set()
        await edit_or_send_message(bot, callback, text=texts.get_data_hard(), kb=keyboards.get_data_hard())
    await callback.answer()


async def find_in_db(**kwargs):
    return await PhoneBookRow.filter(**kwargs)


def get_kwargs_from_args(args: list):
    fields = GetDataHard.all_states_names
    return {fields[i]: arg for i, arg in enumerate(args)}


def get_kwargs_from_state(state: FSMContext):
    data = await state.get_data()
    kwargs = {}
    for st in GetDataHard.all_states_names:
        try:
            val = data[st]
        except KeyError:
            continue
        else:
            kwargs.update({st: val})
    return kwargs


def rows_to_str(rows):
    return "\n\n".join([str(row) async for row in rows])


@dp.message_handler(state=GetDataEasy.me)
async def get_data_easy(message: types.Message, state: FSMContext, bot_user: BotUser):
    args = message.text.replace("  ", " % ").split()
    args = [arg.replace("%", "") for arg in args]
    data = get_kwargs_from_args(args)
    async with state.proxy() as st_data:
        result = await (getattr(actions, st_data["action"]))()
        st_data["action"] = None
    # await edit_or_send_message(bot, message, text=rows, kb=keyboards.back_to_menu())


###################FIND##########################


@dp.callback_query_handler(Button("find"), state="*")
async def find_(callback: types.CallbackQuery, bot_user: BotUser):
    await edit_or_send_message(bot, callback, text=texts.find(), kb=keyboards.find())
    await callback.answer()


@dp.callback_query_handler(Button("find:", True), state="*")
async def find_(callback: types.CallbackQuery, state: FSMContext, bot_user: BotUser):
    find_num = int(callback.data.slpit(":")[-1])
    if find_num == Find.easy:
        await edit_or_send_message(bot, callback, text=texts.easy_find())
        await States.easy_find.set()
    elif find_num == Find.hard:
        await States.hard_find_fn.set()
        await edit_or_send_message(bot, callback, text=texts.hard_find_(await state.get_state()), kb=keyboards.hard_find())
    await edit_or_send_message(bot, callback, text=texts.find(), kb=keyboards.find())
    await callback.answer()




async def hard_find(what: str, msg_or_call: [types.Message, types.CallbackQuery], state: FSMContext):
    st_str = await state.get_state()
    await state.update_data({st_str: what})
    if st_str == States.hard_find_bd.state:
        rows = await find_in_db(**get_kwargs_from_state(state))
        text = rows_to_str(rows)
        kb = keyboards.back_to_menu()
    else:
        await States.next()
        text = texts.hard_find_(await state.get_state())
        kb = keyboards.hard_find()
    await edit_or_send_message(bot, msg_or_call, text=text, kb=kb)


@dp.callback_query_handler(Button("hard_find:dont_know", True), state="*")
async def hard_find__dont_know(callback: types.CallbackQuery, state: FSMContext, bot_user: BotUser):
    await hard_find("", callback, state)
    await callback.answer()


@dp.message_handler(custom_state=[States.hard_find_bd, States.hard_find_fn, States.hard_find_ln, States.hard_find_phn], state="*")
async def hard_find__any_step(message: types.Message, state: FSMContext, bot_user: BotUser):
    await hard_find(message.text, message, state)


###################FIND##########################


###################ADD###########################


@dp.message_handler(state="*")
async def any_message(message: types.Message, state: FSMContext, bot_user: BotUser):
    await message.delete()


@dp.callback_query_handler(state="*")
async def any_callback(callback: types.CallbackQuery, bot_user: BotUser):
    await callback.answer(texts.maintenance())
