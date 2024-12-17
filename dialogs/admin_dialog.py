from aiogram_dialog import Dialog, DialogManager, StartMode, Window, setup_dialogs
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Button, Cancel, Row, Column
from aiogram import Router
from aiogram.types import Message, User, CallbackQuery, BufferedInputFile
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command, CommandStart, StateFilter, BaseFilter
from dataprocessing.excel_forms import entry_list, last_stage, process_championship_full, championship_team_full, process_calculation_command
from dataprocessing.calculation_gp_drivers import calculation_drivers
from database.database import select_drivers, add_user, get_users, send_predict, get_predict, add_result, \
    show_result, get_actual_gp, add_points, show_result, show_points, get_result, check_res, show_points_all, \
    is_prediced, get_user_team, add_team, get_team, show_points_team_all, get_teams_fonts_colors, clear_results, \
    get_name_gp, get_maximus



class AdminSG(StatesGroup):
    start = State()
    users_menu = State()
    tables = State()
    stage = State()
    exit_admin = State()


class IsAdmin(BaseFilter):
    async def __call__(self, message: Message, all_admins) -> bool:
        return message.from_user.id in all_admins


async def go_back(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.back()


async def button_users(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(AdminSG.users_menu)


async def button_show_users(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    output = await entry_list()  # Получаем объект файла
    await callback.message.answer_document(
        document=BufferedInputFile(output.read(), filename='entry_list.xlsx')
    )
    output.close()  # Закрываем объект после использования
    await dialog_manager.switch_to(AdminSG.users_menu)


async def button_last_stage(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    output = await last_stage()  # Получаем объект файла
    await callback.message.answer_document(
        document=BufferedInputFile(output.read(), filename=f'results {get_name_gp(get_actual_gp())}.xlsx')
    )
    output.close()  # Закрываем объект после использования
    await dialog_manager.switch_to(AdminSG.tables)


async def button_drivers_champ(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    output = await process_championship_full()  # Получаем объект файла
    await callback.message.answer_document(
        document=BufferedInputFile(output.read(), filename='championship_points.xlsx')
    )
    output.close()  # Закрываем объект после использования
    await dialog_manager.switch_to(AdminSG.tables)


async def button_teams_champ(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    output = await championship_team_full()  # Получаем объект файла
    await callback.message.answer_document(
        document=BufferedInputFile(output.read(), filename='championship_team_points.xlsx')
    )
    output.close()  # Закрываем объект после использования
    await dialog_manager.switch_to(AdminSG.tables)


async def button_find_user(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await callback.message.answer('Я нашел следующих участников:')
    await dialog_manager.switch_to(AdminSG.users_menu)

async def button_calculate(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    gp = get_actual_gp()
    if check_res(gp):
        await callback.message.answer(f'Вы уже сделали расчет для этого GP', isable_web_page_preview=True)
    else:
        output = await process_calculation_command(calculation_drivers(gp))
        await callback.message.answer_document(
            document=BufferedInputFile(output.read(), filename='gp_results.xlsx')
        )
        output.close()  # Закрываем объект после использования

    await dialog_manager.switch_to(AdminSG.stage)

async def button_clear_result(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    clear_results(get_actual_gp())
    await callback.message.answer('Результат удалён')
    await dialog_manager.switch_to(AdminSG.stage)

async def button_tables(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(AdminSG.tables)

async def button_stage(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(AdminSG.stage)


async def button_menu(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(AdminSG.start)


async def button_exit(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await callback.message.answer('Вы, вышли из админки!')
    await dialog_manager.done()


admin_dialog = Dialog(
    Window(
        Const('Это админка, нажми нужную кнопку'),
        Column(Button(
            text=Const('Меню управления пользователями'),
            id='button_users',
            on_click=button_users)
        ),
        Button(
            text=Const('Таблицы'),
            id='button_tables',
            on_click=button_tables
        ),
        Button(
            text=Const('Обработка этапа'),
            id='button_stage',
            on_click=button_stage
        ),
        Button(
            text=Const('Выйти из админки'),
            id='button_exit',
            on_click=button_exit),
        state=AdminSG.start
    ),
    Window(
        Const('Это главное меню пользователей'),
        Column(
            Button(
                text=Const('Найти пользователя'),
                id='button_users',
                on_click=button_find_user
            ),
            Button(
                text=Const('Показать список пользователей'),
                id='button_show_users',
                on_click=button_show_users)
            ,
            Button(
                text=Const('Вернуться в главное меню'),
                id='button_menu',
                on_click=button_menu)
            ,
            Button(
                text=Const('Выйти из админки'),
                id='button_exit',
                on_click=button_exit),

        ),
        state=AdminSG.users_menu
    ),
    Window(
        Const('Это меню с таблицами'),
        Column(
            Button(
                text=Const('Таблица с результатами последнего этапа'),
                id='button_last_stage',
                on_click=button_last_stage
            ),
            Button(
                text=Const('Таблица личного зачёта'),
                id='button_drivers_champ',
                on_click=button_drivers_champ)
            ,
            Button(
                text=Const('Таблица командного зачёта'),
                id='button_teams_champ',
                on_click=button_teams_champ)
            ,
            Button(
                text=Const('Вернуться в главное меню'),
                id='button_menu',
                on_click=button_menu)
            ,
            Button(
                text=Const('Выйти из админки'),
                id='button_exit',
                on_click=button_exit),

        ),
        state=AdminSG.tables
    ),
    Window(
        Const('Управление этапом'),
        Column(
            Button(
                text=Const('Рассчитать результаты этапа'),
                id='button_calculate',
                on_click=button_calculate
            ),
            Button(
                text=Const('Загрузить результаты этапа'),
                id='button_drivers_champ',
                on_click=button_drivers_champ)
            ,
            Button(
                text=Const('Сбросить расчет этапа'),
                id='button_clear_result',
                on_click=button_clear_result)
            ,
            Button(
                text=Const('Вернуться в главное меню'),
                id='button_menu',
                on_click=button_menu)
            ,
            Button(
                text=Const('Выйти из админки'),
                id='button_exit',
                on_click=button_exit),

        ),
        state=AdminSG.stage
    ),
)

router: Router = Router()
router.include_router(admin_dialog)
setup_dialogs(router)


@router.message(IsAdmin(), Command(commands='admin'))
async def command_start_process(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(state=AdminSG.start, mode=StartMode.RESET_STACK)
