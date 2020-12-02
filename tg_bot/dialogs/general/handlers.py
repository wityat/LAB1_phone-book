from aiogram.dispatcher.filters import CommandStart
from .actions import sure_delete
from ...db.exceptions import ValidateError
from ...db.models import BotUser, PhoneBookRow
from ...load_all import dp, bot
from . import texts, keyboards, actions

from ...modules.filters import Button
from ...modules.edit_or_send_message import edit_or_send_message
from ...modules.help_functions import *
from ...modules.states import *
from ...modules.validation import validate, make_data


async def menu(message: types.Message, state: FSMContext):
    await edit_or_send_message(bot, message, state, text=texts.menu(), kb=keyboards.menu())


@dp.message_handler(CommandStart(), state="*")
async def start(message: types.Message, state: FSMContext, bot_user: BotUser):
    await menu(message, state)


@dp.callback_query_handler(Button("menu"), state="*")
async def menu_(callback: types.CallbackQuery, state: FSMContext, bot_user: BotUser):
    await menu(callback.message, state)
    await state.update_data(get_empty_data())
    await callback.answer()


@dp.callback_query_handler(Button("all"), state="*")
async def all_(callback: types.CallbackQuery, state: FSMContext, bot_user: BotUser):
    all_rows = await rows_to_str(await PhoneBookRow.all())
    await edit_or_send_message(bot, callback, state, text=all_rows, kb=keyboards.back_to_menu())
    await callback.answer()


@dp.callback_query_handler(Button("find"), state="*")
async def find_(callback: types.CallbackQuery, state: FSMContext, bot_user: BotUser):
    await edit_or_send_message(bot, callback, state, text=texts.how_find(), kb=keyboards.how_find())
    await callback.answer()


@dp.callback_query_handler(Button("find_birth_day"), state="*")
async def find_birth_day_(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data({"action": callback.data})
    await edit_or_send_message(bot, callback, state, text=texts.get_data_birth_day(), kb=keyboards.back_to_menu())
    await GetDataBirthDay.me.set()
    await callback.answer()


@dp.message_handler(state=GetDataBirthDay.me)
async def get_data_birth_day(message: types.Message, state: FSMContext, bot_user: BotUser):
    try:
        d = validate("birth_day", message.text+".2020")
    except ValidateError as e:
        text = str(e)
    else:
        args = ["", "", "", d]
        try:
            await data_to_action(message, state=state, args=args)
            return
        except ValidateError as e:
            text = str(e)
    await edit_or_send_message(bot, message, state, text=text, kb=keyboards.back_to_menu())


@dp.callback_query_handler(Button("find_norm") | Button("add") | Button("delete") | Button("change") | Button("age"),
                           state="*")
async def set_action(callback: types.CallbackQuery, state: FSMContext, bot_user: BotUser):
    await state.update_data({"action": callback.data})
    await edit_or_send_message(bot, callback, state, text=texts.get_data(), kb=keyboards.get_data())
    await callback.answer()


@dp.callback_query_handler(Button("get_data:", True), state="*")
async def get_data(callback: types.CallbackQuery, state: FSMContext, bot_user: BotUser):
    get_data_way = callback.data.split(":")[-1]
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
        try:
            await data_to_action(callback.message, state=state, action="find_norm")
        except ValidateError as e:
            await edit_or_send_message(bot, callback, state, text=str(e), kb=keyboards.back_to_menu())
    await callback.answer()


@dp.callback_query_handler(Button("choice_row", True), state="*")
async def choice_row(callback: types.CallbackQuery, state: FSMContext):
    choice_hash = callback.data.split(":")[-1]
    row = await PhoneBookRow.get(hash_name__startswith=choice_hash)
    try:
        await data_to_action(callback.message, state=state, row=row)
    except ValidateError as e:
        await edit_or_send_message(bot, callback, state, text=str(e), kb=keyboards.back_to_menu())


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
            val = validate(what, message.text, return_date=True)
            print(val, flush=True)
        except ValidateError as e:
            text = str(e)
        else:
            if "name" in what:
                row_ = row
                await row.delete()
                setattr(row_, what, val)
                row_._custom_generated_pk = True
                await row_.save(force_create=True)
                row = row_
            else:
                setattr(row, what, val)
                await row.save(force_update=True)
            # text = texts.success_changed()
            await state.update_data({what: val})
            await actions.change(message, state, row=row)
    if text:
        await edit_or_send_message(bot, message, text=text, kb=keyboards.back_to_menu())


@dp.callback_query_handler(Button("birth_day_soon"), state="*")
async def birth_day_soon(callback: types.CallbackQuery, state: FSMContext):
    text, kb = await rows_to_str(await get_birth_day_soon()), keyboards.back_to_menu()
    await edit_or_send_message(bot, callback, state, text=text, kb=kb)
    await callback.answer()


@dp.message_handler(state="*")
async def any_message(message: types.Message, state: FSMContext, bot_user: BotUser):
    await message.delete()


@dp.callback_query_handler(state="*")
async def any_callback(callback: types.CallbackQuery, bot_user: BotUser):
    await callback.answer(texts.maintenance())
