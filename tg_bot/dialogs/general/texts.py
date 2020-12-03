from ...load_all import _
from ...modules.help_functions import state_to_readable_word

menu = lambda: _("Меню:")

get_data = lambda: _("1 - Простой ввод (вводите через пробел имя фимилию телефон дата_рождения)\n") + \
                   _("2 - Сложный ввод (каждое поле новое сообщение)\n")

maintenance = lambda: _("В разработке!")

get_data_easy = lambda: _("Отправьте через пробел поля, например:\nВиктор Шатилов 79300085393 13.07.2001\n\nЧтобы пропустить какое-то поле, введите пробел два раза, пример:\nВиктор  79300085393")

get_data_hard = lambda st: _("Отправьте мне <b>") + f"{state_to_readable_word(st)}" + _("</b> или нажмите кнопку <i>Пропустить</i>")

success_deleted = lambda: _("Успешно удалено!")

sure_delete = lambda: _("Действительно хочешь удалить?")

success_added = lambda:  _("Успешно добавлено!")

already_exist = lambda:  _("Такая запись уже существует!")

change = lambda st: _("Отправьте мне новое <b>") + f"{state_to_readable_word(st, True)}" + _("</b>")

success_changed = lambda:  _("Успешно изменено!")

age = lambda age: _("Возраст человека из этой записи - ") + f"{age}"

nothing_find = lambda: _("Ничего не найдено!")

try_input_again = lambda: _("Попробуйте ввести снова!")
