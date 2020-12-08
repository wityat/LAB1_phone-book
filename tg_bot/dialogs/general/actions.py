from aiogram import types
from aiogram.dispatcher import FSMContext
from tortoise.exceptions import DoesNotExist

from tg_bot.db.exceptions import ValidateError
from tg_bot.db.models import PhoneBookRow
from tg_bot.dialogs.general import texts, keyboards
from tg_bot.load_all import bot
from tg_bot.modules.edit_or_send_message import edit_or_send_message
from tg_bot.modules.filters import Button
from ...db import exceptions_texts
from ...modules.help_functions import *
from ...modules.validation import make_data, validate_names


async def find_with_choice(message: types.Message, state: FSMContext, bd=None):
    data = await get_kwargs_from_state(state)
    try:
        rows = await find_in_db(**make_data(data)) if not bd else await find_in_db_by_birthday(**make_data(data))
    except Exception as e:
        text, kb = str(e), keyboards.back_to_menu()
    else:
        if rows:
            text, kb = await rows_to_str(rows), keyboards.choice_row(rows)
        else:
            text, kb = texts.nothing_find(), keyboards.back_to_menu()
    return text, kb


async def delete(message: types.Message, state: FSMContext, row=None):
    if not row:
        text, kb = await find_with_choice(message, state)
    else:
        await state.update_data(get_kwargs_from_row(row))
        text, kb = texts.sure_delete(), keyboards.choice_yes_no("delete")
    await edit_or_send_message(bot, message, state, text=text, kb=kb)


async def sure_delete(message: types.Message, state: FSMContext):
    data = make_data(await get_kwargs_from_state(state))
    try:
        row = await PhoneBookRow.get_(**data)
    except ValidateError as e:
        text = str(e)
        kb = keyboards.back_to_menu()
    else:
        try:
            await row.delete()
        except ValidateError as e:
            text = str(e)
            kb = keyboards.back_to_menu()
        else:
            text = texts.success_deleted()
            kb = keyboards.back_to_menu()
    await edit_or_send_message(bot, message, state, text=text, kb=kb)


async def find_norm(message: types.Message, state: FSMContext, row=None):
    if not row:
        text, kb = await find_with_choice(message, state)
    else:
        text, kb = await rows_to_str([row]), keyboards.back_to_menu()
    await edit_or_send_message(bot, message, state, text=text, kb=kb)


async def find_birth_day(message: types.Message, state: FSMContext, row=None):
    if not row:
        text, kb = await find_with_choice(message, state, bd=True)
    else:
        text, kb = await rows_to_str([row]), keyboards.back_to_menu()
    await edit_or_send_message(bot, message, state, text=text, kb=kb)


async def add(message: types.Message, state: FSMContext, row=None):
    if not row:
        data = make_data(await get_kwargs_from_state(state))
        print(data, flush=True)
        try:
            await PhoneBookRow.get(**data)
        except DoesNotExist:
            try:
                await PhoneBookRow.create_(**data)
            except ValidateError as e:
                text = str(e)
            else:
                text = texts.success_added()
        else:
            text = texts.already_exist()
        kb = keyboards.back_to_menu()
    else:
        text = await rows_to_str([row])
        kb = keyboards.change_row()
    await edit_or_send_message(bot, message, state, text=text, kb=kb)


async def change(message: types.Message, state: FSMContext, row=None):
    if not row:
        text, kb = await find_with_choice(message, state)
    else:
        await state.update_data(**get_kwargs_from_row(row))
        text, kb = await rows_to_str([row]), keyboards.change_row()
    await edit_or_send_message(bot, message, state, text=text, kb=kb)


async def age(message: types.Message, state: FSMContext, row=None):
    if not row:
        text, kb = await find_with_choice(message, state)
    else:
        if row.birth_day:
            age_ = calculate_age(row.birth_day)
            text, kb = texts.age(age_), keyboards.back_to_menu()
        else:
            raise ValidateError(exceptions_texts.no_bd())
    await edit_or_send_message(bot, message, state, text=text, kb=kb)
