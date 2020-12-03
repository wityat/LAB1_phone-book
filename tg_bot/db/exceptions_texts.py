
def _(s):
    from ..load_all import _
    return _(s)


template = lambda: _("❌ ОШИБКА!\n\n")

punctuation_names = lambda: template() + _("Пунктуационные символы в имени или фамилии!")

numbers_phone = lambda: template() + _("В номере посторонние знаки!")

len_phone = lambda: template() + _("Длина номера не 11 символов!")

no_fn_or_ln = lambda: template() + _("Нет либо имени, либо фамилии, либо вообще ничего нет!")

does_not_exist = lambda: template() + _("Не существует такой записи!")

bad_date = lambda: template() + _("Неправильный формат даты!\nПоддерживаемые форматы: ДД.ММ.ГГГГ или ДД/ММ/ГГГГ")

bad_field_name = lambda: template() + _("Неправильный filed_name, обратитесь к разработчику!")

no_phone = lambda: template() + _("Не указан телефон, укажите, пожалуйста!")
