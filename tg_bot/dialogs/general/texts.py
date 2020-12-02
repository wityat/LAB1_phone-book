from ...load_all import _

menu = lambda: _("Меню:")

get_data = lambda: _("1 - Простой поиск (вводите через пробел поля, которые считаете нужными)\n") + \
                   _("2 - Поиск каждое поле новое сообщение\n")

maintenance = lambda: _("В разработке!")

get_data_easy = lambda: _("Отправьте через пробел поля, по которым хотите произвести поиск, например:\nВиктор Шатилов 79300085393 13.07.2001\n\nЧтобы пропустить какое-то поле, введите пробел два раза, пример:\nШатилов  79300085393")


def state_to_readable_word(st: str):
    if "first_name" == st:
        return "имя"
    elif "last_name" == st:
        return "фамилия"
    elif "phone" == st:
        return "номер телефона"
    elif "birth_day" == st:
        return "день рождения"


get_data_hard = lambda st: _("Отправьте мне <b>") + f"{state_to_readable_word(st)}" + _("</b> или нажмите кнопку <i>Пропустить</i>")

success_deleted = lambda: _("Успешно удалено!")

sure_delete = lambda: _("Действительно хочешь удалить?")
