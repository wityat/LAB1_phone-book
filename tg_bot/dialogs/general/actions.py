from aiogram import types
from aiogram.dispatcher import FSMContext
from tortoise.exceptions import DoesNotExist

from tg_bot.db.exceptions import ValidateError
from tg_bot.db.models import PhoneBookRow
from tg_bot.dialogs.general import texts, keyboards
from tg_bot.load_all import bot
from tg_bot.modules.edit_or_send_message import edit_or_send_message
from tg_bot.modules.filters import Button
from ...modules.help_functions import *
from ...modules.validation import make_data, validate_names


async def delete(message: types.Message, state: FSMContext, row=None):
    if row:
        await state.update_data(get_kwargs_from_args([row.first_name, row.last_name,
                                                      row.phone, row.birth_day]))
    await edit_or_send_message(bot, message, state, text=texts.sure_delete(), kb=keyboards.choice_yes_no("delete"))


async def sure_delete(message: types.Message, state: FSMContext):
    data = make_data(await get_kwargs_from_state(state))
    print(data, flush=True)
    try:
        row = await PhoneBookRow.get(**data)
    except ValidateError as e:
        text = str(e)
        kb = keyboards.back_to_menu()
    else:
        try:
            await row.delete(**data)
        except ValidateError as e:
            text = str(e)
            kb = keyboards.back_to_menu()
        else:
            text = texts.success_deleted()
            kb = keyboards.back_to_menu()
    await edit_or_send_message(bot, message, state, text=text, kb=kb)


async def find(message: types.Message, state: FSMContext, row=None):
    if not row:
        data = await get_kwargs_from_state(state)
        try:
            rows = await find_in_db(**make_data(data))
        except Exception as e:
            text = str(e)
        else:
            text = await rows_to_str(rows)
    else:
        text = await rows_to_str([row])
    await edit_or_send_message(bot, message, state, text=text, kb=keyboards.back_to_menu())


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
    data = await get_kwargs_from_state(state)
    if not row:
        try:
            row = await PhoneBookRow.get_(**make_data(data))
        except Exception as e:
            text = str(e)
            kb = keyboards.back_to_menu()
        else:
            text = await rows_to_str([row])
            kb = keyboards.change_row()
    else:
        text = await rows_to_str([row])
        kb = keyboards.change_row()
    await edit_or_send_message(bot, message, state, text=text, kb=kb)


async def age(message: types.Message, state: FSMContext, row=None):
    data = await get_kwargs_from_state(state)
    if not row:
        try:
            row = await PhoneBookRow.get_(**make_data(data))
        except Exception as e:
            text = str(e)
        else:
            age_ = calculate_age(row.birth_day)
            text = texts.age(age_)
    else:
        age_ = calculate_age(row.birth_day)
        text = texts.age(age_)
    await edit_or_send_message(bot, message, state, text=text, kb=keyboards.back_to_menu())
