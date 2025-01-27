import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from database.database import delete_old_scheduled_messages, get_scheduled_messages, get_users_async, is_prediced, get_actual_gp_async
from dialogs.dop_functions import send_message
from aiogram.client.bot import DefaultBotProperties
from aiogram import Bot
from aiogram.enums import ParseMode


scheduler = AsyncIOScheduler()


async def schedule_message(chat_id: int, text: str, bot: Bot):
    if chat_id == 0:
        users = await get_users_async()
        actual_gp: int = await get_actual_gp_async()
        # Создаем список задач
        tasks = []

        for user in users:
            if not await is_prediced(user.id_telegram, actual_gp):
                tasks.append(send_message(user_id=chat_id, text=text, bot=bot))
                # Если количество задач достигло 25, ждем их завершения
            if len(tasks) == 25:
                await asyncio.gather(*tasks)
                tasks = []  # Сбрасываем список задач
                await asyncio.sleep(1)  # Пауза в 1 секунду, чтобы не превышать 25 сообщений в секунду

        # Отправляем оставшиеся сообщения, если они есть
        if tasks:
            await asyncio.gather(*tasks)
    else:
        await send_message(user_id=chat_id, text=text, bot=bot)

async def schedule_messages_on_start(bot):
    await delete_old_scheduled_messages()  # Удаляем старые сообщения
    messages = await get_scheduled_messages()
    for message in messages:
        send_time = message.send_time
        if send_time > datetime.now():  # Проверяем, что время отправки еще не прошло
            scheduler.add_job(schedule_message, 'date', run_date=send_time.strftime("%Y-%m-%d %H:%M:%S"), args=[message.chat_id, message.text, bot])

def start_scheduler():
    scheduler.start()
    # Периодическая задача для удаления старых сообщений каждые 10 минут
    scheduler.add_job(periodic_cleanup, 'interval', days=1)

async def periodic_cleanup():
    await delete_old_scheduled_messages()