import asyncio

from aiogram.types import Message, InlineKeyboardMarkup

from load_all import bot


async def send_storage(user_id, message: Message, inline_markup: InlineKeyboardMarkup, max_attempts):
    attempt = 0
    success = False
    wait_message = None

    while attempt < max_attempts and not success:
        try:
            message = await asyncio.wait_for(message.edit_reply_markup(
                reply_markup=inline_markup,
            ), timeout=0.3)
            success = True
            if wait_message:
                await bot.delete_message(user_id, wait_message.message_id)
            return message
        except Exception as e:
            if not wait_message:
                wait_message = await bot.send_message(user_id, f"⏳")
            print(f"Attempt {attempt + 1}: {e}")
            attempt += 1
            await asyncio.sleep(0.5)

    if not success:
        print("Failed after maximum attempts.")

    if wait_message:
        await bot.delete_message(user_id, wait_message.message_id)

    return message