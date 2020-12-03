from aiogram import types, Bot
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import MessageNotModified, TelegramAPIError


async def delete_message_with_protect(bot, chat_id, msg_id):
    try:
        await bot.delete_message(chat_id, msg_id)
        return True
    except TelegramAPIError as e:
        return False


async def edit_or_send_message(bot: Bot, message_or_call: [types.Message, types.CallbackQuery],
                               state: FSMContext = None, message_id=None, parse_mode='HTML',
                               kb=None, text=None, video=None, photo=None, anim=None, chat_id=None, disable_web=False):
    was_msg = True if isinstance(message_or_call, types.Message) else False
    message = message_or_call if isinstance(message_or_call, types.Message) else message_or_call.message
    msg = None
    message_id = (await state.get_data()).get("edit_msg_id") if state and not message_id else message_id
    if photo or anim or video:
        try:
            msg = await bot.edit_message_caption(
                chat_id=message.chat.id if not chat_id else chat_id,
                message_id=message.message_id if not message_id else message_id,
                caption=text,
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
                message_id=message.message_id if not message_id else message_id,
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
    if was_msg:
        await message.delete()
    if isinstance(types.Message, msg):
        await state.update_data({"edit_msg_id": msg.message_id})
    return msg
