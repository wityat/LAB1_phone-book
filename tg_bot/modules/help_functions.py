import re
from datetime import date
from itertools import islice

from aiogram import types
from aiogram.dispatcher import FSMContext

from tg_bot.db.models import PhoneBookRow
from tg_bot.dialogs.general import actions
from tg_bot.modules.states import GetDataHard


async def find_in_db(**kwargs):
    return await PhoneBookRow.filter(**kwargs)


def get_kwargs_from_args(args: list):
    fields = GetDataHard.all_states_names
    while len(fields) > len(args):
        args.append(None)
    return {fields[i].split(":")[-1]: arg for i, arg in enumerate(args)}


def get_empty_data():
    fields = GetDataHard.all_states_names
    return {i.split(":")[-1]: None for i in fields}


async def get_kwargs_from_state(state: FSMContext):
    data = await state.get_data()
    kwargs = {}
    for st in GetDataHard.all_states_names:
        try:
            val = data[st.split(":")[-1]]
        except KeyError:
            continue
        else:
            kwargs.update({st.split(":")[-1]: val})
    return kwargs


async def data_to_action(message: types.Message, state: FSMContext = None, args: list = None, row: PhoneBookRow = None):
    if args or state:
        data = get_kwargs_from_args(args) if args else await get_kwargs_from_state(state)
        print(data, flush=True)
        await state.update_data(data)
        await state.reset_state(with_data=False)
    async with state.proxy() as st_data:
        await (getattr(actions, st_data["action"]))(message, state, row)
        st_data["action"] = None


async def rows_to_str(rows):
    return "Записи:\n\n" + "\n\n".join([f"{i+1}. "+str(row) for i, row in enumerate(rows)])


def state_to_readable_word(st: str, add_info=False):
    if "first_name" in st:
        return "имя"
    elif "last_name" in st:
        return "фамилия"
    elif "phone" in st:
        return "номер телефона"
    elif "birth_day" in st:
        return "день рождения" + (" (в формате ГГГГ-ММ-ДД) " if add_info else "")


def calculate_age(born):
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


def chunks(data, size=10000):
    it = iter(data)
    for i in range(0, len(data), size):
        yield {k: data[k] for k in islice(it, size)}
