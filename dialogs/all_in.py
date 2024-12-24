from datetime import datetime, date, time
import os
from aiogram.fsm.state import State, StatesGroup
from aiogram_dialog import Dialog, DialogManager, StartMode, Window, setup_dialogs, ShowMode
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput, MessageInput
from aiogram_dialog.widgets.kbd import Button, Cancel, Row, Column, Group, Select, Calendar
from aiogram.types import Message, User, CallbackQuery, BufferedInputFile
from string import ascii_letters, digits
from dataprocessing.excel_forms import entry_list, last_stage, process_championship_full, championship_team_full, \
    process_calculation_command
from dataprocessing.calculation_gp_drivers import calculation_drivers
from database.database import select_drivers, add_user, get_users, send_predict, get_predict, add_result, \
    show_result, get_actual_gp, add_points, show_result, show_points, get_result, check_res, show_points_all, \
    is_prediced, get_user_team, add_team, get_team, show_points_team_all, get_teams_fonts_colors, clear_results, \
    get_name_gp, get_users_by_name, change_user_name_async, change_user_number_async, get_grandprix_list, \
    update_driver_positions, update_grandprix, get_all_teams, update_team, create_team_only_name, get_team_members, update_or_remove_team_member, select_drivers_async, update_driver_nextgp, create_f1_driver, update_driver_team, update_grandprix_result, get_users_async, add_user_async, get_end_grandprix_by_id, get_start_grandprix_by_id, get_penalty_grandprix_by_id
from datetime import datetime, date, time
import os
from aiogram.fsm.state import State, StatesGroup
from aiogram_dialog import Dialog, DialogManager, StartMode, Window, setup_dialogs, ShowMode
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput, MessageInput
from aiogram_dialog.widgets.kbd import Button, Cancel, Row, Column, Group, Select, Calendar
from aiogram.types import Message, User, CallbackQuery, BufferedInputFile
from dataprocessing.excel_forms import entry_list, last_stage, process_championship_full, championship_team_full, \
    process_calculation_command
from dataprocessing.calculation_gp_drivers import calculation_drivers
from database.database import select_drivers, add_user, get_users, send_predict, get_predict, add_result, \
    show_result, get_actual_gp, add_points, show_result, show_points, get_result, check_res, show_points_all, \
    is_prediced, get_user_team, add_team, get_team, show_points_team_all, get_teams_fonts_colors, clear_results, \
    get_name_gp, get_users_by_name, change_user_name_async, change_user_number_async, get_grandprix_list, \
    update_driver_positions, update_grandprix, get_all_teams, update_team, create_team_only_name, get_team_members, update_or_remove_team_member, select_drivers_async, update_driver_nextgp, create_f1_driver, update_driver_team, update_grandprix_result

import operator
from datetime import datetime, date, time
from aiogram_dialog import Dialog, DialogManager, StartMode, Window, setup_dialogs, ShowMode
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput, MessageInput
from aiogram_dialog.widgets.kbd import Button, Cancel, Row, Column, Group, Select, Calendar, Radio, Back
from aiogram import Router, F
from aiogram.types import Message, User, CallbackQuery, BufferedInputFile
from aiogram.fsm.state import State, StatesGroup
from aiogram.enums import ContentType, ParseMode
from aiogram.filters import Command, CommandStart, StateFilter, BaseFilter
from .getters import *

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
    datetime_start = State()
    datetime_start_day = State()
    datetime_start_hours = State()
    datetime_start_minutes = State()
    datetime_penalty = State()
    datetime_penalty_hours = State()
    datetime_penalty_minutes = State()
    datetime_end = State()
    datetime_end_hours = State()
    datetime_end_minutes = State()
    predict_end = State()
    team_management = State()
    edit_team = State()
    edit_team_menu = State()
    change_team_font_color = State()
    change_team_background_color = State()
    change_team_number_font = State()
    change_team_number_font_font = State()
    change_team_number_font_color = State()
    change_team_number_font_italic = State()
    change_team_logo = State()
    change_team_name = State()
    new_team = State()
    team_members = State()
    team_members_menu = State()
    enter_team_member = State()
    found_user_for_member = State()
    member_selected = State()
    f1_drivers_menu = State()
    f1_drivers_active = State()
    f1_drivers_deactivated = State()
    add_f1_driver = State()
    add_f1_driver_team = State()
    f1_driver_change_team = State()
    f1_driver_change_team_teams = State()
    loading_f1_results = State()
    loading_f1_result_sprint = State()
    loading_f1_result_quali = State()
    loading_f1_result_race = State()
    exit_admin = State()

class UserSG(StatesGroup):
    start = State()
    fill_form_name = State()
    send_predict = State()
    send_predict_engine = State()
    send_predict_first = State()
    send_predict_second = State()
    send_predict_third = State()
    send_predict_fourth = State()
    send_predict_gap = State()
    send_predict_laps = State()
    send_predict_ending = State()

async def go_back(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.back()


async def button_users(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(AdminSG.users_menu)


async def correct_name(message: Message,widget: ManagedTextInput,dialog_manager: DialogManager,text: str) -> None:
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


async def button_change_user_name(callback: CallbackQuery, button: Button,
                                  dialog_manager: DialogManager):
    await dialog_manager.switch_to(AdminSG.new_name_user)


async def button_change_user_number(callback: CallbackQuery, button: Button,
                                    dialog_manager: DialogManager):
    await dialog_manager.switch_to(AdminSG.new_number_user)


async def new_name_user(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str) -> None:
    await change_user_name_async(dialog_manager.dialog_data['user_tg_id'], text)
    await message.answer(f'Вы изменили имя на {text}')
    dialog_manager.dialog_data.clear()
    await dialog_manager.switch_to(AdminSG.users_menu)


async def new_number_user(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str) -> None:
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

async def button_edit_team(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(AdminSG.edit_team)


async def all_teams(**kwargs):
    return {'all_teams': await get_all_teams()}

async def button_add_team(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(AdminSG.new_team)

async def selected_team(callback: CallbackQuery, button: Button, dialog_manager: DialogManager, team_str :str):
    team = team_str.split('^')
    dialog_manager.dialog_data['team_id'] = team[1]
    dialog_manager.dialog_data['team_name'] = team[0]
    await dialog_manager.switch_to(AdminSG.edit_team_menu)

async def getter_team_name(dialog_manager: DialogManager, **kwargs):
    return {'team_name': dialog_manager.dialog_data['team_name']}

async def change_team_number_font(callback: CallbackQuery, button: Button, dialog_manager: DialogManager, **kwargs):
    await dialog_manager.switch_to(AdminSG.change_team_number_font_font)


async def team_number_font_input(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str) -> None:
    dialog_manager.dialog_data['team_number_font_font'] = text
    await dialog_manager.switch_to(AdminSG.change_team_number_font_color)

async def team_number_font_color_input(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str) -> None:
    dialog_manager.dialog_data['team_number_font_color_input'] = text
    await dialog_manager.switch_to(AdminSG.change_team_number_font_italic)

async def change_team_number_font_record(callback: CallbackQuery, source, dialog_manager: DialogManager, radio_id, **kwargs) -> None:
    dialog_manager.dialog_data['team_number_font_color_italic'] = radio_id[0]
    await update_team(team_id=dialog_manager.dialog_data['team_id'], number_font=dialog_manager.dialog_data['team_number_font_font'], number_color=dialog_manager.dialog_data['team_number_font_color_input'], number_italic=int(dialog_manager.dialog_data['team_number_font_color_italic']))
    await callback.answer('Настройки номера успешно записаны', show_alert=True)
    await dialog_manager.switch_to(AdminSG.edit_team_menu)


async def change_team_members(callback: CallbackQuery, button: Button, dialog_manager: DialogManager, **kwargs):
    await dialog_manager.switch_to(AdminSG.team_members)

async def team_members(dialog_manager: DialogManager, **kwargs):
    return {'team_members': await get_team_members(dialog_manager.dialog_data['team_id'])}

async def selected_team_member(callback: CallbackQuery, button: Button, dialog_manager: DialogManager, member:str):
    dialog_manager.dialog_data['team_place_member'] = member.split('^')[-1]
    await dialog_manager.switch_to(AdminSG.team_members_menu)

async def delite_team_members(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await update_or_remove_team_member(int(dialog_manager.dialog_data['team_id']), dialog_manager.dialog_data['team_place_member'])
    await dialog_manager.switch_to(AdminSG.team_members)

async def replace_team_member(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(AdminSG.enter_team_member)

async def enter_team_member(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    res = await get_users_by_name(text)
    if res:
        dialog_manager.dialog_data['found_users'] = res
        await dialog_manager.switch_to(AdminSG.found_user_for_member)
    else:
        await message.answer(text=f'Я никого не нашел, введите другое имя.')
        await dialog_manager.switch_to(AdminSG.enter_team_member)

async def member_selected(callback: CallbackQuery, widget: Select,
                        dialog_manager: DialogManager, user_id: str):
    await update_or_remove_team_member(int(dialog_manager.dialog_data['team_id']), dialog_manager.dialog_data['team_place_member'], int(user_id))
    await dialog_manager.switch_to(AdminSG.team_members)


async def change_team_name(callback: CallbackQuery, button: Button, dialog_manager: DialogManager, **kwargs):
    await dialog_manager.switch_to(AdminSG.enter_team_member)

async def new_team(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str) -> None:
    await create_team_only_name(text)
    await message.answer(f'Команда {text} создан')
    await dialog_manager.switch_to(AdminSG.team_management)

async def new_team_name(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str) -> None:
    dialog_manager.dialog_data['team_name'] = text
    await update_team(team_id=dialog_manager.dialog_data['team_id'],
                      name=text)
    await message.answer(f'Название команды изменено на {text}')
    await dialog_manager.switch_to(AdminSG.edit_team_menu)

async def change_team_logo(callback: CallbackQuery, button: Button, dialog_manager: DialogManager, **kwargs):
    await dialog_manager.switch_to(AdminSG.change_team_logo)

async def team_logo_receive(message: Message, widget: MessageInput, dialog_manager: DialogManager, **kwargs):
    photo = message.photo[-1]  # Получаем наибольшее качество
    file_id = photo.file_id
    # Получаем файл
    file = await dialog_manager.middleware_data['bot'].get_file(file_id)
    # Загружаем файл
    photo_data = await dialog_manager.middleware_data['bot'].download_file(file.file_path)
    file_name = '_'.join(dialog_manager.dialog_data['team_name'].replace("'",'').split()) + '.png'
    await update_team(team_id=dialog_manager.dialog_data['team_id'],
                      logo=file_name)
    with open(os.path.join('logos', file_name), 'wb') as new_file:
        new_file.write(photo_data.getvalue())
    await message.reply("Логотип команды сохранён")
    await dialog_manager.switch_to(AdminSG.edit_team_menu)

async def change_team_name_color(callback: CallbackQuery, button: Button, dialog_manager: DialogManager, **kwargs):
    await dialog_manager.switch_to(AdminSG.change_team_font_color)

async def team_font_color(callback: CallbackQuery, source, dialog_manager: DialogManager, radio_id, **kwargs) -> None:
    dialog_manager.dialog_data['team_font_color'] = radio_id
    await dialog_manager.switch_to(AdminSG.change_team_background_color)

async def team_background_color(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str) -> None:
    await update_team(team_id=dialog_manager.dialog_data['team_id'], background_color=text, text_color=dialog_manager.dialog_data['team_font_color'])
    await message.answer('Настройки цветов успешно записаны', show_alert=True)
    await dialog_manager.switch_to(AdminSG.edit_team_menu)



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

async def receive_data(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    return dialog_manager



async def button_calculate(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    gp = get_actual_gp()
    if check_res(gp):
        await callback.message.answer(f'Вы уже сделали расчет для этого GP')
    else:
        output = await process_calculation_command(await calculation_drivers(gp))
        await callback.message.answer_document(
            document=BufferedInputFile(output.read(), filename='gp_results.xlsx')
        )
        output.close()  # Закрываем объект после использования

    await dialog_manager.switch_to(AdminSG.stage)


async def loading_f1_results(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(AdminSG.loading_f1_results)

async def button_f1_sprint(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(AdminSG.loading_f1_result_sprint)

async def loading_f1_result_sprint(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    await update_grandprix_result(grandprix_id=get_actual_gp(), result_type='sprint', result_text=text)
    await message.answer('Результат Спринта записан')
    await dialog_manager.switch_to(AdminSG.loading_f1_results)

async def button_f1_quali(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(AdminSG.loading_f1_result_quali)

async def loading_f1_result_quali(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    await update_grandprix_result(grandprix_id=get_actual_gp(), result_type='qualifying', result_text=text)
    await message.answer('Результат Квалификации записан')
    await dialog_manager.switch_to(AdminSG.loading_f1_results)

async def button_f1_race(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(AdminSG.loading_f1_result_race)

async def loading_f1_result_race(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    await update_grandprix_result(grandprix_id=get_actual_gp(), result_type='race', result_text=text)
    await message.answer('Результат Гонки записан')
    await dialog_manager.switch_to(AdminSG.loading_f1_results)

async def button_clear_result(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    clear_results(get_actual_gp())
    await callback.message.answer('Результат удалён')
    await dialog_manager.switch_to(AdminSG.stage)

async def replace_driver(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(AdminSG.f1_drivers_active)

async def f1_drivers_active(**kwargs):
    return {'f1_drivers_active': await select_drivers_async(active=True)}

async def f1_teams_active(**kwargs):
    teams = {i.driver_team for i in await select_drivers_async(active=True)}
    return {'f1_teams_active': teams}

async def f1_driver_active_selected(callback: CallbackQuery, widget: Select,
                        dialog_manager: DialogManager, item: str):
    dialog_manager.dialog_data['f1_drivers_active_to_replace'] = item
    await dialog_manager.switch_to(AdminSG.f1_drivers_deactivated)


async def f1_drivers_deactivated_selected(callback: CallbackQuery, widget: Select,
                        dialog_manager: DialogManager, item: str):
    await update_driver_nextgp(dialog_manager.dialog_data['f1_drivers_active_to_replace'], item)
    await dialog_manager.switch_to(AdminSG.f1_drivers_menu)

async def f1_driver_deactivated(**kwargs):
    return {'f1_drivers_all': await select_drivers_async(active=False)}

async def f1_drivers_all(**kwargs):
    return {'f1_drivers_all': await select_drivers_async()}


async def add_driver(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(AdminSG.add_f1_driver)

async def add_f1_driver(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    dialog_manager.dialog_data['f1_new_driver'] = text
    await dialog_manager.switch_to(AdminSG.add_f1_driver_team)

async def add_f1_driver_team(callback: CallbackQuery, widget: Select,
                        dialog_manager: DialogManager, item: str):
    await create_f1_driver(dialog_manager.dialog_data['f1_new_driver'], item)
    await callback.message.answer(f'Пилот {dialog_manager.dialog_data['f1_new_driver']} успешно добавлен.')
    await dialog_manager.switch_to(AdminSG.f1_drivers_menu)

async def f1_drivers_all_selected(callback: CallbackQuery, widget: Select,
                        dialog_manager: DialogManager, item: str):
    dialog_manager.dialog_data['f1_driver_name'] = item
    await dialog_manager.switch_to(AdminSG.f1_driver_change_team_teams)

async def f1_driver_change_team_teams(callback: CallbackQuery, widget: Select,
                        dialog_manager: DialogManager, item: str):
    await update_driver_team(dialog_manager.dialog_data['f1_driver_name'], item)
    await callback.message.answer(f'Пилоту {dialog_manager.dialog_data['f1_driver_name']} изменена команда на {item}.')
    await dialog_manager.switch_to(AdminSG.f1_drivers_menu)

async def changing_driver(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(AdminSG.f1_driver_change_team)



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
    await dialog_manager.switch_to(AdminSG.datetime_start)

async def button_start_time_now(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(AdminSG.datetime_penalty)

async def button_start_time_select(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(AdminSG.datetime_start_day)

async def on_date_selected_start(callback: CallbackQuery, widget,
                                   dialog_manager: DialogManager, selected_date: date):
    dialog_manager.dialog_data['start_datetime'] = datetime.combine(selected_date, time.min).strftime(
        '%Y-%m-%d %H:%M:%S')
    await dialog_manager.switch_to(AdminSG.datetime_start_hours)

async def on_date_selected_start_hours(callback: CallbackQuery, widget,
                                         dialog_manager: DialogManager, item_id: int):
    selected_date: datetime = datetime.strptime(dialog_manager.dialog_data['start_datetime'], '%Y-%m-%d %H:%M:%S')
    dialog_manager.dialog_data['start_datetime'] = selected_date.replace(hour=int(item_id)).strftime(
        '%Y-%m-%d %H:%M:%S')
    await dialog_manager.switch_to(AdminSG.datetime_start_minutes)

async def on_date_selected_start_minutes(callback: CallbackQuery, widget,
                                           dialog_manager: DialogManager, item_id: int):
    selected_date: datetime = datetime.strptime(dialog_manager.dialog_data['start_datetime'], '%Y-%m-%d %H:%M:%S')
    dialog_manager.dialog_data['start_datetime'] = selected_date.replace(minute=int(item_id)).strftime(
        '%Y-%m-%d %H:%M:%S')
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
            'end': dialog_manager.dialog_data['end_datetime'],
            'start': dialog_manager.dialog_data.get('start_datetime', datetime.now().replace(second=0).strftime('%Y-%m-%d %H:%M:%S'))
            }


async def button_confirm_predict(callback: CallbackQuery, button: Button, dialog_manager: DialogManager, **kwargs):
    pattern = '%Y-%m-%d %H:%M:%S'
    gp_id = dialog_manager.dialog_data['predict_gp_selected']
    time_start = dialog_manager.dialog_data.get('start_datetime', datetime.now().replace(second=0).strftime('%Y-%m-%d %H:%M:%S'))
    time_penalty = dialog_manager.dialog_data['penalty_datetime']
    time_end = dialog_manager.dialog_data['end_datetime']
    await update_grandprix(gp_id=gp_id, time_start=datetime.strptime(time_start, pattern), time_penalty=datetime.strptime(time_penalty, pattern),
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

async def button_team_management(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(AdminSG.team_management)

async def button_f1_drivers(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(AdminSG.f1_drivers_menu)

async def button_menu(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
    await dialog_manager.switch_to(AdminSG.start)


async def button_exit(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await callback.message.answer('Вы, вышли из админки!')
    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
    await dialog_manager.done()

def name_check(text: str) -> str:
    if all(char in ascii_letters + ' ' for char in text) and text.count(' ') == 1:
        return text
    raise ValueError


async def error_fill_form_name(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, error: ValueError):
    await message.answer(text='В имени могут быть только латинские буквы и должен быть только один пробел между именем и фамилией.')

async def fill_form_name(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    name, lastname = text.split()
    await add_user_async(message.from_user.id, name.capitalize(), lastname.upper())
    await message.answer(
        text='Спасибо за регистрацию, теперь Вы можете делать прогнозы.')

    await dialog_manager.switch_to(UserSG.start)



async def user_name(event_from_user: User, all_admins: list, **kwargs):
    user = await get_users_async(event_from_user.id)
    is_admin = False
    if event_from_user.id in all_admins:
        is_admin = True

    if user:
        return {'user_name': user.name, 'unregistered': False, 'registered': True, 'admins': is_admin}
    else:
        return {'user_name': 'Незарегистрированный пользователь', 'unregistered': True, 'admins': is_admin}

async def button_registration(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(UserSG.fill_form_name)

async def button_send_predict(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    dialog_manager.dialog_data.clear()
    actual_gp: int = get_actual_gp()
    end_time = await get_end_grandprix_by_id(actual_gp)
    start_time = await get_start_grandprix_by_id(actual_gp)
    if is_prediced(callback.from_user.id, actual_gp):
        await callback.answer(
            text=f'Вы уже отправили прогноз на {get_name_gp(actual_gp)} GP')
        await dialog_manager.switch_to(UserSG.start, dialog_manager.dialog_data.clear())

    elif datetime.now() > start_time:
        if datetime.now() < end_time:
            penalty_time = await get_penalty_grandprix_by_id(actual_gp)
            await callback.message.answer(
                text=f'Окончание приема прогноза на <b>{get_name_gp(actual_gp)} GP</b> закончится <b>{end_time}</b>\n Без штрафа прогноз можно подать до <b>{penalty_time}</b>')
            dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
            await dialog_manager.switch_to(UserSG.send_predict)
        else:
            await callback.message.answer(
                text=f'В данный момент прогноз на {get_name_gp(actual_gp)} GP не принимается\n Прием прогнозов закончился {end_time}')
            dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
            await dialog_manager.switch_to(UserSG.start, dialog_manager.dialog_data.clear())

async def get_all_teams_predict(**kwargs):
    return {'teams_for_select': sorted({i.driver_team + '  ' + i.engine_short for i in select_drivers()})}

async def get_all_engines_predict(**kwargs):
    return {'engines_for_select': sorted({i.driver_engine + '  ' + i.engine_short for i in select_drivers()})}

async def get_all_drivers_predict(**kwargs):
    return {'drivers_for_select': [i.driver_name + ' (' + i.driver_team + ')' + '  ' + i.engine_short for i in select_drivers()]}

async def get_all_drivers_predict_second(dialog_manager: DialogManager, **kwargs):
    return {'drivers_for_select': [i.driver_name + ' (' + i.driver_team + ')' + '  ' + i.engine_short for i in select_drivers() if
                                                                    i.driver_name not in [*dialog_manager.dialog_data.values()]]}

async def get_all_drivers_predict_third(dialog_manager: DialogManager, **kwargs):
    return {'drivers_for_select': [i.driver_name + ' (' + i.driver_team + ')' + '  ' + i.engine_short for i in select_drivers()[10:] if i.driver_name not in [*dialog_manager.dialog_data.values()]]}

async def get_all_drivers_predict_fourth(dialog_manager: DialogManager, **kwargs):
    return {'drivers_for_select': [i.driver_name + ' (' + i.driver_team + ')' + '  ' + i.engine_short for i in select_drivers()[15:] if i.driver_name not in [*dialog_manager.dialog_data.values()]]}

async def predict_ending(dialog_manager: DialogManager, **kwargs):
    name_gp = get_name_gp(get_actual_gp())
    driver_team = dialog_manager.dialog_data['selected_team']
    driver_engine = dialog_manager.dialog_data['selected_engine']
    first_driver = dialog_manager.dialog_data['first_driver']
    second_driver = dialog_manager.dialog_data['second_driver']
    third_driver = dialog_manager.dialog_data['third_driver']
    fourth_driver = dialog_manager.dialog_data['fourth_driver']
    gap = dialog_manager.dialog_data['gap']
    lapped = dialog_manager.dialog_data['laps']
    return {'name_gp': name_gp, 'driver_team': driver_team, 'driver_engine': driver_engine, 'first_driver': first_driver, 'second_driver': second_driver, 'third_driver': third_driver, 'fourth_driver': fourth_driver, 'gap': gap, 'lapped': lapped}


async def select_team(callback: CallbackQuery, button: Button, dialog_manager: DialogManager, item: str):
    dialog_manager.dialog_data['selected_team'] = item.rsplit(' ', 1)[0].strip()
    dialog_manager.dialog_data['select1_engine'] = item.split()[-1].strip()
    await dialog_manager.switch_to(UserSG.send_predict_engine)

def is_correct_number(text: str) -> str:
    if all(ch.isdigit() for ch in text) and 0 <= int(text):
        return text
    raise ValueError

async def select_engine(callback: CallbackQuery, button: Button, dialog_manager: DialogManager, item: str):
    dialog_manager.dialog_data['selected_engine'] = item.rsplit(' ', 1)[0].strip()
    dialog_manager.dialog_data['select2_engine'] = item.split()[-1].strip()
    await dialog_manager.switch_to(UserSG.send_predict_first)

async def select_first_driver(callback: CallbackQuery, button: Button, dialog_manager: DialogManager, item: str):
    dialog_manager.dialog_data['first_driver'] = item.split('(')[0].strip()
    dialog_manager.dialog_data['select3_engine'] = item.split()[-1].strip()
    await dialog_manager.switch_to(UserSG.send_predict_second)

async def select_second_driver(callback: CallbackQuery, button: Button, dialog_manager: DialogManager, item: str):
    dialog_manager.dialog_data['second_driver'] = item.split('(')[0].strip()
    dialog_manager.dialog_data['select4_engine'] = item.split()[-1].strip()
    if all(engine == dialog_manager.dialog_data['select1_engine'] for engine in
           [dialog_manager.dialog_data['select2_engine'], dialog_manager.dialog_data['select3_engine'], dialog_manager.dialog_data['select4_engine']]):
        await callback.message.answer('В вашем выборе 4 одинаковых двигателя!\nВыберите другого гонщика или вернитесь назад, чтобы изменить выбор на прошлых шагах')
        dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
        await dialog_manager.switch_to(UserSG.send_predict_second)
    else:
        await dialog_manager.switch_to(UserSG.send_predict_third)

async def select_third_driver(callback: CallbackQuery, button: Button, dialog_manager: DialogManager, item: str):
    dialog_manager.dialog_data['third_driver'] = item.split('(')[0].strip()
    dialog_manager.dialog_data['select5_engine'] = item.split()[-1].strip()
    values = [dialog_manager.dialog_data['select1_engine'], dialog_manager.dialog_data['select2_engine'], dialog_manager.dialog_data['select3_engine'],
              dialog_manager.dialog_data['select4_engine'], dialog_manager.dialog_data['select5_engine']]
    if any(values.count(x) == 4 for x in set(values)):
        await callback.message.answer('В вашем выборе 4 одинаковых двигателя!\nВыберите другого гонщика или вернитесь назад, чтобы изменить выбор на прошлых шагах')
        dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
        await dialog_manager.switch_to(UserSG.send_predict_third)
    else:
        await dialog_manager.switch_to(UserSG.send_predict_fourth)

async def select_fourth_driver(callback: CallbackQuery, button: Button, dialog_manager: DialogManager, item: str):
    dialog_manager.dialog_data['fourth_driver'] = item.split('(')[0].strip()
    dialog_manager.dialog_data['select6_engine'] = item.split()[-1].strip()
    values = [dialog_manager.dialog_data['select1_engine'], dialog_manager.dialog_data['select2_engine'], dialog_manager.dialog_data['select3_engine'],
              dialog_manager.dialog_data['select4_engine'], dialog_manager.dialog_data['select5_engine'], dialog_manager.dialog_data['select6_engine']]
    if any(values.count(x) == 4 for x in set(values)):
        await callback.message.answer('В вашем выборе 4 одинаковых двигателя!\nВыберите другого гонщика или вернитесь назад, чтобы изменить выбор на прошлых шагах')
        dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
        await dialog_manager.switch_to(UserSG.send_predict_fourth)
    else:
        await dialog_manager.switch_to(UserSG.send_predict_gap)

async def select_gap(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    dialog_manager.dialog_data['gap'] = int(text)
    await dialog_manager.switch_to(UserSG.send_predict_laps)

async def select_laps(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    dialog_manager.dialog_data['laps'] = int(text)
    await dialog_manager.switch_to(UserSG.send_predict_ending)

async def button_user_confirm_predict(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    gp = get_actual_gp()
    end_time = await get_end_grandprix_by_id(gp)
    if end_time < datetime.now():
        await callback.answer(
            text=f'К сожалению Вы не успели сделать прогноз на {get_name_gp(gp)} GP, окончание приема заявок было до {end_time}')
        dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
        await dialog_manager.switch_to(UserSG.start, dialog_manager.dialog_data.clear())
    else:
        penalty_time = await get_penalty_grandprix_by_id(gp)
        if datetime.now() < penalty_time:
            penalty = None
        else:
            penalty = 30

        driver_team = dialog_manager.dialog_data['selected_team']
        driver_engine = dialog_manager.dialog_data['selected_engine']
        first_driver = dialog_manager.dialog_data['first_driver']
        second_driver = dialog_manager.dialog_data['second_driver']
        third_driver = dialog_manager.dialog_data['third_driver']
        fourth_driver = dialog_manager.dialog_data['fourth_driver']
        gap = dialog_manager.dialog_data['gap']
        lapped = dialog_manager.dialog_data['laps']
        #tg_id, gp, first_driver, second_driver, third_driver, fourth_driver, driver_team, driver_engine, gap,lapped, penalty, time
        send_predict(tg_id=callback.from_user.id, gp=gp, first_driver=first_driver, second_driver=second_driver, third_driver=third_driver, fourth_driver=fourth_driver,driver_team=driver_team,driver_engine=driver_engine, gap=gap, lapped=lapped, penalty=penalty, time=datetime.now())
        await callback.message.answer(f'Спасибо, принято!\nВаш прогноз на <b>{get_name_gp(gp)} GP:</b> \nКоманда: <b>{driver_team}</b>\nДвигатель: <b>{driver_engine}</b>\nПервый пилот: <b>{first_driver}</b>\nВторой пилот: <b>{second_driver}</b>\nТретий пилот: <b>{third_driver}</b>\nЧетвертый пилот: <b>{fourth_driver}</b>\nОтставание от лидера: <b>{gap}</b>\nКоличество круговых: <b>{lapped}</b>')
        dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
        await dialog_manager.switch_to(UserSG.start, dialog_manager.dialog_data.clear())

async def button_user_menu(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
    await dialog_manager.switch_to(UserSG.start, dialog_manager.dialog_data.clear())

async def button_about(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    pass

async def button_exit_user(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await callback.message.answer('Вы, вышли из пользовательского меню!')
    await dialog_manager.done()

async def button_admin(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager
):
    await dialog_manager.start(state=AdminSG.start)

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
            text=Const('Отправить прогноз на ближайший GP'),
            id='button_send_predict',
            on_click=button_send_predict,
            when=F["registered"]
            ),
            Button(
                text=Const('Информация о фэнтези'),
                id='button_about',
                on_click=button_about
            ),
            Button(
            text=Const('Админка'),
            id='button_admin',
            on_click=button_admin,
            when=F['admins']),
        ),
        state=UserSG.start,
        getter=user_name
    ),
    Window(
        Const(text='Пожалуйста, введите ваше имя и фамилию латинским буквами через пробел:'),
        TextInput(
            type_factory=name_check,
            id='fill_form_name',
            on_success=fill_form_name,
            on_error=error_fill_form_name
        ),
        state=UserSG.fill_form_name,
    ),
    Window(
        Const(text='Выберите <b>команду</b>:'),
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
        Const(text='Выберите <b>двигатель</b>:'),
        Group(
            Select(
                Format('{item}'),
                id='selected_engine',
                item_id_getter=lambda x: x,
                items='engines_for_select',
                on_click=select_engine,
            ),
            Back(Const('◀️ Назад'), id='back'),
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
        Const(text='Выберите <b>первого пилота</b>:'),
        Group(
            Select(
                Format('{item}'),
                id='select_first_driver',
                item_id_getter=lambda x: x,
                items='drivers_for_select',
                on_click=select_first_driver,
            ),
            Back(Const('◀️ Назад'), id='back'),
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
        Const(text='Выберите <b>второго пилота</b>:'),
        Group(
            Select(
                Format('{item}'),
                id='select_second_driver',
                item_id_getter=lambda x: x,
                items='drivers_for_select',
                on_click=select_second_driver,
            ),
            Back(Const('◀️ Назад'), id='back'),
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
        Const(text='Выберите <b>третьего пилота</b>:'),
        Group(
            Select(
                Format('{item}'),
                id='select_third_driver',
                item_id_getter=lambda x: x,
                items='drivers_for_select',
                on_click=select_third_driver,
            ),
            Back(Const('◀️ Назад'), id='back'),
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
        Const(text='Выберите <b>четвертого пилота</b>:'),
        Group(
            Select(
                Format('{item}'),
                id='select_fourth_driver',
                item_id_getter=lambda x: x,
                items='drivers_for_select',
                on_click=select_fourth_driver,
            ),
            Back(Const('◀️ Назад'), id='back'),
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
        Const(text='<b>Введите отставание от лидера в секундах (целое число)</b>:'),
        TextInput(
            id='loading_f1_result_sprint',
            type_factory=is_correct_number,
            on_success=select_gap,
        ),
        state=UserSG.send_predict_gap
    ),
    Window(
        Const(text='<b>Введите количество круговых</b>:'),
        TextInput(
            id='loading_f1_result_sprint',
            type_factory=is_correct_number,
            on_success=select_laps,
        ),
        state=UserSG.send_predict_laps
    ),
    Window(
        Format('Ваш прогноз на <b>{name_gp} GP</b>:\nКоманда: <b>{driver_team}</b>\nДвигатель: <b>{driver_engine}</b>\nПервый пилот: <b>{first_driver}</b>\nВторой пилот: <b>{second_driver}</b>\nТретий пилот: <b>{third_driver}</b>\nЧетвертый пилот: <b>{fourth_driver}</b>\nОтставание от лидера: <b>{gap}</b>\nКоличество круговых: <b>{lapped}</b>'),
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
                on_click=loading_f1_results)
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
        Format('Загрузка результатов этапа'),
        Column(
            Button(
                text=Const('Спринт'),
                id='button_f1_sprint',
                on_click=button_f1_sprint
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
        state=AdminSG.loading_f1_results
    ),
    Window(
        Const(text='Введите результат спринта'),
        TextInput(
            id='loading_f1_result_sprint',
            type_factory=str,
            on_success=loading_f1_result_sprint,
        ),
        state=AdminSG.loading_f1_result_sprint,
    ),
    Window(
        Const(text='Введите результат квалификации'),
        TextInput(
            id='loading_f1_result_quali',
            type_factory=str,
            on_success=loading_f1_result_quali,
        ),
        state=AdminSG.loading_f1_result_quali,
    ),
    Window(
        Const(text='Введите результат гонки'),
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
                text=Const('Вернуться в главное меню'),
                id='button_menu',
                on_click=button_menu)
            ),
        state=AdminSG.edit_team_menu,
        getter=getter_team_name
    ),
    Window(
        Const(text='Введите название шрифта номера'),
        TextInput(
            id='team_number_font_input',
            type_factory=str,
            on_success=team_number_font_input,
        ),
        state=AdminSG.change_team_number_font_font,
    ),
    Window(
        Const(text='Введите цвет номера'),
        TextInput(
            id='team_number_font_color_input',
            type_factory=str,
            on_success=team_number_font_color_input,
        ),
        state=AdminSG.change_team_number_font_color,
    ),
    Window(
        Const(text='Номер курсивом или нет'),
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
        TextInput(
            id='team_background_color_input',
            type_factory=str,
            on_success=team_background_color,
        ),
        state=AdminSG.change_team_background_color,
    ),
    Window(
        Const(text='Пришлите мне логотип команды в формате png, размер 140х49'),
        MessageInput(
            func=team_logo_receive,
            content_types=ContentType.PHOTO,
        ),
        state=AdminSG.change_team_logo,
    ),
    Window(
        Const(text='Введите новое название команды'),
        TextInput(
            id='new_team_name',
            type_factory=str,
            on_success=new_team_name,
        ),
        state=AdminSG.change_team_name,
    ),
    Window(
        Const(text='Введите название команды'),
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


user_router: Router = Router()
user_router.include_router(user_dialog)
user_router.include_router(admin_dialog)
setup_dialogs(user_router)


@user_router.message(Command(commands='start'))
async def command_start_process(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(state=UserSG.start, mode=StartMode.RESET_STACK)


