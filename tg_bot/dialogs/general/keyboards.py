from ...load_all import _
from ...modules.keyboard import KeyboardInline, KeyboardReply

menu = lambda: KeyboardInline([{_("Все"): "all"},
                               {_("Поиск"): "find"},
                               {_("Добавить"): "add"},
                               {_("Удалить"): "del"},
                               {_("Изменить "): "change"},
                               {_("Возраст"): "age"},
                               ]).get()

back_to_menu = lambda: KeyboardInline([{_("Меню"): "menu"}]).get()

find = lambda: KeyboardInline([{"1": "find:1", "2": "find:2"},
                               {"3": "find:3", "4": "find:4"}]).get()


