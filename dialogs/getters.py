from datetime import datetime, date, time
import random
import locale
import platform
import asyncio
import os
from aiogram.fsm.state import State, StatesGroup
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput, MessageInput
from aiogram_dialog.widgets.kbd import Button, Select
from aiogram.types import Message, User, CallbackQuery, BufferedInputFile
from asyncpg.pgproto.pgproto import timedelta

from dataprocessing.excel_forms import entry_list, last_stage, process_championship_full, championship_team_full, \
    process_calculation_command, process_all_predicts, process_all_teams, export_places_summary_by_year, export_counts_to_excel, process_championship_by_segment, statistic_team_excel, statistic_team_position_excel, statistic_user_position_excel
from dataprocessing.calculation_gp_drivers import calculation_drivers
from database.database import get_users_async, check_res, \
    clear_results, get_name_gp, get_users_by_name, change_user_name_async, change_user_number_async, get_grandprix_list, \
    update_driver_positions, update_grandprix, get_all_teams, update_team, create_team_only_name, get_team_members, update_or_remove_team_member, select_drivers_async, update_driver_nextgp, create_f1_driver, update_driver_team, update_grandprix_result, is_sprint, get_actual_gp_async, change_user_banned_status, delete_team_from_db, add_scheduled_message, get_users_async_no_team, get_new_users_async, get_users_from_requests, approving_the_request, add_duel, delete_duels_by_gp, get_duel_pair, can_change_name
from .dop_functions import send_message
from scheduler.scheduler import scheduler, schedule_message

class AdminSG(StatesGroup):
    start = State()
    users_menu = State()
    tables = State()
    stage = State()
    input_name = State()
    found_user = State()
    users_request = State()
    users_edit_select = State()
    users_request_answer = State()
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
    delete_team = State()
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
    send_message = State()
    exit_admin = State()
    send_all = State()
    send_no_team = State()
    duel1 = State()
    duel2 = State()
    duel3 = State()
    statistics = State()

current_os = platform.system()

# Устанавливаем локаль на русский язык
if current_os == "Windows":
    locale.setlocale(locale.LC_TIME, 'Russian_Russia')
elif current_os == "Linux":
    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
else:
    raise Exception("Unsupported operating system")

async def sprint(event_from_user: User, **kwargs):
    return {'sprint': await is_sprint(await get_actual_gp_async())}

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

async def send_all(message: Message,widget: ManagedTextInput,dialog_manager: DialogManager,text: str) -> None:
    bot = dialog_manager.middleware_data.get('bot')
    if dialog_manager.dialog_data.get('user_tg_id'):
        await send_message(dialog_manager.dialog_data.get('user_tg_id'), message.html_text, bot)
        await message.answer('Ваше сообщение было отправлено')
    else:
        users = await get_users_async(active=False)
        # Создаем список задач
        tasks = []
        for user in users:
            tasks.append(send_message(user.id_telegram, message.html_text, bot))
            # Если количество задач достигло 25, ждем их завершения
            if len(tasks) == 25:
                await asyncio.gather(*tasks)
                tasks = []  # Сбрасываем список задач
                await asyncio.sleep(1)  # Пауза в 1 секунду, чтобы не превышать 25 сообщений в секунду
            # Отправляем оставшиеся сообщения, если они есть
        if tasks:
            await asyncio.gather(*tasks)
        await message.answer('Ваше сообщение было отправлено')

    dialog_manager.dialog_data.clear()
    await dialog_manager.switch_to(AdminSG.send_message)

async def send_no_team(message: Message,widget: ManagedTextInput,dialog_manager: DialogManager,text: str) -> None:
    bot = dialog_manager.middleware_data.get('bot')

    users = await get_users_async_no_team()
    # Создаем список задач
    tasks = []
    for user in users:
        tasks.append(send_message(user.id_telegram, message.html_text, bot))
        # Если количество задач достигло 25, ждем их завершения
        if len(tasks) == 25:
            await asyncio.gather(*tasks)
            tasks = []  # Сбрасываем список задач
            await asyncio.sleep(1)  # Пауза в 1 секунду, чтобы не превышать 25 сообщений в секунду
        # Отправляем оставшиеся сообщения, если они есть
    if tasks:
        await asyncio.gather(*tasks)

    dialog_manager.dialog_data.clear()
    await dialog_manager.switch_to(AdminSG.send_message)


async def found_users(dialog_manager: DialogManager, **kwargs):
    return {'found_user': dialog_manager.dialog_data['found_users']}

async def users_request(dialog_manager: DialogManager, **kwargs):
    return {'users_request': dialog_manager.dialog_data['users_request']}


async def user_selected(callback: CallbackQuery, widget: Select,
                        dialog_manager: DialogManager, user_tg_id: str):
    dialog_manager.dialog_data['user_tg_id'] = user_tg_id
    await dialog_manager.switch_to(AdminSG.users_edit_select)

async def user_selected_request(callback: CallbackQuery, widget: Select,
                        dialog_manager: DialogManager, user_tg_id: str):
    dialog_manager.dialog_data['user_tg_id'] = user_tg_id
    await dialog_manager.switch_to(AdminSG.users_request_answer)


async def button_change_user_name(callback: CallbackQuery, button: Button,
                                  dialog_manager: DialogManager):
    await dialog_manager.switch_to(AdminSG.new_name_user)


async def button_change_user_number(callback: CallbackQuery, button: Button,
                                    dialog_manager: DialogManager):
    await dialog_manager.switch_to(AdminSG.new_number_user)

async def button_delite_user_number(callback: CallbackQuery, button: Button,
                                    dialog_manager: DialogManager):
    await change_user_number_async(int(dialog_manager.dialog_data['user_tg_id']), None)
    await callback.answer(f'Вы удалили номер')
    await dialog_manager.switch_to(AdminSG.users_menu)

async def button_ban_user(callback: CallbackQuery, button: Button,
                                    dialog_manager: DialogManager):
    await change_user_banned_status(int(dialog_manager.dialog_data['user_tg_id']), True)
    await callback.message.answer(f'Вы забанили пользователя')
    await dialog_manager.switch_to(AdminSG.users_menu)

async def button_unban_user(callback: CallbackQuery, button: Button,
                                    dialog_manager: DialogManager):
    await change_user_banned_status(int(dialog_manager.dialog_data['user_tg_id']), False)
    await callback.message.answer(f'Вы разбанили пользователя')
    await dialog_manager.switch_to(AdminSG.users_menu)

async def approve_the_request(callback: CallbackQuery, button: Button,
                                    dialog_manager: DialogManager):
    bot = dialog_manager.middleware_data.get('bot')
    await can_change_name(int(dialog_manager.dialog_data['user_tg_id']), False)
    await approving_the_request(int(dialog_manager.dialog_data['user_tg_id']), True)
    await send_message(int(dialog_manager.dialog_data['user_tg_id']), 'Ваша заявка на участи в Fantasy одобрена', bot)
    await callback.message.answer(f'Вы одобрили заявку пользователя')
    await dialog_manager.switch_to(AdminSG.users_menu)

async def button_decline_the_request(callback: CallbackQuery, button: Button,
                                    dialog_manager: DialogManager):
    bot = dialog_manager.middleware_data.get('bot')
    await can_change_name(int(dialog_manager.dialog_data['user_tg_id']), True)
    await approving_the_request(int(dialog_manager.dialog_data['user_tg_id']), False)
    await send_message(int(dialog_manager.dialog_data['user_tg_id']), 'Ваша заявка на участи в Fantasy отклонена (некорректное имя), измените имя на корректное и повторно отправьте заявку.\nОбновите меню командой /start', bot)
    await callback.message.answer(f'Вы отклонили заявку пользователя')
    await dialog_manager.switch_to(AdminSG.users_menu)


async def new_name_user(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str) -> None:
    name, lastname = text.split()
    await change_user_name_async(int(dialog_manager.dialog_data['user_tg_id']), name.capitalize() + ' ' + lastname.upper())
    await message.answer(f'Вы изменили имя на {name.capitalize() + ' ' + lastname.upper()}')
    dialog_manager.dialog_data.clear()
    await dialog_manager.switch_to(AdminSG.users_menu)


async def new_number_user(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str) -> None:
    await change_user_number_async(int(dialog_manager.dialog_data['user_tg_id']), int(text))
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

async def button_new_users(callback: CallbackQuery, button: Button, dialog_manager: DialogManager) -> None:
    res = await get_new_users_async()
    if res:
        dialog_manager.dialog_data['found_users'] = res
        await dialog_manager.switch_to(AdminSG.found_user)

async def button_new_requests(callback: CallbackQuery, button: Button, dialog_manager: DialogManager) -> None:
    res = await get_users_from_requests()
    if res:
        dialog_manager.dialog_data['users_request'] = res
        await dialog_manager.switch_to(AdminSG.users_request)

async def button_edit_team(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(AdminSG.edit_team)

async def cancel_team_edit(callback: CallbackQuery, button: Button, dialog_manager: DialogManager, **kwargs):
    await dialog_manager.switch_to(AdminSG.edit_team_menu)

async def cancel_team(callback: CallbackQuery, button: Button, dialog_manager: DialogManager, **kwargs):
    await dialog_manager.switch_to(AdminSG.team_management)

async def cancel_f1_driver(callback: CallbackQuery, button: Button, dialog_manager: DialogManager, **kwargs):
    await dialog_manager.switch_to(AdminSG.f1_drivers_menu)

async def cancel_user_menu(callback: CallbackQuery, button: Button, dialog_manager: DialogManager, **kwargs):
    await dialog_manager.switch_to(AdminSG.users_menu)

async def cancel_loading_f1_results(callback: CallbackQuery, button: Button, dialog_manager: DialogManager, **kwargs):
    await dialog_manager.switch_to(AdminSG.loading_f1_results)

async def cancel_open_predict(callback: CallbackQuery, button: Button, dialog_manager: DialogManager, **kwargs):
    await dialog_manager.switch_to(AdminSG.start)

async def cancel_send_message(callback: CallbackQuery, button: Button, dialog_manager: DialogManager, **kwargs):
    await dialog_manager.switch_to(AdminSG.send_message)

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
    dialog_manager.dialog_data['team_number_font_color_input'] = text.strip('#')
    await dialog_manager.switch_to(AdminSG.change_team_number_font_italic)

async def change_team_number_font_record(callback: CallbackQuery, source, dialog_manager: DialogManager, radio_id, **kwargs) -> None:
    dialog_manager.dialog_data['team_number_font_color_italic'] = radio_id[0]
    await update_team(team_id=int(dialog_manager.dialog_data['team_id']), number_font=dialog_manager.dialog_data['team_number_font_font'], number_color=dialog_manager.dialog_data['team_number_font_color_input'], number_italic=int(dialog_manager.dialog_data['team_number_font_color_italic']))
    await callback.answer('Настройки номера успешно записаны', show_alert=True)
    await dialog_manager.switch_to(AdminSG.edit_team_menu)


async def change_team_members(callback: CallbackQuery, button: Button, dialog_manager: DialogManager, **kwargs):
    await dialog_manager.switch_to(AdminSG.team_members)

async def team_members(dialog_manager: DialogManager, **kwargs):
    return {'team_members': await get_team_members(int(dialog_manager.dialog_data['team_id']))}

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
    await dialog_manager.switch_to(AdminSG.change_team_name)


async def delete_team(callback: CallbackQuery, button: Button, dialog_manager: DialogManager, **kwargs):
    await dialog_manager.switch_to(AdminSG.delete_team)

def is_yes(text: str) -> str:
    if text == 'ДА':
        return text
    raise ValueError

async def delete_team_not_confirmed(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, error: ValueError):
    await dialog_manager.switch_to(AdminSG.team_management)

async def delete_team_confirmation(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    await delete_team_from_db(int(dialog_manager.dialog_data['team_id']))
    await message.answer(f'Команда {dialog_manager.dialog_data['team_name']} удалена')
    await dialog_manager.switch_to(AdminSG.team_management)

async def new_team(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str) -> None:
    await create_team_only_name(text)
    await message.answer(f'Команда {text} создана')
    await dialog_manager.switch_to(AdminSG.team_management)

async def new_team_name(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str) -> None:
    dialog_manager.dialog_data['team_name'] = text
    await update_team(team_id=int(dialog_manager.dialog_data['team_id']),
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
    await update_team(team_id=int(dialog_manager.dialog_data['team_id']),
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
    await update_team(team_id=int(dialog_manager.dialog_data['team_id']), background_color=text.strip('#'), text_color=dialog_manager.dialog_data['team_font_color'])
    await message.answer('Настройки цветов успешно записаны', show_alert=True)
    await dialog_manager.switch_to(AdminSG.edit_team_menu)



async def button_last_stage(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    output = await last_stage()  # Получаем объект файла
    await callback.message.answer_document(
        document=BufferedInputFile(output.read(), filename=f'results {await get_name_gp(await get_actual_gp_async())}.xlsx')
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


async def button_get_all_predict(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    output = await process_all_predicts()  # Получаем объект файла
    await callback.message.answer_document(
        document=BufferedInputFile(output.read(), filename=f'predicts_for_{await get_name_gp(await get_actual_gp_async())}.xlsx')
    )
    output.close()  # Закрываем объект после использования
    await dialog_manager.switch_to(AdminSG.stage)


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
    gp = await get_actual_gp_async()
    if await check_res(gp):
        await callback.message.answer(f'Вы уже сделали расчет для этого GP')
    else:
        output = await process_calculation_command(await calculation_drivers(gp))
        await callback.message.answer_document(
            document=BufferedInputFile(output.read(), filename=f'gp_results_{await get_name_gp(gp)}.xlsx')
        )
        output.close()  # Закрываем объект после использования

    await dialog_manager.switch_to(AdminSG.stage)

async def button_get_all_teams(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    output = await process_all_teams()
    await callback.message.answer_document(
        document=BufferedInputFile(output.read(), filename='team_list.xlsx')
    )
    output.close()  # Закрываем объект после использования
    await dialog_manager.switch_to(AdminSG.team_management)

async def statistic_users(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    output = await export_places_summary_by_year()
    await callback.message.answer_document(
        document=BufferedInputFile(output.read(), filename='statistic_users.xlsx')
    )
    output.close()  # Закрываем объект после использования
    await dialog_manager.switch_to(AdminSG.statistics)

async def statistic_select(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    output = await export_counts_to_excel()
    await callback.message.answer_document(
        document=BufferedInputFile(output.read(), filename='statistic_select.xlsx')
    )
    output.close()  # Закрываем объект после использования
    await dialog_manager.switch_to(AdminSG.statistics)

async def statistic_points_by_segment(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    output = await process_championship_by_segment()
    await callback.message.answer_document(
        document=BufferedInputFile(output.read(), filename='statistic_points_by_segment.xlsx')
    )
    output.close()  # Закрываем объект после использования
    await dialog_manager.switch_to(AdminSG.statistics)

async def statistic_team(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    output = await statistic_team_excel()
    await callback.message.answer_document(
        document=BufferedInputFile(output.read(), filename='statistic_team.xlsx')
    )
    output.close()  # Закрываем объект после использования
    await dialog_manager.switch_to(AdminSG.statistics)

async def statistic_team_position(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    output = await statistic_team_position_excel()
    await callback.message.answer_document(
        document=BufferedInputFile(output.read(), filename='statistic_team_position.xlsx')
    )
    output.close()  # Закрываем объект после использования
    await dialog_manager.switch_to(AdminSG.statistics)

async def statistic_user_position(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    output = await statistic_user_position_excel()
    await callback.message.answer_document(
        document=BufferedInputFile(output.read(), filename='statistic_user_position.xlsx')
    )
    output.close()  # Закрываем объект после использования
    await dialog_manager.switch_to(AdminSG.statistics)


async def loading_f1_results(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(AdminSG.loading_f1_results)

async def button_f1_sprint(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(AdminSG.loading_f1_result_sprint)

async def loading_f1_result_sprint(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    res = await update_grandprix_result(grandprix_id= await get_actual_gp_async(), result_type='sprint', result_text=text)
    if res == 'OK':
        await message.answer('Результат Спринта записан')
        await dialog_manager.switch_to(AdminSG.loading_f1_results)
    else:
        await message.answer(res)
        await dialog_manager.switch_to(AdminSG.loading_f1_results)


async def button_f1_quali(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(AdminSG.loading_f1_result_quali)

async def loading_f1_result_quali(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    res = await update_grandprix_result(grandprix_id=await get_actual_gp_async(), result_type='qualifying', result_text=text)
    if res == 'OK':
        await message.answer('Результат Квалификации записан')
        await dialog_manager.switch_to(AdminSG.loading_f1_results)
    else:
        await message.answer(res)
        await dialog_manager.switch_to(AdminSG.loading_f1_results)

async def button_f1_race(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(AdminSG.loading_f1_result_race)

async def loading_f1_result_race(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    res = await update_grandprix_result(grandprix_id=await get_actual_gp_async(), result_type='race', result_text=text)
    if res == 'OK':
        await message.answer('Результат Гонки записан')
        await dialog_manager.switch_to(AdminSG.loading_f1_results)
    else:
        await message.answer(res)
        await dialog_manager.switch_to(AdminSG.loading_f1_results)

async def button_clear_result(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await clear_results(await get_actual_gp_async())
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
    return {'f1_driver_deactivated': await select_drivers_async(active=False)}

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

async def get_duelists1(dialog_manager: DialogManager, **kwargs):
    duelists = [i.driver_name for i in await select_drivers_async(active=True)][1:5]
    duelists_pairs = [(name, name) for name in duelists]
    return {'duelists': duelists_pairs}

async def confirm_duel1(callback: CallbackQuery, button: Button, dialog_manager: DialogManager, **kwargs):
    widget = dialog_manager.find('duel1')
    pair = widget.get_checked()
    await add_duel(pair[0], pair[1], 1,dialog_manager.dialog_data.get('predict_gp_selected'))
    await dialog_manager.switch_to(AdminSG.duel2)

async def random_duel1(callback: CallbackQuery, button: Button, dialog_manager: DialogManager, **kwargs):
    duelists1 = [i.driver_name for i in await select_drivers_async(active=True)][1:5]
    pair = random.sample(duelists1, 2)
    await add_duel(pair[0], pair[1], 1,dialog_manager.dialog_data.get('predict_gp_selected'))
    await dialog_manager.switch_to(AdminSG.duel2)


async def get_duelists2(dialog_manager: DialogManager, **kwargs):
    duelists = [i.driver_name for i in await select_drivers_async(active=True)][8:12]
    duelists_pairs = [(name, name) for name in duelists]
    return {'duelists': duelists_pairs}

async def confirm_duel2(callback: CallbackQuery, button: Button, dialog_manager: DialogManager, **kwargs):
    widget = dialog_manager.find('duel2')
    pair = widget.get_checked()
    await add_duel(pair[0], pair[1], 2,dialog_manager.dialog_data.get('predict_gp_selected'))
    await dialog_manager.switch_to(AdminSG.duel3)

async def random_duel2(callback: CallbackQuery, button: Button, dialog_manager: DialogManager, **kwargs):
    duelists1 = [i.driver_name for i in await select_drivers_async(active=True)][8:12]
    pair = random.sample(duelists1, 2)
    await add_duel(pair[0], pair[1], 2,dialog_manager.dialog_data.get('predict_gp_selected'))
    await dialog_manager.switch_to(AdminSG.duel3)

async def get_duelists3(dialog_manager: DialogManager, **kwargs):
    duelists = [i.driver_name for i in await select_drivers_async(active=True)][15:19]
    duelists_pairs = [(name, name) for name in duelists]
    return {'duelists': duelists_pairs}

async def confirm_duel3(callback: CallbackQuery, button: Button, dialog_manager: DialogManager, **kwargs):
    widget = dialog_manager.find('duel3')
    pair = widget.get_checked()
    await add_duel(pair[0], pair[1], 3,dialog_manager.dialog_data.get('predict_gp_selected'))
    await dialog_manager.switch_to(AdminSG.datetime_start)

async def random_duel3(callback: CallbackQuery, button: Button, dialog_manager: DialogManager, **kwargs):
    duelists1 = [i.driver_name for i in await select_drivers_async(active=True)][15:19]
    pair = random.sample(duelists1, 2)
    await add_duel(pair[0], pair[1], 3,dialog_manager.dialog_data.get('predict_gp_selected'))
    await dialog_manager.switch_to(AdminSG.datetime_start)

async def predict_gp_selected(callback: CallbackQuery, widget: Select,
                              dialog_manager: DialogManager, item_id: str):
    dialog_manager.dialog_data.clear()
    dialog_manager.dialog_data['predict_gp_selected'] = int(item_id)
    await delete_duels_by_gp(int(item_id))
    await dialog_manager.switch_to(AdminSG.update_drivers_standing)


async def update_drivers_standing(
        message: Message,
        widget: ManagedTextInput,
        dialog_manager: DialogManager,
        text: str) -> None:
    answer = await update_driver_positions(text)
    if answer == 'OK':
        await dialog_manager.switch_to(AdminSG.duel1)
    else:
        await  message.answer(answer)
        await dialog_manager.switch_to(AdminSG.start)




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
    return {'GP': await get_name_gp(dialog_manager.dialog_data['predict_gp_selected']),
            'penalty': dialog_manager.dialog_data['penalty_datetime'],
            'end': dialog_manager.dialog_data['end_datetime'],
            'start': dialog_manager.dialog_data.get('start_datetime', datetime.now().replace(second=0).strftime('%Y-%m-%d %H:%M:%S'))
            }




def get_day_of_week(day_number, case):
    days = {
        "именительный": ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"],
        "родительный": ["понедельника", "вторника", "среды", "четверга", "пятницы", "субботы", "воскресенья"],
        "дательный": ["понедельнику", "вторнику", "среде", "четвергу", "пятнице", "субботе", "воскресенью"],
        "винительный": ["понедельник", "вторник", "среду", "четверг", "пятницу", "субботу", "воскресенье"],
        "творительный": ["понедельником", "вторником", "средой", "четвергом", "пятницей", "субботой", "воскресеньем"],
        "предложный": ["о понедельнике", "о вторнике", "о среде", "о четверге", "о пятнице", "о субботе",
                       "о воскресенье"]
    }
    return days[case][day_number]

def get_preposition(day_name):
    # Проверяем, начинается ли день недели на "вт" (вторник)
    if day_name.startswith('вт'):
        return 'во'
    return 'в'


async def button_confirm_predict(callback: CallbackQuery, button: Button, dialog_manager: DialogManager, **kwargs):

    pattern = '%Y-%m-%d %H:%M:%S'
    gp_id = dialog_manager.dialog_data['predict_gp_selected']
    time_start = dialog_manager.dialog_data.get('start_datetime', datetime.now().replace(second=0).strftime('%Y-%m-%d %H:%M:%S'))
    time_penalty = dialog_manager.dialog_data['penalty_datetime']
    time_end = dialog_manager.dialog_data['end_datetime']
    await update_grandprix(gp_id=gp_id, time_start=datetime.strptime(time_start, pattern), time_penalty=datetime.strptime(time_penalty, pattern),
                           time_end=datetime.strptime(time_end, pattern))
    await callback.message.answer(f'Прогноз на {await get_name_gp(gp_id)} GP создан')

    '''
    # Отправка перенесена в шедулер
    users = await get_users_async()
    # Создаем список задач
    tasks = []
    for user in users:
        tasks.append(send_message(user.id_telegram, text, bot))
        # Если количество задач достигло 25, ждем их завершения
        if len(tasks) == 25:
            await asyncio.gather(*tasks)
            tasks = []  # Сбрасываем список задач
            await asyncio.sleep(1)  # Пауза в 1 секунду, чтобы не превышать 25 сообщений в секунду

    # Отправляем оставшиеся сообщения, если они есть
    if tasks:
        await asyncio.gather(*tasks)
    '''

    # Отправка уведомлений о создании прогноза
    time_start_d = datetime.strptime(time_start, "%Y-%m-%d %H:%M:%S")
    time_penalty_d = datetime.strptime(time_penalty, "%Y-%m-%d %H:%M:%S")
    time_end_d = datetime.strptime(time_end, "%Y-%m-%d %H:%M:%S")
    time_start = datetime.strptime(time_start, "%Y-%m-%d %H:%M:%S").strftime('%Y-%m-%d %H:%M')
    time_penalty = datetime.strptime(time_penalty, "%Y-%m-%d %H:%M:%S").strftime('%Y-%m-%d %H:%M')
    time_end = datetime.strptime(time_end, "%Y-%m-%d %H:%M:%S").strftime('%Y-%m-%d %H:%M')


    bot = dialog_manager.middleware_data.get('bot')
    # Формируем текст с правильными предлогами
    day_open = get_day_of_week(time_start_d.weekday(), "винительный")
    prep_open = get_preposition(day_open)

    day_end = get_day_of_week(time_end_d.weekday(), "винительный")
    prep_end = get_preposition(day_end)


    all_duels = await get_duel_pair(gp_value=gp_id)
    duel1 = f'<b>{all_duels[0][0]}</b> vs <b>{all_duels[0][1]}</b>'
    duel2 = f'<b>{all_duels[1][0]}</b> vs <b>{all_duels[1][1]}</b>'
    duel3 = f'<b>{all_duels[2][0]}</b> vs <b>{all_duels[2][1]}</b>'
    text = f'Привет!\nПриём прогнозов на <b> {await get_name_gp(gp_id)} GP</b>\nоткроется {prep_open} <b>{day_open} {time_start} МСК</b>\nбез штрафа до <b>{get_day_of_week(time_penalty_d.weekday(), "родительный")} {time_penalty} МСК</b>\nокончание приёма {prep_end} <b>{day_end} {time_end} МСК</b>\n<b>Дуэли:</b>\n{duel1}\n{duel2}\n{duel3}'
    await add_scheduled_message(0, text, datetime.now() + timedelta(minutes=1))
    scheduler.add_job(schedule_message, 'date', run_date=(datetime.now() + timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M:%S"), args=[0, text, bot])

    # Уведомление о начале принятия прогноза
    text = f'❗ Приём прогнозов на <b> {await get_name_gp(gp_id)} GP</b> открылся!\nБез штрафа можно подать до <b>{get_day_of_week(time_penalty_d.weekday(), "родительный")} {time_penalty} МСК</b>\nОкончание приёма прогнозов в <b>{get_day_of_week(time_end_d.weekday(), "винительный")} {time_end} МСК</b>\n<b>Дуэли:</b>\n{duel1}\n{duel2}\n{duel3}'
    await add_scheduled_message(0, text, datetime.strptime(time_start, "%Y-%m-%d %H:%M"))
    scheduler.add_job(schedule_message, 'date', run_date=dialog_manager.dialog_data.get('start_datetime'), args=[0, text, bot])

    # Уведомление, что осталось 48 часов до штрафа
    text = f'⏱️ Осталось 48 часов, чтобы подать прогноз на <b> {await get_name_gp(gp_id)} GP</b>\nбез штрафа до <b>{get_day_of_week(time_penalty_d.weekday(), "родительный")} {time_penalty} МСК</b>\nОкончание приёма прогнозов в <b>{get_day_of_week(time_end_d.weekday(), "винительный")} {time_end} МСК</b>'
    await add_scheduled_message(0, text, datetime.strptime(time_penalty, "%Y-%m-%d %H:%M") - timedelta(hours=48))
    scheduler.add_job(schedule_message, 'date',
                      run_date=(datetime.strptime(time_penalty, "%Y-%m-%d %H:%M") - timedelta(hours=48)).strftime(
                          "%Y-%m-%d %H:%M:%S"), args=[0, text, bot])

    # Уведомление, что осталось 24 часа до штрафа
    text = f'⏱️ Осталось 24 часа, чтобы подать прогноз на <b> {await get_name_gp(gp_id)} GP</b>\nбез штрафа до <b>{get_day_of_week(time_penalty_d.weekday(), "родительный")} {time_penalty} МСК</b>\nОкончание приёма прогнозов в <b>{get_day_of_week(time_end_d.weekday(), "винительный")} {time_end} МСК</b>'
    await add_scheduled_message(0, text, datetime.strptime(time_penalty, "%Y-%m-%d %H:%M") - timedelta(hours=24))
    scheduler.add_job(schedule_message, 'date', run_date=(datetime.strptime(time_penalty, "%Y-%m-%d %H:%M") - timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S"), args=[0, text, bot])


    # Уведомление, что осталось 18 часов до штрафа
    text = f'⏱️ Осталось 18 часов, чтобы подать прогноз на <b> {await get_name_gp(gp_id)} GP</b>\nбез штрафа до <b>{get_day_of_week(time_penalty_d.weekday(), "родительный")} {time_penalty} МСК</b>\nОкончание приёма прогнозов в <b>{get_day_of_week(time_end_d.weekday(), "винительный")} {time_end} МСК</b>'
    await add_scheduled_message(0, text, datetime.strptime(time_penalty, "%Y-%m-%d %H:%M") - timedelta(hours=18))
    scheduler.add_job(schedule_message, 'date', run_date=(datetime.strptime(time_penalty, "%Y-%m-%d %H:%M") - timedelta(hours=18)).strftime("%Y-%m-%d %H:%M:%S"), args=[0, text, bot])


    # Уведомление, что осталось 5 часов до штрафа
    text = f'⏱️ Осталось 5 часов, чтобы подать прогноз на <b> {await get_name_gp(gp_id)} GP</b>\nбез штрафа до <b>{get_day_of_week(time_penalty_d.weekday(), "родительный")} {time_penalty} МСК</b>\nОкончание приёма прогнозов в <b>{get_day_of_week(time_end_d.weekday(), "винительный")} {time_end} МСК</b>'
    await add_scheduled_message(0, text, datetime.strptime(time_penalty, "%Y-%m-%d %H:%M") - timedelta(hours=5))
    scheduler.add_job(schedule_message, 'date', run_date=(datetime.strptime(time_penalty, "%Y-%m-%d %H:%M") - timedelta(hours=5)).strftime("%Y-%m-%d %H:%M:%S"), args=[0, text, bot])

    # Уведомление, что осталось 3 часа до штрафа
    text = f'⚠️Осталось 3 часа, чтобы подать прогноз на <b> {await get_name_gp(gp_id)} GP</b>\nбез штрафа до <b>{get_day_of_week(time_penalty_d.weekday(), "родительный")} {time_penalty}МСК</b>\nОкончание приёма прогнозов в <b>{get_day_of_week(time_end_d.weekday(), "винительный")} {time_end} МСК</b>'
    await add_scheduled_message(0, text, datetime.strptime(time_penalty, "%Y-%m-%d %H:%M") - timedelta(hours=3))
    scheduler.add_job(schedule_message, 'date', run_date=(datetime.strptime(time_penalty, "%Y-%m-%d %H:%M") - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S"), args=[0, text, bot])

    # Уведомление, что осталось 2 часа до штрафа
    text = f'⚠️Осталось 2 часа, чтобы подать прогноз на <b> {await get_name_gp(gp_id)} GP</b>\nбез штрафа до <b>{get_day_of_week(time_penalty_d.weekday(), "родительный")} {time_penalty}МСК</b>\nОкончание приёма прогнозов в <b>{get_day_of_week(time_end_d.weekday(), "винительный")} {time_end} МСК</b>'
    await add_scheduled_message(0, text, datetime.strptime(time_penalty, "%Y-%m-%d %H:%M") - timedelta(hours=2))
    scheduler.add_job(schedule_message, 'date', run_date=(datetime.strptime(time_penalty, "%Y-%m-%d %H:%M") - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S"), args=[0, text, bot])

    # Уведомление, что остался 1 час до штрафа
    text = f'‼️ ️Остался 1 час, чтобы подать прогноз на <b> {await get_name_gp(gp_id)} GP</b>\nбез штрафа до <b>{get_day_of_week(time_penalty_d.weekday(), "родительный")} {time_penalty}МСК</b>\nОкончание приёма прогнозов в <b>{get_day_of_week(time_end_d.weekday(), "винительный")} {time_end} МСК</b>'
    await add_scheduled_message(0, text, datetime.strptime(time_penalty, "%Y-%m-%d %H:%M") - timedelta(hours=1))
    scheduler.add_job(schedule_message, 'date',
                      run_date=(datetime.strptime(time_penalty, "%Y-%m-%d %H:%M") - timedelta(hours=1)).strftime(
                          "%Y-%m-%d %H:%M:%S"), args=[0, text, bot])

    # Уведомление, что осталось 4 часа до дедлайна
    text = f'‼️ Осталось 4 часа, чтобы подать прогноз на <b> {await get_name_gp(gp_id)} GP</b>\nОкончание приёма прогнозов в <b>{get_day_of_week(time_end_d.weekday(), "винительный")} {time_end} МСК</b>'
    await add_scheduled_message(0, text, datetime.strptime(time_end, "%Y-%m-%d %H:%M") - timedelta(hours=4))
    scheduler.add_job(schedule_message, 'date',
                      run_date=(datetime.strptime(time_end, "%Y-%m-%d %H:%M") - timedelta(hours=4)).strftime(
                          "%Y-%m-%d %H:%M:%S"), args=[0, text, bot])

    # Уведомление, что осталось 2 часа до дедлайна
    text = f'‼️ Осталось 2 часа, чтобы подать прогноз на <b> {await get_name_gp(gp_id)} GP</b>\nОкончание приёма прогнозов в <b>{get_day_of_week(time_end_d.weekday(), "винительный")} {time_end} МСК</b>'
    await add_scheduled_message(0, text, datetime.strptime(time_end, "%Y-%m-%d %H:%M") - timedelta(hours=2))
    scheduler.add_job(schedule_message, 'date',
                      run_date=(datetime.strptime(time_end, "%Y-%m-%d %H:%M") - timedelta(hours=2)).strftime(
                          "%Y-%m-%d %H:%M:%S"), args=[0, text, bot])

    dialog_manager.dialog_data.clear()
    await dialog_manager.switch_to(AdminSG.start)


async def button_tables(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(AdminSG.tables)

async def button_send_all(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(AdminSG.send_all)

async def button_send_no_team(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(AdminSG.send_no_team)


async def button_stage(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(AdminSG.stage)


async def button_open_predict(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(AdminSG.open_predict)

async def button_team_management(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(AdminSG.team_management)

async def button_f1_drivers(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(AdminSG.f1_drivers_menu)

async def button_send_message(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(AdminSG.send_message)

async def button_statistics(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(AdminSG.statistics)

async def button_menu(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    dialog_manager.dialog_data.clear()
    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
    await dialog_manager.switch_to(AdminSG.start)


async def button_exit(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    dialog_manager.dialog_data.clear()
    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
    #await callback.message.answer('Вы, вышли из админки!')
    await dialog_manager.done()