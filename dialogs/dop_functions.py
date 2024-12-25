from aiogram import Bot

async def send_message(user_id: int, text: str, bot: Bot):
    await bot.send_message(user_id, text)

