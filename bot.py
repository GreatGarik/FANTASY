import asyncio
import logging
from aiogram import Bot, Dispatcher
from config_data.config import Config, load_config
from handlers import user_handlers, other_handlers, admin_handlers
from keyboards.menu_button import set_main_menu
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode

# Инициализируем логгер
logger = logging.getLogger(__name__)

# Функция конфигурирования и запуска бота
async def main():
    # Конфигурируем логирование
    logging.basicConfig(
        level=logging.INFO,
        filename="py_log.log", filemode="a",
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s '
               u'[%(asctime)s] - %(name)s - %(message)s')

    # Выводим в консоль информацию о начале запуска бота
    logger.info('Starting bot')

    # Загружаем конфиг в переменную config
    config: Config = load_config()

    # Инициализируем бот и диспетчер
    bot: Bot = Bot(token=config.tg_bot.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp: Dispatcher = Dispatcher()

    # Отправка сообщения при запуске
    await bot.send_message(config.tg_bot.admin_id, text='Бот запущен')


    # Настраиваем кнопку Menu
    await set_main_menu(bot)

    # Регистрируем все хэндлеры
    dp.include_router(admin_handlers.router)
    dp.include_router(user_handlers.router)

    # Запускаем polling
    await dp.start_polling(bot)


if __name__ == '__main__':

    try:
        # Запускаем функцию main
        asyncio.run(main())

    except (KeyboardInterrupt, SystemExit):
        # Выводим в консоль сообщение об ошибке,
        # если получены исключения KeyboardInterrupt или SystemExit
        logger.error('Bot stopped!')
