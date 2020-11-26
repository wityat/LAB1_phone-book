from aiogram.contrib.middlewares.i18n import I18nMiddleware
from aiogram import types
from ..config import I18N_DOMAIN, LOCALES_DIR
from ..db.models import BotUser


async def get_lang(user_id):
    # Делаем запрос к базе, узнаем установленный язык
    try:
        user = await BotUser.get(tg_id=user_id)
    except:
        pass
    else:
        # Если пользователь найден - возвращаем его
        return user.lang


class ACLMiddleware(I18nMiddleware):
    # Каждый раз, когда нужно узнать язык пользователя - выполняется эта функция
    async def get_user_locale(self, action, args):
        user = types.User.get_current()
        # Возвращаем язык из базы ИЛИ (если не найден) - язык из Телеграма
        return await get_lang(user.id) or user.locale


def setup_middleware(dp):
    # Устанавливаем миддлварь
    i18n = ACLMiddleware(I18N_DOMAIN, LOCALES_DIR)
    dp.middleware.setup(i18n)
    return i18n

#
# Название - testbot, можете сменить на любое другое
#
# Запускаем первый раз
# 1. Вытаскиваем тексты из файлов (он сам находит)
# pybabel extract . -o locales/testbot.pot
# 2. Создаем папку для перевода на английский
# pybabel init -i locales/testbot.pot -d locales -D testbot -l en
# 3. То же, на русский
# pybabel init -i locales/testbot.pot -d locales -D testbot -l ru
# 4. То же, на украинский
# pybabel init -i locales/testbot.pot -d locales -D testbot -l uk
# 5. Переводим, а потом собираем переводы
# pybabel compile -d locales -D testbot
#
#
# Обновляем переводы
# 1. Вытаскиваем тексты из файлов, Добавляем текст в переведенные версии
# pybabel extract . -o locales/testbot.pot
# pybabel update -d locales -D testbot -i locales/testbot.pot
# 3. Вручную делаем переводы, а потом Собираем
# pybabel compile -d locales -D testbot