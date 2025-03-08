from aiogram import Bot
import logging

# Инициализируем логгер
logger = logging.getLogger(__name__)

async def send_message(user_id: int, text: str, bot: Bot):
    logging.basicConfig(
        level=logging.INFO,
        filename="py_log.log", filemode="a",
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s '
               u'[%(asctime)s] - %(name)s - %(message)s')
    try:
        await bot.send_message(user_id, text, disable_web_page_preview=True)
    except Exception as e:
        logger.warning(f'{e}, {user_id}')

