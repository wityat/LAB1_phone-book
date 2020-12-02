from ...load_all import _
from ...modules.keyboard import KeyboardInline, KeyboardReply

menu = lambda: KeyboardInline([{_("Все"): "all"},
                               {_("Поиск"): "find"},
                               {_("Добавить"): "add"},
                               {_("Удалить"): "delete"},
                               {_("Изменить"): "change"},
                               {_("Возраст"): "age"},
                               ]).get()

back_to_menu = lambda: KeyboardInline([{_("Меню"): "menu"}]).get()

get_data = lambda: KeyboardInline([{"1": "get_data:easy", "2": "get_data:hard"}]).get()

get_data_hard = lambda: KeyboardInline([{_("Показать уже найденные"): "get_data:show_find"},
                                        {_("Пропустить"): "get_data:skip"}]).get()

get_data_hard__nothing = lambda: KeyboardInline([{_("Ничего не найдено"): "get_data:nothing"},
                                                 {_("Пропустить"): "get_data:skip"}]).get()

choice_yes_no = lambda call: KeyboardInline([{_("Да"): f"{call}:1", _("Нет"): f"{call}:0"}]).get()

change_row = lambda: KeyboardInline([{"Изменить имя": "change:first_name", "Изменить фамилию": "change:last_name"},
                                     {"Изменить номер телефона": "change:phone", "Изменить дату рождения": "change:birth_day"}]).get()
