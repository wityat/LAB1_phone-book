from datetime import date

from aiogram.dispatcher import FSMContext

from tg_bot.db.models import PhoneBookRow
from tg_bot.modules.states import GetDataHard


async def find_in_db(**kwargs):
    return await PhoneBookRow.filter(**kwargs)


def get_kwargs_from_args(args: list):
    fields = GetDataHard.all_states_names
    return {fields[i].split(":")[-1]: arg for i, arg in enumerate(args)}


async def get_kwargs_from_state(state: FSMContext):
    data = await state.get_data()
    kwargs = {}
    for st in GetDataHard.all_states_names:
        try:
            val = data[st]
        except KeyError:
            continue
        else:
            kwargs.update({st.split(":")[-1]: val})
    return kwargs


async def rows_to_str(rows):
    return "Записи:\n\n" + "\n\n".join([str(row) for row in rows])


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


