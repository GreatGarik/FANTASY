from aiogram import Bot
from aiogram.types import BotCommand


# Функция для настройки кнопки Menu бота
async def set_main_menu(bot: Bot):
    main_menu_commands = [BotCommand(
            command='/predict',
            description='Сделать прогноз на ближайший GP'),
        BotCommand(
            command='/registration',
            description='Регистрация в Fantasy'),
        BotCommand(
            command='/help',
            description='Информация о Fantasy'),
        BotCommand(
            command='/cancel',
            description='Сброс заполнения анкеты/прогноза'),
        BotCommand(
            command='/showdata',
            description='Показать данные пользователя'),
        BotCommand(
            command='/create_team',
            description='Создать команду'),
        BotCommand(
            command='/championship',
            description='Посмотеть актуальное положение в чемпионате')

    ]
    await bot.set_my_commands(main_menu_commands)