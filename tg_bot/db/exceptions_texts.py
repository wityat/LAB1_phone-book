from ..load_all import _

template = lambda: _("❌ ОШИБКА!\n\n")

punctuation_names = lambda: template() + _("Пунктуационные символы в имени или фамилии!")

numbers_phone = lambda: template() + _("В номере посторонние знаки!")

len_phone = lambda: template() + _("Длина номера не 11 символов!")
