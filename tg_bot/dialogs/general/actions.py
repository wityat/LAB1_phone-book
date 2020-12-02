from aiogram import types
from aiogram.dispatcher import FSMContext

from tg_bot.db.exceptions import ValidateError
from tg_bot.db.models import PhoneBookRow
from tg_bot.dialogs.general import texts


async def


async def delete(callback: types.CallbackQuery, state: FSMContext, data: dict):
    row = await PhoneBookRow(**data)
    try:
        row.validate_names()
    except ValidateError as e:
        text = str(e)
    else:
        try:
            await row.get_()
        except ValidateError as e:
            text = str(e)
        else:
            text = texts.sure_delete()
    await callback.answer(text)

