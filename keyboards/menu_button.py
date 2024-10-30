from aiogram import Bot
from aiogram.types import BotCommand


# Функция для настройки кнопки Menu бота
async def set_main_menu(bot: Bot):
    main_menu_commands = [BotCommand(
        command='/start',
        description='На старт!'),
        BotCommand(
            command='/help',
            description='Если хочешь узнать, что я делаю'),
        BotCommand(
            command='/predict',
            description='Сделать прогноз на ближайший GP'),
    ]
    await bot.set_my_commands(main_menu_commands)