import operator
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Radio, Back
from aiogram import Router, F
from aiogram.enums import ContentType, ParseMode
from aiogram.filters import Command, CommandStart, StateFilter, BaseFilter
from .getters import *
from aiogram_dialog import Dialog, DialogManager, StartMode, Window, setup_dialogs, ShowMode
from aiogram_dialog.widgets.kbd import Button, Cancel, Row, Column, Group, Select, Calendar, Radio, Back, Url


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
            text=Const('Управление гонщиками F1'),
            id='button_f1_drivers',
            on_click=button_f1_drivers
        ),
        Button(
            text=Const('Отправить сообщение'),
            id='button_send_message',
            on_click=button_send_message
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
                text=Const('Последние зарегистрированные пользователи'),
                id='button_new_users',
                on_click=button_new_users)
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
        Const('Меню отправки сообщения'),
        Column(
        Button(
                text=Const('Отправить всем'),
                id='button_send_all',
                on_click=button_send_all)
            ,
            Button(
                text=Const('Найти пользователя для отправки сообщения'),
                id='button_users',
                on_click=button_find_user
            ),
            Button(
                text=Const('Отправить участникам без команды'),
                id='button_send_no_team',
                on_click=button_send_no_team
            ),
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
        state=AdminSG.send_message
    ),
    Window(
        Const(text='Введите сообщение для отправки'),
        Button(
            text=Const('✕ Отмена'),
            id='cancel_send_message',
            on_click=cancel_send_message)
        ,
        TextInput(
            id='send_all',
            on_success=send_all,
        ),
        state=AdminSG.send_all,
    ),
    Window(
        Const(text='Введите сообщение для отправки'),
        Button(
            text=Const('✕ Отмена'),
            id='cancel_send_message',
            on_click=cancel_send_message)
        ,
        TextInput(
            id='send_no_team',
            on_success=send_no_team,
        ),
        state=AdminSG.send_no_team,
    ),

    Window(
        Const(text='Введите полное имя пользователя'),
        Button(
            text=Const('✕ Отмена'),
            id='cancel_user_menu',
            on_click=cancel_user_menu)
        ,
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
        Button(
            text=Const('✕ Отмена'),
            id='cancel_open_predict',
            on_click=cancel_open_predict)
        ,
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
            'Проверьте данные\n Вы открываете прогноз на <b>{GP} GP</b>\n Начало приема прогнозов <b>{start}</b>\n Без штрафа до <b>{penalty}</b>\n Окончание приема прогнозов <b>{end}</b>'),
        Button(
            text=Const('Подтвердить'),
            id='button_confirm_predict',
            on_click=button_confirm_predict
        ),
        Button(
            text=Const('Вернуться в главное меню без открытия прогноза'),
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
                text=Const('Отправить сообщение'),
                id='button_send_message_one',
                on_click=button_send_all
            ),
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
                text=Const('Удалить номер'),
                id='button_delite_user_number',
                on_click=button_delite_user_number,
            )
            ,
            Button(
                text=Const('Забанить пользователя'),
                id='button_ban_user',
                on_click=button_ban_user,
            )
            ,
            Button(
                text=Const('Разбанить пользователя'),
                id='button_unban_user',
                on_click=button_unban_user,
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
                on_click=loading_f1_results)
            ,
            Button(
                text=Const('Сбросить расчет этапа'),
                id='button_clear_result',
                on_click=button_clear_result)
            ,
            Button(
                text=Const('Получить все прогнозы'),
                id='button_get_all_predict',
                on_click=button_get_all_predict)
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
        Format('Загрузка результатов этапа'),
        Column(
            Button(
                text=Const('Спринт'),
                id='button_f1_sprint',
                on_click=button_f1_sprint,
                when=F["sprint"]
            ),
            Button(
                text=Const('Квалификация'),
                id='button_f1_quali',
                on_click=button_f1_quali)
            ,
            Button(
                text=Const('Гонка'),
                id='button_f1_race',
                on_click=button_f1_race)
            ,
            Back(Const('◀️'), id='back'),
            Button(
                text=Const('Вернуться в главное меню'),
                id='button_menu',
                on_click=button_menu)
            ,
        ),
        state=AdminSG.loading_f1_results,
        getter=sprint
    ),
    Window(
        Const(text='Введите результат спринта'),
        Button(
            text=Const('✕ Отмена'),
            id='cancel_loading_f1_results',
            on_click=cancel_loading_f1_results)
        ,
        TextInput(
            id='loading_f1_result_sprint',
            type_factory=str,
            on_success=loading_f1_result_sprint,
        ),
        state=AdminSG.loading_f1_result_sprint,
    ),
    Window(
        Const(text='Введите результат квалификации'),
        Button(
            text=Const('✕ Отмена'),
            id='cancel_loading_f1_results',
            on_click=cancel_loading_f1_results)
        ,
        TextInput(
            id='loading_f1_result_quali',
            type_factory=str,
            on_success=loading_f1_result_quali,
        ),
        state=AdminSG.loading_f1_result_quali,
    ),
    Window(
        Const(text='Введите результат гонки'),
        Button(
            text=Const('✕ Отмена'),
            id='cancel_loading_f1_results',
            on_click=cancel_loading_f1_results)
        ,
        TextInput(
            id='loading_f1_result_race',
            type_factory=str,
            on_success=loading_f1_result_race,
        ),
        state=AdminSG.loading_f1_result_race,
    ),
    Window(
        Const('Это меню управления командами'),
        Column(
            Button(
                text=Const('Изменить настройки/состав команды'),
                id='button_users',
                on_click=button_edit_team),
            Button(
                text=Const('Добавить команду'),
                id='button_show_users',
                on_click=button_add_team)
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
                item_id_getter=lambda x: f'{x[0]}^{x[1]}',
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
        Format('Что меняем у команды <b>{team_name}</b>?'),

        Column(
            Button(
                text=Const('Изменить состав'),
                id='change_team_members',
                on_click=change_team_members),
            Button(
                text=Const('Изменить логотип'),
                id='change_team_logo',
                on_click=change_team_logo)
            ,
            Button(
                text=Const('Цвет фона/текста'),
                id='change_team_name_color',
                on_click=change_team_name_color)
            ,
            Button(
                text=Const('Цвет/шрифт номеров'),
                id='change_team_number_font',
                on_click=change_team_number_font)
            ,
            Button(
                text=Const('Сменить название команды'),
                id='change_team_name',
                on_click=change_team_name)
            ,
            Button(
                text=Const('Удалить команду'),
                id='delete_team',
                on_click=delete_team)
            ,
            Button(
                text=Const('Вернуться в главное меню'),
                id='button_menu',
                on_click=button_menu)
            ),
        state=AdminSG.edit_team_menu,
        getter=getter_team_name
    ),
    Window(
        Const(text='Введите название шрифта номера'),
        Button(
            text=Const('✕ Отмена'),
            id='cancel_team',
            on_click=cancel_team_edit)
        ,
        TextInput(
            id='team_number_font_input',
            type_factory=str,
            on_success=team_number_font_input,
        ),
        state=AdminSG.change_team_number_font_font,
    ),
    Window(
        Const(text='Введите цвет номера'),
        Button(
            text=Const('✕ Отмена'),
            id='cancel_team',
            on_click=cancel_team_edit)
        ,
        TextInput(
            id='team_number_font_color_input',
            type_factory=str,
            on_success=team_number_font_color_input,
        ),
        state=AdminSG.change_team_number_font_color,
    ),
    Window(
        Const(text='Номер курсивом или нет'),
        Button(
            text=Const('✕ Отмена'),
            id='cancel_team',
            on_click=cancel_team_edit)
        ,
        Row(
            Radio(
                checked_text=Format('🔘 {item[0]}'),
                unchecked_text=Format('⚪️ {item[0]}'),
                id='radio_italic',
                item_id_getter=operator.itemgetter(1),
                items=[('Да', 1), ('Нет', 0)],
                on_click=change_team_number_font_record,
            ),
        ),
        state=AdminSG.change_team_number_font_italic,
    ),
    Window(Const(text='Выберите цвет шрифта команды'),
        Button(
            text=Const('✕ Отмена'),
            id='cancel_team',
            on_click=cancel_team_edit)
        ,
        Row(
            Radio(
                checked_text=Format('🔘 {item[0]}'),
                unchecked_text=Format('⚪️ {item[0]}'),
                id='radio_font_color',
                item_id_getter=operator.itemgetter(1),
                items=[('Чёрный', '000000'), ('Белый', 'FFFFFF')],
                on_click=team_font_color,
            ),
        ),
        state=AdminSG.change_team_font_color,
    ),
    Window(
        Const(text='Введите цвет фона названия команды'),
        Button(
            text=Const('✕ Отмена'),
            id='cancel_team',
            on_click=cancel_team_edit)
        ,
        TextInput(
            id='team_background_color_input',
            type_factory=str,
            on_success=team_background_color,
        ),
        state=AdminSG.change_team_background_color,
    ),
    Window(
        Const(text='Пришлите мне логотип команды в формате png, размер 140х49'),
        Button(
            text=Const('✕ Отмена'),
            id='cancel_team',
            on_click=cancel_team_edit)
        ,
        MessageInput(
            func=team_logo_receive,
            content_types=ContentType.PHOTO,
        ),
        state=AdminSG.change_team_logo,
    ),
    Window(
        Const(text='Введите новое название команды'),
        Button(
            text=Const('✕ Отмена'),
            id='cancel_team',
            on_click=cancel_team_edit)
        ,
        TextInput(
            id='new_team_name',
            type_factory=str,
            on_success=new_team_name,
        ),
        state=AdminSG.change_team_name,
    ),
    Window(
        Const(text='Напишите <b>ДА</b> если Вы уверены, что хотите удалить команду, если вы введете, что-то другое Вы вернетесь в меню команд'),
        Button(
            text=Const('✕ Отмена'),
            id='cancel_team',
            on_click=cancel_team_edit)
        ,
        TextInput(
            id='delite_team_confirmation',
            type_factory=is_yes,
            on_success=delete_team_confirmation,
            on_error=delete_team_not_confirmed,
        ),
        state=AdminSG.delete_team,
    ),
    Window(
        Const(text='Введите название команды'),
        Button(
            text=Const('✕ Отмена'),
            id='cancel_team',
            on_click=cancel_team)
        ,
        TextInput(
            id='new_team',
            type_factory=str,
            on_success=new_team,
        ),
        state=AdminSG.new_team,
    ),
    Window(
        Const(text='Сейчас такой состав команды, выберите поле для замены'),
        Group(
            Select(
                Format('{item[0]}'),
                id='team_member_id',
                item_id_getter=lambda x: f'{x[0]}^{x[1]}',
                items='team_members',
                on_click=selected_team_member,
            ),
            width=1
            ),
            Button(
            text=Const('✕ Отмена'),
            id='cancel_team',
            on_click=cancel_team_edit)
            ,
            Row(Button(
                text=Const('Вернуться в главное меню'),
                id='button_menu',
                on_click=button_menu),
        ),
        state=AdminSG.team_members,
        getter=team_members
    ),
    Window(
        Format('Что делаем с участником команды?'),

        Column(
            Button(
                text=Const('Удалить'),
                id='delite_team_members',
                on_click=delite_team_members),
            Button(
                text=Const('Заменить на нового'),
                id='replace_team_member',
                on_click=replace_team_member)
            ,
            Button(
                text=Const('Вернуться в главное меню'),
                id='button_menu',
                on_click=button_menu)
            ),
        state=AdminSG.team_members_menu,
    ),
    Window(
        Const(text='Введите полное имя пилота, которого вы хотите добавить'),
        TextInput(
            id='enter_team_member',
            type_factory=str,
            on_success=enter_team_member,
        ),
        state=AdminSG.enter_team_member,
    ),
    Window(
        Const(text='Выберите пользователя из найденных:'),
        Group(
            Select(
                Format('{item[name]}' + ' № {item[number]}'),
                id='user_id',
                item_id_getter=lambda x: x['id'],
                items='found_user',
                on_click=member_selected,
            ),
            Button(
                text=Const('Вернуться в главное меню'),
                id='button_menu',
                on_click=button_menu)
            ,
            width=1
        ),
        state=AdminSG.found_user_for_member,
        getter=found_users
    ),
    Window(
        Const('Меню управления пилотами F1'),
        Column(Button(
            text=Const('Заменить участвующего пилота'),
            id='replace_driver',
            on_click=replace_driver
        ),
        Button(
            text=Const('Добавить пилота'),
            id='add_driver',
            on_click=add_driver
        ),
        Button(
            text=Const('Изменить команду пилота'),
            id='changing_driver',
            on_click=changing_driver
        ),

        Button(
            text=Const('Вернуться в главное меню'),
            id='button_menu',
            on_click=button_menu)
        ),
        state=AdminSG.f1_drivers_menu
    ),
    Window(
        Const(text='Выберите пилота для замены:'),
        Group(
            Select(
                Format('{item.driver_name}'),
                id='f1_driver_active',
                item_id_getter=lambda x: x.driver_name,
                items='f1_drivers_active',
                on_click=f1_driver_active_selected,
            ),

            Button(
                text=Const('Вернуться в главное меню'),
                id='button_menu',
                on_click=button_menu)
            ,
            width=1
        ),
        state=AdminSG.f1_drivers_active,
        getter=f1_drivers_active
    ),
    Window(
        Const(text='Выберите пилота, который будет заменять:'),
        Group(
            Select(
                Format('{item.driver_name}'),
                id='f1_driver_deactivated',
                item_id_getter=lambda x: x.driver_name,
                items='f1_driver_deactivated',
                on_click=f1_drivers_deactivated_selected,
            ),
            Button(
                text=Const('Вернуться в главное меню'),
                id='button_menu',
                on_click=button_menu)
            ,
            width=1
        ),
        state=AdminSG.f1_drivers_deactivated,
        getter=f1_driver_deactivated
    ),
    Window(
        Const(text='Введите пилота'),
        Button(
            text=Const('✕ Отмена'),
            id='cancel_f1_driver',
            on_click=cancel_f1_driver)
        ,
        TextInput(
            id='add_f1_driver',
            type_factory=str,
            on_success=add_f1_driver,
        ),
        state=AdminSG.add_f1_driver,
    ),
    Window(
        Const(text='Выберите команду нового пилота:'),
        Group(
            Select(
                Format('{item}'),
                id='add_f1_driver_team',
                item_id_getter=lambda x: x,
                items='f1_teams_active',
                on_click=add_f1_driver_team,
            ),
            Button(
                text=Const('Вернуться в главное меню'),
                id='button_menu',
                on_click=button_menu)
            ,
            width=1
        ),
        state=AdminSG.add_f1_driver_team,
        getter=f1_teams_active
    ),
Window(
        Const(text='Выберите пилота, который будет заменять:'),
        Group(
            Select(
                Format('{item.driver_name}'),
                id='f1_drivers_all',
                item_id_getter=lambda x: x.driver_name,
                items='f1_drivers_all',
                on_click=f1_drivers_all_selected,
            ),
            Button(
                text=Const('Вернуться в главное меню'),
                id='button_menu',
                on_click=button_menu)
            ,
            width=1
        ),
        state=AdminSG.f1_driver_change_team,
        getter=f1_drivers_all
    ),
    Window(
        Const(text='Выберите новую команду пилота:'),
        Group(
            Select(
                Format('{item}'),
                id='f1_driver_change_team_teams',
                item_id_getter=lambda x: x,
                items='f1_teams_active',
                on_click=f1_driver_change_team_teams,
            ),
            Button(
                text=Const('Вернуться в главное меню'),
                id='button_menu',
                on_click=button_menu)
            ,
            width=1
        ),
        state=AdminSG.f1_driver_change_team_teams,
        getter=f1_teams_active
    ),
)
'''
admin_router: Router = Router()
admin_router.include_router(admin_dialog)
setup_dialogs(admin_router)


@admin_router.message(IsAdmin(), Command(commands='admin'))
async def command_start_process(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(state=AdminSG.start, mode=StartMode.RESET_STACK)
'''
