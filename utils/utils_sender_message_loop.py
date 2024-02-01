import asyncio

from aiogram.types import Message, InlineKeyboardMarkup

from load_all import bot


async def send_storage_folders(user_id, message: Message, text: str, inline_markup: InlineKeyboardMarkup, max_attempts):
    return await send_storage(
        user_id=user_id,
        message=message,
        text=text,
        inline_markup=inline_markup,
        max_attempts=max_attempts
    )
    #return result


async def send_storage_with_items(user_id, message: Message, inline_markup: InlineKeyboardMarkup, max_attempts):
    return await send_storage(
        user_id=user_id,
        message=message,
        inline_markup=inline_markup,
        max_attempts=max_attempts,
        with_wait_message=True
    )
    #return result


async def send_storage(
        user_id: int,
        message: Message,
        inline_markup: InlineKeyboardMarkup,
        max_attempts: int,
        text: str = None,
        with_wait_message=False
):
    attempt = 0
    success = False
    wait_message = None

    while attempt < max_attempts and not success:
        try:
            if (message.reply_markup
                    and len(inline_markup.inline_keyboard) <= len(message.reply_markup.inline_keyboard)):
                return message
            if not text:
                print(f"inline_markup.inline_keyboard len {len(inline_markup.inline_keyboard)}")
                return await asyncio.wait_for(message.edit_reply_markup(
                    reply_markup=inline_markup,
                ), timeout=1)
            else:
                message = await asyncio.wait_for(bot.edit_message_text(
                    chat_id=user_id,
                    message_id=message.message_id,
                    text=text,
                    reply_markup=inline_markup,
                ), timeout=1)

            success = True
            await delete_wait_message(user_id, wait_message)
            await asyncio.sleep(0.3)
            return message

        except Exception as e:
            wait_message = await send_wait_message(user_id, with_wait_message, wait_message)
            print(f"Attempt {attempt + 1}: {e}")
            attempt += 1
            await asyncio.sleep(0.3)

    if not success:
        print("Failed after maximum attempts.")

    await delete_wait_message(user_id, wait_message)
    return message


async def send_wait_message(user_id, with_wait_message, wait_message=None):
    if with_wait_message and not wait_message:
        wait_message = await bot.send_message(user_id, "⏳")
    return wait_message


async def delete_wait_message(user_id, wait_message=None):
    if wait_message:
        await bot.delete_message(user_id, wait_message.message_id)