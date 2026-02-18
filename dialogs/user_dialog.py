import operator
from datetime import datetime, date, time
from aiogram_dialog import Dialog, DialogManager, StartMode, Window, setup_dialogs, ShowMode
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput, MessageInput
from aiogram_dialog.widgets.kbd import Button, Cancel, Row, Column, Group, Select, Calendar, Radio, Back, Url
from aiogram import Router, F
from aiogram.types import Message, User, CallbackQuery, BufferedInputFile
from aiogram.fsm.state import State, StatesGroup
from aiogram.enums import ContentType, ParseMode
from aiogram.filters import Command, CommandStart, StateFilter, BaseFilter
from .user_getters import *
from .admin_dialog import admin_dialog


class IsAdmin(BaseFilter):
    async def __call__(self, message: Message, all_admins) -> bool:
        return message.from_user.id in all_admins

user_dialog = Dialog(
    Window(
        Format('Здравствуйте, <b>{user_name}</b>'),
        Column(Button(
                text=Const('Регистрация в фэнтези'),
                id='all_stages',
                on_click=button_registration,
                when=F["unregistered"]
            ),
            Button(
            text=Const('🏎️ Отправить прогноз'),
            id='button_send_predict',
            on_click=button_send_predict,
            when=F['registered'] & F['active']
            ),
            Button(
                text=Const('Изменить имя'),
                id='button_change_name',
                on_click=button_registration,
                when=F['registered'] & F['can_change_name'] & ~F['is_user_in_request']
            ),

            Button(
                text=Const('Отправить заявку на участие в Fantasy'),
                id='button_send_active',
                on_click=button_send_request,
                when=F['registered'] & ~F['active']
            ),

            Button(
                text=Const('📜 Информация о фэнтези'),
                id='button_about',
                on_click=button_about
            ),
            Url(text=Const('💬 Чат F1 Fantasy by Silly Formula'),
                url=Const('https://t.me/+fa8OXqqblLxhODQy'),
                id='chat_tg_group'),
            Button(
                text=Const('✉️ Обратная связь'),
                id='feedback',
                on_click=button_feedback,
                when=F["registered"]
            ),
            Url(text=Const('👍🏻 Поделиться ботом'),
            url=Const('https://t.me/share/url?url=https://t.me/sillyf1fantasy_bot&text=Присоединяйся!'),
            id='button_share'),
            Button(
                text=Const('Админка'),
                id='button_admin',
                on_click=button_admin,
                when=F['admins']),
        ),

        state=UserSG.start,
        getter=user_name
    ),
    Window(Const('Я принимаю прогнозы на Фэнтези'),
        Url(text=Const('Ссылка на регламент Fantasy'),
            url=Const('https://docs.google.com/document/d/1s-qmH73Ji6zAX7U-M1q4unNKITnjgvIoIp_kPwkxx1Q'),
            id='button_reglament'),
        Url(text=Const('Группа ВК Silly Formula'),
            url=Const('https://vk.com/sillyformula'),
            id='button_vk_group'),
       Url(text=Const('Тема для регистраций команд в ВК'),
           url=Const('https://vk.com/topic-220163893_56068969'),
           id='button_vk_team_reg'),
        Url(text=Const('Телеграм канал Silly Formula'),
            url=Const('https://t.me/sillyformula'),
            id='button_tg_group'),
        Button(
            text=Const('Вернуться в главное меню'),
            id='button_menu',
            on_click=button_user_menu),
        state=UserSG.about_fantasy,
    ),
    Window(
        Const(text='При участии в чемпионате эти данные будут отображаться в таблице. Можно использовать псевдонимы в разумных пределах, согласно регламенту\nПожалуйста, введите ваше имя и фамилию латинским буквами через пробел:'),
        TextInput(
            type_factory=name_check,
            id='fill_form_name',
            on_success=fill_form_name,
            on_error=error_fill_form_name
        ),
        state=UserSG.fill_form_name,
    ),
    Window(
        Const(text='Введите Ваше сообщение для админов Fantasy:'),
        Button(
            text=Const('✕ Отмена'),
            id='cancel_feedback',
            on_click=cancel_feedback)
        ,
        TextInput(
            type_factory=str,
            id='feedback',
            on_success=feedback,
            on_error=error_feedback
        ),
        state=UserSG.feedback,
    ),
    Window(
        Format(text='Выберите <b>команду</b>:\n'
                    'Не забывайте про правило двух двигателей\n'
                    'Сейчас у Вас выбраны:\n'
                    '{engines}'),
        Group(
            Select(
                Format('{item}'),
                id='selected_team',
                item_id_getter=lambda x: x,
                items='teams_for_select',
                on_click=select_team,
            ),
            Button(
                text=Const('Вернуться в главное меню'),
                id='button_menu',
                on_click=button_user_menu)
            ,
            width=1
        ),
        state=UserSG.send_predict,
        getter=get_all_teams_predict
    ),
    Window(
        Format(text='Выберите <b>двигатель</b>:\n'
                    'Не забывайте про правило двух двигателей\n'
                    'Сейчас у Вас выбраны:\n'
                    '{engines}'),
        Group(
            Select(
                Format('{item}'),
                id='selected_engine',
                item_id_getter=lambda x: x,
                items='engines_for_select',
                on_click=select_engine,
            ),
            Back(Const('◀️ Назад'), id='back', on_click=back_select_engine),
            Button(
                text=Const('Вернуться в главное меню'),
                id='button_menu',
                on_click=button_user_menu)
            ,
            width=1
        ),
        state=UserSG.send_predict_engine,
        getter=get_all_engines_predict
    ),
    Window(
        Format(text='Выберите <b>первого пилота</b>:\n'
                    'Не забывайте про правило двух двигателей\n'
                    'Сейчас у Вас выбраны:\n'
                    '{engines}'),
        Group(
            Select(
                Format('{item[0]}'),
                id='select_first',
                item_id_getter=lambda x: f'{x[1]}:{x[2]}',
                items='drivers_for_select',
                on_click=select_first_driver,
            ),
            Back(Const('◀️ Назад'), id='back', on_click=back_select_first),
            Button(
                text=Const('Вернуться в главное меню'),
                id='button_menu',
                on_click=button_user_menu)
            ,
            width=1
        ),
        state=UserSG.send_predict_first,
        getter=get_all_drivers_predict
    ),
    Window(
        Format(text='Выберите <b>второго пилота</b>:\n'
                    'Не забывайте про правило двух двигателей\n'
                    'Сейчас у Вас выбраны:\n'
                    '{engines}'),
        Group(
            Select(
                Format('{item[0]}'),
                id='select_second',
                item_id_getter=lambda x: f'{x[1]}:{x[2]}',
                items='drivers_for_select',
                on_click=select_second_driver,
            ),
            Back(Const('◀️ Назад'), id='back', on_click=back_select_second),
            Button(
                text=Const('Вернуться в главное меню'),
                id='button_menu',
                on_click=button_user_menu)
            ,
            width=1
        ),
        state=UserSG.send_predict_second,
        getter=get_all_drivers_predict_second
    ),
    Window(
        Format(text='Выберите <b>третьего пилота</b>:\n'
                    'Не забывайте про правило двух двигателей\n'
                    'Сейчас у Вас выбраны:\n'
                    '{engines}'),
        Group(
            Select(
                Format('{item[0]}'),
                id='select_third',
                item_id_getter=lambda x: f'{x[1]}:{x[2]}',
                items='drivers_for_select',
                on_click=select_third_driver,
            ),
            Back(Const('◀️ Назад'), id='back', on_click=back_select_third),
            Button(
                text=Const('Вернуться в главное меню'),
                id='button_menu',
                on_click=button_user_menu)
            ,
            width=1
        ),
        state=UserSG.send_predict_third,
        getter=get_all_drivers_predict_third
    ),
    Window(
        Format(text='Выберите <b>четвертого пилота</b>:\n'
                    'Не забывайте про правило двух двигателей\n'
                    'Сейчас у Вас выбраны:\n'
                    '{engines}'),
        Group(
            Select(
                Format('{item[0]}'),
                id='select_fourth',
                item_id_getter=lambda x: f'{x[1]}:{x[2]}',
                items='drivers_for_select',
                on_click=select_fourth_driver,
            ),
            Back(Const('◀️ Назад'), id='back', on_click=back_select_fourth),
            Button(
                text=Const('Вернуться в главное меню'),
                id='button_menu',
                on_click=button_user_menu)
            ,
            width=1
        ),
        state=UserSG.send_predict_fourth,
        getter=get_all_drivers_predict_fourth
    ),
    Window(
        Format(text='Выберите победителя\n'
                    '<b>первой дуэли</b>:\n'
                    ),
        Group(
            Select(
                Format('{item}'),
                id='select_duel1',
                item_id_getter=lambda x: x,
                items='duelists_1',
                on_click=select_duel1,
            ),
            Back(Const('◀️ Назад'), id='back', on_click=back_duel1),
            Button(
                text=Const('Вернуться в главное меню'),
                id='button_menu',
                on_click=button_user_menu)
            ,
            width=1
        ),
        state=UserSG.select_duel1,
        getter=get_duel1
    ),
    Window(
        Format(text='Выберите победителя\n'
                    '<b>второй дуэли</b>:\n'
               ),
        Group(
            Select(
                Format('{item}'),
                id='select_duel2',
                item_id_getter=lambda x: x,
                items='duelists_2',
                on_click=select_duel2,
            ),
            Back(Const('◀️ Назад'), id='back', on_click=back_duel2),
            Button(
                text=Const('Вернуться в главное меню'),
                id='button_menu',
                on_click=button_user_menu)
            ,
            width=1
        ),
        state=UserSG.select_duel2,
        getter=get_duel2
    ),
    Window(
        Format(text='Выберите победителя\n'
                    '<b>третьей дуэли</b>:\n'
               ),
        Group(
            Select(
                Format('{item}'),
                id='select_duel3',
                item_id_getter=lambda x: x,
                items='duelists_3',
                on_click=select_duel3,
            ),
            Back(Const('◀️ Назад'), id='back', on_click=back_duel3),
            Button(
                text=Const('Вернуться в главное меню'),
                id='button_menu',
                on_click=button_user_menu)
            ,
            width=1
        ),
        state=UserSG.select_duel3,
        getter=get_duel3
    ),
    Window(
        Const(text='<b>Введите отставание от лидера в секундах (целое число)</b>:'),
        TextInput(
            id='loading_f1_result_sprint',
            type_factory=is_correct_gap,
            on_success=select_gap,
        ),
        state=UserSG.send_predict_gap
    ),
    Window(
        Const(text='<b>Введите количество круговых</b>:'),
        TextInput(
            id='loading_f1_result_sprint',
            type_factory=is_correct_laps,
            on_success=select_laps,
        ),
        state=UserSG.send_predict_laps
    ),
    Window(
        Format('Подтвердите Ваш прогноз на <b>{name_gp} GP</b>:\nКоманда: <b>{driver_team}</b>\nДвигатель: <b>{driver_engine}</b>\nПервый пилот: <b>{first_driver}</b>\nВторой пилот: <b>{second_driver}</b>\nТретий пилот: <b>{third_driver}</b>\nЧетвертый пилот: <b>{fourth_driver}</b>\n1 дуэль: <b>{select_duel1}</b>\n2 дуэль: <b>{select_duel2}</b>\n3 дуэль: <b>{select_duel3}</b>\nКоличество круговых: <b>{lapped}</b>'),
        Button(
            text=Const('Подтвердить'),
            id='button_confirm_predict',
            on_click=button_user_confirm_predict
        ),
        Button(
            text=Const('Ой, я ошибся, хочу ввести заново'),
            id='button_send_predict',
            on_click=button_send_predict
        ),
        Button(
            text=Const('В главное меню (без отправки прогноза)'),
            id='button_menu',
            on_click=button_user_menu)
        ,
        getter=predict_ending,
        state=UserSG.send_predict_ending,

    ),
)

router: Router = Router()
router.include_router(user_dialog)
router.include_router(admin_dialog)
setup_dialogs(router)


@router.message(Command(commands='start'))
async def command_start_process(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(state=UserSG.start, mode=StartMode.RESET_STACK)
