from datetime import datetime, date, time
from aiogram_dialog import Dialog, DialogManager, StartMode, Window, setup_dialogs, ShowMode
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput
from aiogram_dialog.widgets.kbd import Button, Cancel, Row, Column, Group, Select, Calendar
from aiogram import Router
from aiogram.types import Message, User, CallbackQuery, BufferedInputFile
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command, CommandStart, StateFilter, BaseFilter
from .getters import *
from sqlalchemy.util import await_only

from dataprocessing.excel_forms import entry_list, last_stage, process_championship_full, championship_team_full, \
    process_calculation_command
from dataprocessing.calculation_gp_drivers import calculation_drivers
from database.database import select_drivers, add_user, get_users, send_predict, get_predict, add_result, \
    show_result, get_actual_gp, add_points, show_result, show_points, get_result, check_res, show_points_all, \
    is_prediced, get_user_team, add_team, get_team, show_points_team_all, get_teams_fonts_colors, clear_results, \
    get_name_gp, get_users_by_name, change_user_name_async, change_user_number_async, get_grandprix_list, \
    update_driver_positions, update_grandprix


class IsAdmin(BaseFilter):
    async def __call__(self, message: Message, all_admins) -> bool:
        return message.from_user.id in all_admins


admin_dialog = Dialog(
    Window(
        Const('Это админка, нажми нужную кнопку'),
        Column(Button(
            text=Const('Обработка этапа'),
            id='button_stage',
            on_click=button_stage
        ),
        Button(
            text=Const('Таблицы'),
            id='button_tables',
            on_click=button_tables
        ),
        Button(
            text=Const('Открыть новый прогноз'),
            id='all_stages',
            on_click=button_open_predict
        ),
        Button(
            text=Const('Управление пользователями'),
            id='button_users',
            on_click=button_users)
        ),
        Button(
            text=Const('Управление командами'),
            id='button_team_management',
            on_click=button_team_management
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
        Const('Начать прием прогнозов сразу или выбрать дату и время начала?'),
        Column(
            Button(
                text=Const('Выбрать дату и время'),
                id='button_start_time_now',
                on_click=button_start_time_select),
            Button(
                text=Const('Начать прием сразу!'),
                id='button_start_time_select',
                on_click=button_start_time_now),
            Button(
                text=Const('Вернуться в главное меню'),
                id='button_menu',
                on_click=button_menu),
        ),
        state=AdminSG.datetime_start
    ),
    Window(
        Const(text='Установка даты и времени начала приёма прогнозов\nВыберите дату:'),
        Calendar(
            id='calendar_start',
            on_click=on_date_selected_start
        ),
        state=AdminSG.datetime_start_day,
    ),
    Window(
        Const(text='Установка даты и времени начала приёма прогнозов\nВыберите часы:'),
        Group(
            Select(
                Format('{item}'),
                id='datetime_start_hours',
                item_id_getter=lambda x: x,
                items='hours',
                on_click=on_date_selected_start_hours,
            ),
            Button(
                text=Const('Вернуться в главное меню'),
                id='button_menu',
                on_click=button_menu)
            ,
            width=6
        ),
        state=AdminSG.datetime_start_hours,
        getter=get_hours
    ),
    Window(
        Const(text='Установка даты и времени начала приёма прогнозов\nВыберите минуты:'),
        Group(
            Select(
                Format('{item}'),
                id='datetime_start_minutes',
                item_id_getter=lambda x: x,
                items='minutes',
                on_click=on_date_selected_start_minutes,
            ),
            Button(
                text=Const('Вернуться в главное меню'),
                id='button_menu',
                on_click=button_menu)
            ,
            width=2
        ),
        state=AdminSG.datetime_start_minutes,
        getter=get_minutes
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
            'Проверьте данные\n Вы открываете прогноз на {GP} GP\n Начало приема прогнозов {start}\n Без штрафа до {penalty}\n Окончание приема прогнозов {end}'),
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
    Window(
        Const('Это меню управления командами'),
        Column(
            Button(
                text=Const('Изменить настройки/состав команды'),
                id='button_users',
                on_click=button_edit_team),
            Button(
                text=Const('Удалить/добавить команду'),
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
        state=AdminSG.team_management
    ),
    Window(
        Const(text='Выберите команду для изменений:'),
        Group(
            Select(
                Format('{item[0]}'),
                id='team_id',
                item_id_getter=lambda x: x[1],
                items='all_teams',
                on_click=selected_team,
            ),
            width=2
            ),
            Row(Button(
                text=Const('Вернуться в главное меню'),
                id='button_menu',
                on_click=button_menu),
        ),
        state=AdminSG.edit_team,
        getter=all_teams
    ),
    Window(
        Const('Что меняем у команды?'),
        Column(
            Button(
                text=Const('Изменить состав'),
                id='button_users',
                on_click=button_edit_team),
            Button(
                text=Const('Изменить название'),
                id='button_show_users',
                on_click=button_show_users)
            ,
            Button(
                text=Const('Изменить название'),
                id='button_show_users',
                on_click=button_show_users)
            ,
            Button(
                text=Const('Изменить название'),
                id='button_show_users',
                on_click=button_show_users)
            ,
            Button(
                text=Const('Изменить название'),
                id='button_show_users',
                on_click=button_show_users)
            ,
            Button(
                text=Const('Вернуться в главное меню'),
                id='button_menu',
                on_click=button_menu)
            ),
        state=AdminSG.team_management
    ),
)

router: Router = Router()
router.include_router(admin_dialog)
setup_dialogs(router)


@router.message(IsAdmin(), Command(commands='admin'))
async def command_start_process(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(state=AdminSG.start, mode=StartMode.RESET_STACK)
