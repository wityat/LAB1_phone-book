import re
import string
from datetime import date

from tg_bot.db import exceptions_texts
from tg_bot.db.exceptions import ValidateError


def validate_birth_day(bd: str) -> [str, None]:
    if not isinstance(bd, str):
        return None
    result = re.findall(r"^[\s]*(\d\d[/.]\d\d[/.]\d\d\d\d)[\s]*$", bd)
    if result:
        day, month, year = map(int, result[0].split("/" if "/" in result[0] else "."))
        try:
            d = date(day=day, month=month, year=year)
        except Exception as e:
            raise ValidateError(exceptions_texts.bad_date())
        else:
            return d.strftime("%Y-%m-%d")
    else:
        raise ValidateError(exceptions_texts.bad_date())


def validate_phone(phone: str):
    if not phone:
        raise ValidateError(exceptions_texts.no_phone())
    if phone.startswith("+7") or phone.startswith("7"):
        phone.replace("+7", "8")
    try:
        phone = re.match(r"[\d]+", phone).group()
    except AttributeError:
        raise ValidateError(exceptions_texts.numbers_phone())
    if not len(phone) == 11:
        raise ValidateError(exceptions_texts.len_phone())
    return phone


def validate_name(name: str):
    n = any(x for x in string.punctuation if x in name)
    if n:
        raise ValidateError(exceptions_texts.punctuation_names())
    return name.title()


def validate_names(first_name: str, last_name: str):
    if not first_name or not last_name:
        raise ValidateError(exceptions_texts.no_fn_or_ln())
    return validate_name(first_name), validate_name(last_name)


def validate(field_name: str, value: str):
    if not isinstance(value, str):
        value = ""
    if "phone" in field_name:
        return validate_phone(value)
    elif "name" in field_name:
        return validate_name(value)
    elif "birth" in field_name:
        return validate_birth_day(value)
    else:
        raise ValidateError(exceptions_texts.bad_field_name())


def validate_all(first_name="", last_name="", phone="", birth_day=""):
    first_name, last_name = validate_names(first_name, last_name)
    phone = validate_phone(phone)
    birth_day = validate_birth_day(birth_day)
    return {"first_name": first_name, "last_name": last_name,
            "phone": phone, "birth_day": birth_day}
