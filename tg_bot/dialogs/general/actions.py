from aiogram import types
from aiogram.dispatcher import FSMContext

from tg_bot.db.exceptions import ValidateError
from tg_bot.db.models import PhoneBookRow
from tg_bot.dialogs.general import texts, keyboards
from tg_bot.load_all import bot
from tg_bot.modules.edit_or_send_message import edit_or_send_message
from tg_bot.modules.filters import Button
from ...modules.help_functions import *


async def delete(message: types.Message, state: FSMContext):
    await edit_or_send_message(bot, message, text=texts.sure_delete(), kb=keyboards.choice_yes_no("delete"))


async def sure_delete(message: types.Message, state: FSMContext):
    data = await get_kwargs_from_state(state)
    row = await PhoneBookRow(**data)
    try:
        row.validate_names()
    except ValidateError as e:
        text = str(e)
        kb = keyboards.back_to_menu()
    else:
        try:
            await row.get_()
        except ValidateError as e:
            text = str(e)
            kb = keyboards.back_to_menu()
        else:
            text = texts.success_deleted()
            kb = keyboards.back_to_menu()
    await edit_or_send_message(bot, message, text=text, kb=kb)


async def find(message: types.Message, state: FSMContext):
    data = await get_kwargs_from_state(state)
    try:
        rows = await find_in_db(**data)
    except Exception as e:
        text = str(e)
    else:
        text = await rows_to_str(rows)
    await edit_or_send_message(bot, message, text=text, kb=keyboards.back_to_menu())


async def add(message: types.Message, state: FSMContext):
    data = await get_kwargs_from_state(state)
    row = await PhoneBookRow(**data)
    try:
        row, is_created = await row.get_or_create()
    except Exception as e:
        text = str(e)
    else:
        if is_created:
            text = texts.success_added()
        else:
            text = texts.already_exist()
    await edit_or_send_message(bot, message, text=text, kb=keyboards.back_to_menu())


async def change(message: types.Message, state: FSMContext):
    data = await get_kwargs_from_state(state)
    row = await PhoneBookRow(**data)
    try:
        row = await row.get_()
    except Exception as e:
        text = str(e)
        kb = keyboards.back_to_menu()
    else:
        text = await rows_to_str(row)
        kb = keyboards.change_row()
    await edit_or_send_message(bot, message, text=text, kb=kb)


async def age(message: types.Message, state: FSMContext):
    data = await get_kwargs_from_state(state)
    row = await PhoneBookRow(**data)

    try:
        row = await row.get_()
    except Exception as e:
        text = str(e)
    else:
        age_ = calculate_age(row.birth_day)
        text = texts.age(age_)
    await edit_or_send_message(bot, message, text=text, kb=keyboards.back_to_menu())
