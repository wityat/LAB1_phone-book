from ...load_all import _
from ...modules.help_functions import chunks
from ...modules.keyboard import KeyboardInline, KeyboardReply

menu = lambda: KeyboardInline([{_("Все"): "all"},
                               {_("Поиск"): "find", _("Добавить"): "add"},
                               {_("Изменить"): "change", _("Удалить"): "delete"},
                               {_("Возраст"): "age"},
                               {_("У кого скоро др?"): "birth_day_soon"},
                               {_("Как пользоваться?"): "how_use"}
                               ]).get()

back_to_menu = lambda: KeyboardInline([{_("Меню"): "menu"}]).get()

get_data = lambda: KeyboardInline([{"1": "get_data:easy", "2": "get_data:hard"}]).get()

get_data_hard = lambda: KeyboardInline([{_("Показать уже найденные"): "get_data_hard:show_find"},
                                        {_("Пропустить"): "get_data_hard:skip"}]).get()

choice_row = lambda rows: KeyboardInline(
    [i for i in chunks({f"{j+1}": f"choice_row:{row.hash_name[:20]}" for j, row in enumerate(rows)}, 3)] +
    [{_("Меню"): "menu"}]).get()


choice_yes_no = lambda call: KeyboardInline([{_("Да"): f"{call}:1", _("Нет"): f"{call}:0"}]).get()

change_row = lambda: KeyboardInline([{_("Изменить имя"): "change:first_name", _("Изменить фамилию"): "change:last_name"},
                                     {_("Изменить номер телефона"): "change:phone", _("Изменить дату рождения"): "change:birth_day"},
                                     {_("Меню"): "menu"}]).get()

how_find = lambda: KeyboardInline([{_("Обычный"): "find_norm", _("По дате рождения"): "find_birth_day"},
                                   {_("Назад"): "menu"}]).get()
