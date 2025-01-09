from aiogram import Bot

async def send_message(user_id: int, text: str, bot: Bot):
    try:
        await bot.send_message(user_id, text)
    except Exception as e:
        print(e)

