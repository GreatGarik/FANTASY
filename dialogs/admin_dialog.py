from datetime import datetime, date, time
from aiogram_dialog import Dialog, DialogManager, StartMode, Window, setup_dialogs, ShowMode
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput
from aiogram_dialog.widgets.kbd import Button, Cancel, Row, Column, Group, Select, Calendar
from aiogram import Router
from aiogram.types import Message, User, CallbackQuery, BufferedInputFile
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command, CommandStart, StateFilter, BaseFilter
from sqlalchemy.util import await_only

from dataprocessing.excel_forms import entry_list, last_stage, process_championship_full, championship_team_full, \
    process_calculation_command
from dataprocessing.calculation_gp_drivers import calculation_drivers
from database.database import select_drivers, add_user, get_users, send_predict, get_predict, add_result, \
    show_result, get_actual_gp, add_points, show_result, show_points, get_result, check_res, show_points_all, \
    is_prediced, get_user_team, add_team, get_team, show_points_team_all, get_teams_fonts_colors, clear_results, \
    get_name_gp, get_users_by_name, change_user_name_async, change_user_number_async, get_grandprix_list, \
    update_driver_positions, update_grandprix


class AdminSG(StatesGroup):
    start = State()
    users_menu = State()
    tables = State()
    stage = State()
    input_name = State()
    found_user = State()
    users_edit_select = State()
    new_name_user = State()
    new_number_user = State()
    open_predict = State()
    update_drivers_standing = State()
    datetime_penalty = State()
    datetime_penalty_hours = State()
    datetime_penalty_minutes = State()
    datetime_end = State()
    datetime_end_hours = State()
    datetime_end_minutes = State()
    predict_end = State()
    exit_admin = State()


class IsAdmin(BaseFilter):
    async def __call__(self, message: Message, all_admins) -> bool:
        return message.from_user.id in all_admins


def datetime_converter(o):
    if isinstance(o, datetime):
        return o.strftime('%Y-%m-%d %H:%M:%S')  # Форматируем как строку
    raise TypeError(f'Object of type {o.__class__.__name__} is not JSON serializable')


async def go_back(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.back()


async def button_users(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(AdminSG.users_menu)


async def correct_name(
        message: Message,
        widget: ManagedTextInput,
        dialog_manager: DialogManager,
        text: str) -> None:
    res = await get_users_by_name(text)
    if res:
        dialog_manager.dialog_data['found_users'] = res
        await dialog_manager.switch_to(AdminSG.found_user)
    else:
        await message.answer(text=f'Я никого не нашел.')
        await dialog_manager.switch_to(AdminSG.users_menu)


async def found_users(dialog_manager: DialogManager, **kwargs):
    return {'found_user': dialog_manager.dialog_data['found_users']}


async def user_selected(callback: CallbackQuery, widget: Select,
                        dialog_manager: DialogManager, user_tg_id: str):
    dialog_manager.dialog_data['user_tg_id'] = user_tg_id
    await dialog_manager.switch_to(AdminSG.users_edit_select)


async def button_change_user_name(callback: CallbackQuery, widget: Select,
                                  dialog_manager: DialogManager):
    await dialog_manager.switch_to(AdminSG.new_name_user)


async def button_change_user_number(callback: CallbackQuery, widget: Select,
                                    dialog_manager: DialogManager):
    await dialog_manager.switch_to(AdminSG.new_number_user)


async def new_name_user(message: Message, widget: Select,
                        dialog_manager: DialogManager, text: str):
    await change_user_name_async(dialog_manager.dialog_data['user_tg_id'], text)
    await message.answer(f'Вы изменили имя на {text}')
    dialog_manager.dialog_data.clear()
    await dialog_manager.switch_to(AdminSG.users_menu)


async def new_number_user(message: Message, widget: Select,
                          dialog_manager: DialogManager, text: str):
    await change_user_number_async(dialog_manager.dialog_data['user_tg_id'], text)
    await message.answer(f'Вы изменили номер на {text}')
    dialog_manager.dialog_data.clear()
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
    await dialog_manager.switch_to(AdminSG.input_name)


async def button_calculate(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    gp = get_actual_gp()
    if check_res(gp):
        await callback.message.answer(f'Вы уже сделали расчет для этого GP')
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


async def all_stages(**kwargs):
    return {'grandprix_list': await get_grandprix_list(datetime.now().year)}


async def predict_gp_selected(callback: CallbackQuery, widget: Select,
                              dialog_manager: DialogManager, item_id: str):
    dialog_manager.dialog_data['predict_gp_selected'] = int(item_id)
    await dialog_manager.switch_to(AdminSG.update_drivers_standing)


async def update_drivers_standing(
        message: Message,
        widget: ManagedTextInput,
        dialog_manager: DialogManager,
        text: str) -> None:
    await update_driver_positions(text)
    await dialog_manager.switch_to(AdminSG.datetime_penalty)


async def on_date_selected_penalty(callback: CallbackQuery, widget,
                                   dialog_manager: DialogManager, selected_date: date):
    dialog_manager.dialog_data['penalty_datetime'] = datetime.combine(selected_date, time.min).strftime(
        '%Y-%m-%d %H:%M:%S')
    await dialog_manager.switch_to(AdminSG.datetime_penalty_hours)


async def on_date_selected_penalty_hours(callback: CallbackQuery, widget,
                                         dialog_manager: DialogManager, item_id: int):
    selected_date: datetime = datetime.strptime(dialog_manager.dialog_data['penalty_datetime'], '%Y-%m-%d %H:%M:%S')
    dialog_manager.dialog_data['penalty_datetime'] = selected_date.replace(hour=int(item_id)).strftime(
        '%Y-%m-%d %H:%M:%S')
    await dialog_manager.switch_to(AdminSG.datetime_penalty_minutes)


async def on_date_selected_penalty_minutes(callback: CallbackQuery, widget,
                                           dialog_manager: DialogManager, item_id: int):
    selected_date: datetime = datetime.strptime(dialog_manager.dialog_data['penalty_datetime'], '%Y-%m-%d %H:%M:%S')
    dialog_manager.dialog_data['penalty_datetime'] = selected_date.replace(minute=int(item_id)).strftime(
        '%Y-%m-%d %H:%M:%S')
    await dialog_manager.switch_to(AdminSG.datetime_end)


async def on_date_selected_end(callback: CallbackQuery, widget,
                               dialog_manager: DialogManager, selected_date: date):
    dialog_manager.dialog_data['end_datetime'] = datetime.combine(selected_date, time.min).strftime('%Y-%m-%d %H:%M:%S')
    await dialog_manager.switch_to(AdminSG.datetime_end_hours)


async def on_date_selected_end_hours(callback: CallbackQuery, widget,
                                     dialog_manager: DialogManager, item_id: int):
    selected_date: datetime = datetime.strptime(dialog_manager.dialog_data['end_datetime'], '%Y-%m-%d %H:%M:%S')
    dialog_manager.dialog_data['end_datetime'] = selected_date.replace(hour=int(item_id)).strftime('%Y-%m-%d %H:%M:%S')
    await dialog_manager.switch_to(AdminSG.datetime_end_minutes)


async def on_date_selected_end_minutes(callback: CallbackQuery, widget,
                                       dialog_manager: DialogManager, item_id: int):
    selected_date: datetime = datetime.strptime(dialog_manager.dialog_data['end_datetime'], '%Y-%m-%d %H:%M:%S')
    dialog_manager.dialog_data['end_datetime'] = selected_date.replace(minute=int(item_id)).strftime(
        '%Y-%m-%d %H:%M:%S')
    await dialog_manager.switch_to(AdminSG.predict_end)


async def get_hours(dialog_manager, **kwargs):
    return {'hours': [i for i in range(24)]}


async def get_minutes(dialog_manager, **kwargs):
    return {'minutes': [0, 30]}


async def predict_end(dialog_manager: DialogManager, **kwargs):
    return {'GP': get_name_gp(dialog_manager.dialog_data['predict_gp_selected']),
            'penalty': dialog_manager.dialog_data['penalty_datetime'],
            'end': dialog_manager.dialog_data['end_datetime']}


async def button_confirm_predict(callback: CallbackQuery, button: Button, dialog_manager: DialogManager, **kwargs):
    pattern = '%Y-%m-%d %H:%M:%S'
    gp_id = dialog_manager.dialog_data['predict_gp_selected']
    time_penalty = dialog_manager.dialog_data['penalty_datetime']
    time_end = dialog_manager.dialog_data['end_datetime']
    await update_grandprix(gp_id=gp_id, time_penalty=datetime.strptime(time_penalty, pattern),
                           time_end=datetime.strptime(time_end, pattern))
    await callback.message.answer(f'Прогноз на {get_name_gp(gp_id)} открыт')
    dialog_manager.dialog_data.clear()
    #await (f'Прогноз на {get_name_gp(gp_id)} открыт')
    await dialog_manager.switch_to(AdminSG.start)




async def button_tables(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(AdminSG.tables)


async def button_stage(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(AdminSG.stage)


async def button_open_predict(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(AdminSG.open_predict)


async def button_menu(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
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
            text=Const('Открыть новый прогноз'),
            id='all_stages',
            on_click=button_open_predict
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
        Const(text='Введите полное имя пользователя'),
        TextInput(
            id='select_user',
            on_success=correct_name,
        ),
        state=AdminSG.input_name,
    ),
    Window(
        Const(text='Введите новое имя пользователя'),
        TextInput(
            id='new_name_user',
            on_success=new_name_user,
        ),
        state=AdminSG.new_name_user,
    ),
    Window(
        Const(text='Введите новый номер пользователя'),
        TextInput(
            type_factory=int,
            id='new_name_user',
            on_success=new_number_user,
        ),
        state=AdminSG.new_number_user,
    ),
    Window(
        Const(text='Выберите пользователя из найденных:'),
        Group(
            Select(
                Format('{item[name]}' + ' № {item[number]}'),
                id='user_tg_id',
                item_id_getter=lambda x: x['id_telegram'],
                items='found_user',
                on_click=user_selected,
            ),
            Button(
                text=Const('Вернуться в главное меню'),
                id='button_menu',
                on_click=button_menu)
            ,
            width=1
        ),
        state=AdminSG.found_user,
        getter=found_users
    ),
    Window(
        Const(text='Выберите этап на который открывается прогноз:'),
        Group(
            Select(
                Format('{item[0]}'),
                id='grndprix_id',
                item_id_getter=lambda x: x[1],
                items='grandprix_list',
                on_click=predict_gp_selected,
            ),
            Button(
                text=Const('Вернуться в главное меню'),
                id='button_menu',
                on_click=button_menu)
            ,
            width=2
        ),
        state=AdminSG.open_predict,
        getter=all_stages
    ),
    Window(
        Const(text='Введите актуальное положение пилотов:'),
        TextInput(
            type_factory=str,
            id='update_drivers_standing',
            on_success=update_drivers_standing,
        ),
        state=AdminSG.update_drivers_standing,
    ),
    Window(
        Const(text='Установка даты и времени до штрафа\nВыберите дату:'),
        Calendar(
            id='calendar_penalty',
            on_click=on_date_selected_penalty
        ),
        state=AdminSG.datetime_penalty,
    ),
    Window(
        Const(text='Установка даты и времени до штрафа\nВыберите часы:'),
        Group(
            Select(
                Format('{item}'),
                id='datetime_penalty_hours',
                item_id_getter=lambda x: x,
                items='hours',
                on_click=on_date_selected_penalty_hours,
            ),
            Button(
                text=Const('Вернуться в главное меню'),
                id='button_menu',
                on_click=button_menu)
            ,
            width=6
        ),
        state=AdminSG.datetime_penalty_hours,
        getter=get_hours
    ),
    Window(
        Const(text='Установка даты и времени до штрафа\nВыберите минуты:'),
        Group(
            Select(
                Format('{item}'),
                id='datetime_penalty_minutes',
                item_id_getter=lambda x: x,
                items='minutes',
                on_click=on_date_selected_penalty_minutes,
            ),
            Button(
                text=Const('Вернуться в главное меню'),
                id='button_menu',
                on_click=button_menu)
            ,
            width=2
        ),
        state=AdminSG.datetime_penalty_minutes,
        getter=get_minutes
    ),
    Window(
        Const(text='Установка даты и времени до конца приема прогнозов\nВыберите дату:'),
        Calendar(
            id='calendar_end',
            on_click=on_date_selected_end
        ),
        state=AdminSG.datetime_end,
    ),
    Window(
        Const(text='Установка даты и времени до штрафа\nВыберите часы:'),
        Group(
            Select(
                Format('{item}'),
                id='datetime_end_hours',
                item_id_getter=lambda x: x,
                items='hours',
                on_click=on_date_selected_end_hours,
            ),
            Button(
                text=Const('Вернуться в главное меню'),
                id='button_menu',
                on_click=button_menu)
            ,
            width=6
        ),
        state=AdminSG.datetime_end_hours,
        getter=get_hours
    ),
    Window(
        Const(text='Установка даты и времени до штрафа\nВыберите минуты:'),
        Group(
            Select(
                Format('{item}'),
                id='datetime_end_minutes',
                item_id_getter=lambda x: x,
                items='minutes',
                on_click=on_date_selected_end_minutes,
            ),
            Button(
                text=Const('Вернуться в главное меню'),
                id='button_menu',
                on_click=button_menu)
            ,
            width=2
        ),
        state=AdminSG.datetime_end_minutes,
        getter=get_minutes
    ),
    Window(
        Format(
            'Проверьте данные\n Вы открываете прогноз на {GP} GP\n Без штрафа до {penalty}\n Окончание приема прогнозов {end}'),
        Button(
            text=Const('Подтвердить'),
            id='button_confirm_predict',
            on_click=button_confirm_predict
        ),
        Button(
            text=Const('Вернуться в главное меню без сохранения'),
            id='button_menu',
            on_click=button_menu)
        ,
        getter=predict_end,
        state=AdminSG.predict_end,

    ),
    Window(
        Format('Что мы хотим сделать с пользователем'),
        Column(
            Button(
                text=Const('Изменить имя'),
                id='button_change_user_name',
                on_click=button_change_user_name
            ),
            Button(
                text=Const('Изменить номер'),
                id='button_change_user_number',
                on_click=button_change_user_number,
            )
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
        state=AdminSG.users_edit_select
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
