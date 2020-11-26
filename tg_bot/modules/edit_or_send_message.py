from aiogram import types
from aiogram.utils.exceptions import MessageNotModified, TelegramAPIError


async def delete_message_with_protect(bot, chat_id, msg_id):
    try:
        await bot.delete_message(chat_id, msg_id)
        return True
    except TelegramAPIError as e:
        return False


async def edit_or_send_message(bot, message_or_call, parse_mode='HTML', kb=None, text=None, video=None, photo=None, anim=None, chat_id=None, disable_web=False):
    message = message_or_call if isinstance(message_or_call, types.Message) else message_or_call.message
    msg = None
    if photo or anim or video:
        try:
            msg = await bot.edit_message_caption(
                chat_id=message.chat.id if not chat_id else chat_id,
                message_id=message.message_id,
                text=text,
                parse_mode=parse_mode,
                reply_markup=kb,
            )
        except Exception as e:
            await delete_message_with_protect(bot, message.chat.id, message.message_id)
            if type(e) == MessageNotModified:
                pass
            elif anim:
                msg = await bot.send_animation(
                    chat_id=message.chat.id if not chat_id else chat_id,
                    animation=anim,
                    caption=text,
                    parse_mode=parse_mode,
                    reply_markup=kb,
                )
            elif video:
                msg = await bot.send_video(
                    chat_id=message.chat.id if not chat_id else chat_id,
                    video=video,
                    caption=text,
                    parse_mode=parse_mode,
                    reply_markup=kb,
                )
            else:
                msg = await bot.send_photo(
                    chat_id=message.chat.id if not chat_id else chat_id,
                    photo=photo,
                    caption=text,
                    parse_mode=parse_mode,
                    reply_markup=kb,
                )
    else:
        try:
            msg = await bot.edit_message_text(
                chat_id=message.chat.id if not chat_id else chat_id,
                message_id=message.message_id,
                text=text,
                parse_mode=parse_mode,
                reply_markup=kb,
                disable_web_page_preview=disable_web
            )
        except Exception as e:
            if type(e) == MessageNotModified:
                pass
            else:
                await delete_message_with_protect(bot, message.chat.id, message.message_id)
                msg = await bot.send_message(
                    chat_id=message.chat.id if not chat_id else chat_id,
                    text=text,
                    parse_mode=parse_mode,
                    reply_markup=kb,
                    disable_web_page_preview=disable_web
                )
    return msg