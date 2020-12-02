from aiogram import executor
from tortoise import Tortoise

from tg_bot.load_all import bot


async def on_shutdown(dp):
    await bot.close()
    await dp.storage.close()
    await dp.storage.wait_closed()
    await Tortoise.close_connections()


async def on_startup(dp):
    await bot.send_message("446162145", "Bot is running!")


from tg_bot.dialogs.general.handlers import dp
executor.start_polling(dp, on_shutdown=on_shutdown, on_startup=on_startup, skip_updates=True)
