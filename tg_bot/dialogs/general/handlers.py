from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from aiogram.dispatcher.filters import CommandStart
from aiogram.utils.deep_linking import get_start_link
from tortoise.exceptions import DoesNotExist

from .actions import sure_delete
from ...db.exceptions import ValidateError
from ...db.models import BotUser, PhoneBookRow
from ...load_all import dp, bot
from . import texts, keyboards, actions

from ...modules.filters import Button
from ...modules.edit_or_send_message import edit_or_send_message
from ...modules.help_functions import *
from ...modules.states import *
from ...modules.validation import validate


async def menu(message: types.Message, state: FSMContext):
    await edit_or_send_message(bot, message, state, text=texts.menu(), kb=keyboards.menu())


@dp.message_handler(CommandStart(), state="*")
async def start(message: types.Message, state: FSMContext, bot_user: BotUser):
    await menu(message, state)


@dp.callback_query_handler(Button("menu"), state="*")
async def menu_(callback: types.CallbackQuery, state: FSMContext, bot_user: BotUser):
    await menu(callback.message, state)
    await callback.answer()


@dp.callback_query_handler(Button("all"), state="*")
async def all_(callback: types.CallbackQuery, state: FSMContext, bot_user: BotUser):
    all_rows = await rows_to_str(await PhoneBookRow.all())
    await edit_or_send_message(bot, callback, state, text=all_rows, kb=keyboards.back_to_menu())
    await callback.answer()


@dp.callback_query_handler(Button("find") | Button("add") | Button("delete") | Button("change") | Button("age"),
                           state="*")
async def set_action(callback: types.CallbackQuery, state: FSMContext, bot_user: BotUser):
    await state.update_data({"action": callback.data})
    await edit_or_send_message(bot, callback, state, text=texts.get_data(), kb=keyboards.get_data())
    await callback.answer()


@dp.callback_query_handler(Button("get_data:", True), state="*")
async def get_data(callback: types.CallbackQuery, state: FSMContext, bot_user: BotUser):
    get_data_way = callback.data.split(":")[-1]
    print(get_empty_data(), flush=True)
    await state.update_data(get_empty_data())
    if get_data_way == "easy":
        await edit_or_send_message(bot, callback, state, text=texts.get_data_easy())
        await GetDataEasy.me.set()
    elif get_data_way == "hard":
        await GetDataHard.first_name.set()
        await edit_or_send_message(bot, callback, state, text=texts.get_data_hard(await state.get_state()), kb=keyboards.get_data_hard())
    await callback.answer()


@dp.callback_query_handler(Button("get_data_hard", True),
                           custom_state=[GetDataHard.first_name, GetDataHard.last_name,
                                         GetDataHard.birth_day, GetDataHard.phone],
                           state="*")
async def get_data_hard(callback: types.CallbackQuery, state: FSMContext, bot_user: BotUser):
    get_data_hard_way = callback.data.split(":")[-1]
    if get_data_hard_way == "skip":
        await get_data_hard_msg(callback.message, state, skip=True)
    elif get_data_hard_way == "show_find":
        rows = await find_in_db(**await get_kwargs_from_state(state))
        text = await rows_to_str(rows)
        await edit_or_send_message(bot, callback, state, text=text, kb=keyboards.get_data_hard__choice(rows))
    elif get_data_hard_way == "nothing":
        await callback.answer(texts.nothing_find())
    elif get_data_hard_way:
        row = await PhoneBookRow.get(hash_name__startswith=get_data_hard_way)
        try:
            await data_to_action(callback.message, state=state, row=row)
        except ValidateError as e:
            await edit_or_send_message(bot, callback, state, text=str(e), kb=keyboards.back_to_menu())
    await callback.answer()


@dp.message_handler(custom_state=[GetDataHard.first_name, GetDataHard.last_name,
                                  GetDataHard.birth_day, GetDataHard.phone],
                    state="*")
async def get_data_hard_msg(message: types.Message, state: FSMContext, skip=None):
    async with state.proxy() as st_data:
        what = (await state.get_state()).split(":")[-1]
        try:
            field_val = validate(what, message.text)
        except ValidateError as e:
            await edit_or_send_message(bot, message, state, text=str(e) + "\n" + texts.try_input_again(),
                                       kb=keyboards.get_data_hard())
        else:
            st_data[what] = field_val
        st_data[what] = message.text if not skip else None

    if what not in GetDataHard.birth_day.state:
        what = await GetDataHard.next()
        await edit_or_send_message(bot, message, state, text=texts.get_data_hard(what), kb=keyboards.get_data_hard())
    else:
        try:
            await data_to_action(message, state=state)
        except ValidateError as e:
            await edit_or_send_message(bot, message, state, text=str(e), kb=keyboards.back_to_menu())


@dp.message_handler(state=GetDataEasy.me)
async def get_data_easy(message: types.Message, state: FSMContext, bot_user: BotUser):
    args = message.text.replace("  ", " % ").split()
    args = [arg.replace("%", "") for arg in args]
    print("ARGS: ", args, flush=True)
    try:
        await data_to_action(message, state=state, args=args)
    except ValidateError as e:
        await edit_or_send_message(bot, message, state, text=str(e), kb=keyboards.back_to_menu())


@dp.callback_query_handler(Button("delete:", True), state="*")
async def delete_(callback: types.CallbackQuery, state: FSMContext):
    sure_del = bool(int(callback.data.split(":")[-1]))
    if sure_del:
        await sure_delete(callback.message, state)
    else:
        await menu(callback.message, state)
    await callback.answer()


@dp.callback_query_handler(Button("change:", True), state="*")
async def change_(callback: types.CallbackQuery, state: FSMContext):
    what = callback.data.split(":")[-1]
    await (getattr(Change, what)).set()
    await edit_or_send_message(bot, callback, state, text=texts.change(what))
    await callback.answer()


@dp.message_handler(custom_state=[Change.first_name, Change.last_name, Change.birth_day, Change.phone], state="*")
async def change__(message: types.Message, state: FSMContext):
    what = (await state.get_state()).split(":")[-1]
    text = ""
    try:
        row = await PhoneBookRow.get_(**await get_kwargs_from_state(state))
    except Exception as e:
        text = str(e)
    else:
        try:
            if "name" in what:
                row_ = row
                await row.delete()
                setattr(row_, what, message.text)
                row_._custom_generated_pk = True
                await row_.save(force_create=True)
            else:
                setattr(row, what, message.text)
                await row.save(force_update=True)
        except ValidateError as e:
            text = str(e)
        else:
            # text = texts.success_changed()
            await actions.change(message, state, row=row)
    if text:
        await edit_or_send_message(bot, message, text=text, kb=keyboards.back_to_menu())



# ###################FIND##########################
#
#
# @dp.callback_query_handler(Button("find"), state="*")
# async def find_(callback: types.CallbackQuery, bot_user: BotUser):
#     await edit_or_send_message(bot, callback, state, text=texts.find(), kb=keyboards.find())
#     await callback.answer()
#
#
# @dp.callback_query_handler(Button("find:", True), state="*")
# async def find_(callback: types.CallbackQuery, state: FSMContext, bot_user: BotUser):
#     find_num = int(callback.data.slpit(":")[-1])
#     if find_num == Find.easy:
#         await edit_or_send_message(bot, callback, state, text=texts.easy_find())
#         await States.easy_find.set()
#     elif find_num == Find.hard:
#         await States.hard_find_fn.set()
#         await edit_or_send_message(bot, callback, state, text=texts.hard_find_(await state.get_state()), kb=keyboards.hard_find())
#     await edit_or_send_message(bot, callback, state, text=texts.find(), kb=keyboards.find())
#     await callback.answer()
#
#
#
#
# async def hard_find(what: str, msg_or_call: [types.Message, types.CallbackQuery], state: FSMContext):
#     st_str = await state.get_state()
#     await state.update_data({st_str: what})
#     if st_str == States.hard_find_bd.state:
#         rows = await find_in_db(**await get_kwargs_from_state(state))
#         text = await rows_to_str(rows)
#         kb = keyboards.back_to_menu()
#     else:
#         await States.next()
#         text = texts.hard_find_(await state.get_state())
#         kb = keyboards.hard_find()
#     await edit_or_send_message(bot, msg_or_call, state, text=text, kb=kb)
#
#
# @dp.callback_query_handler(Button("hard_find:dont_know", True), state="*")
# async def hard_find__dont_know(callback: types.CallbackQuery, state: FSMContext, bot_user: BotUser):
#     await hard_find("", callback, state)
#     await callback.answer()
#
#
# @dp.message_handler(custom_state=[States.hard_find_bd, States.hard_find_fn, States.hard_find_ln, States.hard_find_phn], state="*")
# async def hard_find__any_step(message: types.Message, state: FSMContext, bot_user: BotUser):
#     await hard_find(message.text, message, state)
#
#
# ###################FIND##########################
#
#
# ###################ADD###########################


@dp.message_handler(state="*")
async def any_message(message: types.Message, state: FSMContext, bot_user: BotUser):
    await message.delete()


@dp.callback_query_handler(state="*")
async def any_callback(callback: types.CallbackQuery, bot_user: BotUser):
    await callback.answer(texts.maintenance())
