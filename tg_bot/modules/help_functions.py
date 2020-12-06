from datetime import date, datetime
from itertools import islice

from aiogram import types
from aiogram.dispatcher import FSMContext

from tg_bot.db.models import PhoneBookRow
from tg_bot.dialogs.general import actions
from tg_bot.modules.states import GetDataHard
from tg_bot.modules.validation import validate_all, make_str_from_date, make_date_from_str


async def find_in_db_by_birthday(**kwargs):
    d = make_date_from_str(kwargs["birth_day"])
    return await PhoneBookRow.filter(birth_day__day=d.day, birth_day__month=d.month)


async def find_in_db(**kwargs):
    return await PhoneBookRow.filter(**kwargs)


def get_kwargs_from_args(args: list):
    fields = GetDataHard.all_states_names
    # while len(fields) > len(args):
    #     args.append(None)
    return {fields[i].split(":")[-1]: arg for i, arg in enumerate(args)}


def get_kwargs_from_row(row: PhoneBookRow):
    fields = GetDataHard.all_states_names
    return {i.split(":")[-1]: getattr(row, i.split(":")[-1])
            if not isinstance(getattr(row, i.split(":")[-1]), date)
            else make_str_from_date(getattr(row, i.split(":")[-1])) for i in fields}


def get_empty_data():
    fields = GetDataHard.all_states_names
    x = {i.split(":")[-1]: None for i in fields}
    x.update({"action": None})
    return x


async def get_kwargs_from_state(state: FSMContext):
    data = await state.get_data()
    kwargs = {}
    for st in GetDataHard.all_states_names:
        try:
            val = data[st.split(":")[-1]]
        except KeyError:
            continue
        else:
            if val:
                kwargs.update({st.split(":")[-1]: val})
    return kwargs


async def data_to_action(message: types.Message,
                         state: FSMContext = None,
                         args: list = None,
                         row: PhoneBookRow = None,
                         action: str = None):
    async with state.proxy() as st_data:
        action = st_data["action"] if not action else action
        if args or state and not row:
            data = get_kwargs_from_args(args) if args else await get_kwargs_from_state(state)
            data = validate_all(**data, action=action)
            st_data.update(data)
    await (getattr(actions, action))(message, state, row)
    await state.reset_state(with_data=False)


async def rows_to_str(rows):
    return "Записи:\n\n" + "\n\n".join([f"{i + 1}. " + str(row) for i, row in enumerate(rows)])


def state_to_readable_word(st: str, add_info=False):
    if "first_name" in st:
        return "имя"
    elif "last_name" in st:
        return "фамилия"
    elif "phone" in st:
        return "номер телефона"
    elif "birth_day" in st:
        return "день рождения" + (" (в формате ДД.ММ.ГГГГ) " if add_info else "")


def calculate_age(born):
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


async def get_birth_day_soon():
    now = datetime.now()
    next_m = datetime(now.year, now.month+1 if now.month != 12 else 1, now.day)
    return await PhoneBookRow.filter(birth_day__range=(now.date(), next_m.date()))


def chunks(data, size=10000):
    it = iter(data)
    for i in range(0, len(data), size):
        yield {k: data[k] for k in islice(it, size)}
