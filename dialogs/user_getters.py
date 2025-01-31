from datetime import datetime
import platform
import locale
from aiogram.fsm.state import State, StatesGroup
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.input import ManagedTextInput
from aiogram_dialog.widgets.kbd import Button
from aiogram.types import Message, User, CallbackQuery
from string import ascii_letters

from sqlalchemy.util import await_fallback
from .dop_functions import send_message
from .getters import AdminSG
from database.database import send_predict, is_prediced, get_name_gp, \
    get_users_async, add_user_async, get_end_grandprix_by_id, get_start_grandprix_by_id, get_penalty_grandprix_by_id, \
    select_drivers_async, get_actual_gp_async, is_user_banned, get_user_team


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
    about_fantasy = State()
    feedback = State()

current_os = platform.system()

# Устанавливаем локаль на русский язык
if current_os == "Windows":
    locale.setlocale(locale.LC_TIME, 'Russian_Russia')
elif current_os == "Linux":
    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
else:
    raise Exception("Unsupported operating system")




def name_check(text: str) -> str:
    if all(char in ascii_letters + ' ' for char in text) and text.count(' ') == 1:
        return text
    raise ValueError


async def error_fill_form_name(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, error: ValueError):
    await message.answer(text='В имени могут быть только латинские буквы и должен быть только один пробел между именем и фамилией.')

async def error_feedback(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, error: ValueError):
    await message.answer(text='Вы можете отправить только текст')

async def cancel_feedback(callback: CallbackQuery, button: Button, dialog_manager: DialogManager, **kwargs):
    await dialog_manager.switch_to(UserSG.start)

async def fill_form_name(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    name, lastname = text.split()
    await add_user_async(message.from_user.id, name.capitalize(), lastname.upper())
    await message.answer(
        text='Спасибо за регистрацию, теперь Вы можете делать прогнозы.')
    await dialog_manager.switch_to(UserSG.start)

async def feedback(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):

    if await is_user_banned(message.from_user.id):
        await message.answer(
            text=f'Вы забанены в Fantasy, обратитесь к администрации в общем чате')
    else:
        user = await get_users_async(message.from_user.id)
        team = await get_user_team(message.from_user.id)
        text = (f'Сообщение от <b>{user.name}</b> из команды {team}:\n'
                f'{text}')
        bot = dialog_manager.middleware_data.get('bot')
        await send_message(user_id=-1002341617853, text=text, bot=bot)
        await message.answer(text='Спасибо. Ваше сообщение отправлено')
    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
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

async def button_send_predict(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    dialog_manager.dialog_data.clear()
    actual_gp: int = await get_actual_gp_async()
    end_time = await get_end_grandprix_by_id(actual_gp)
    start_time = await get_start_grandprix_by_id(actual_gp)

    if await is_user_banned(callback.from_user.id):
        await callback.answer(
            text=f'Вы забанены в Fantasy, обратитесь к администрации')
        await dialog_manager.switch_to(UserSG.start, dialog_manager.dialog_data.clear())

    elif await is_prediced(callback.from_user.id, actual_gp):
        await callback.answer(
            text=f'Вы уже отправили прогноз на {await get_name_gp(actual_gp)} GP')
        await dialog_manager.switch_to(UserSG.start, dialog_manager.dialog_data.clear())

    elif datetime.now() < start_time:
        await callback.message.answer(
            text=f'В данный момент прогноз на <b>{await get_name_gp(actual_gp)} GP</b> еще не принимается\nПрием прогнозов начнётся в <b>{get_day_of_week(start_time.weekday(), "винительный")} {start_time.strftime("%Y-%m-%d %H:%M")}</b>')
        dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
        await dialog_manager.switch_to(UserSG.start, dialog_manager.dialog_data.clear())


    elif datetime.now() > start_time:
        if datetime.now() < end_time:
            penalty_time = await get_penalty_grandprix_by_id(actual_gp)
            await callback.message.answer(
                text=f'Окончание приема прогноза на <b>{await get_name_gp(actual_gp)} GP</b> закончится в <b>{get_day_of_week(end_time.weekday(), "винительный")} {end_time.strftime("%Y-%m-%d %H:%M")}</b>\n Без штрафа прогноз можно подать до <b>{get_day_of_week(end_time.weekday(), "родительный")} {penalty_time.strftime("%Y-%m-%d %H:%M")}</b>')
            dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
            await dialog_manager.switch_to(UserSG.send_predict)
        else:
            await callback.message.answer(
                text=f'В данный момент прогноз на <b>{await get_name_gp(actual_gp)} GP</b> не принимается\nПрием прогнозов закончился в <b>{get_day_of_week(end_time.weekday(), "винительный")} {end_time.strftime("%Y-%m-%d %H:%M")}</b>')
            dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
            await dialog_manager.switch_to(UserSG.start, dialog_manager.dialog_data.clear())

async def get_all_teams_predict(**kwargs):
    return {'teams_for_select': sorted({i.driver_team + '  ' + i.engine_short for i in await select_drivers_async(active=True)})}

async def get_all_engines_predict(**kwargs):
    return {'engines_for_select': sorted({i.driver_engine + '  ' + i.engine_short for i in await select_drivers_async(active=True)})}

async def get_all_drivers_predict(**kwargs):
    return {'drivers_for_select': [(i.driver_name + ' (' + i.driver_team + ')' + '  ' + i.engine_short, i.driver_name, i.engine_short) for i in await select_drivers_async(active=True)]}

async def get_all_drivers_predict_second(dialog_manager: DialogManager, **kwargs):
    return {'drivers_for_select': [(i.driver_name + ' (' + i.driver_team + ')' + '  ' + i.engine_short, i.driver_name, i.engine_short) for i in await select_drivers_async(active=True) if
                                                                    i.driver_name not in [*dialog_manager.dialog_data.values()]]}

async def get_all_drivers_predict_third(dialog_manager: DialogManager, **kwargs):
    return {'drivers_for_select': [(i.driver_name + ' (' + i.driver_team + ')' + '  ' + i.engine_short, i.driver_name, i.engine_short) for i in await select_drivers_async(start=10, active=True) if i.driver_name not in [*dialog_manager.dialog_data.values()]]}

async def get_all_drivers_predict_fourth(dialog_manager: DialogManager, **kwargs):
    return {'drivers_for_select': [(i.driver_name + ' (' + i.driver_team + ')' + '  ' + i.engine_short, i.driver_name, i.engine_short) for i in await select_drivers_async(start=15, active=True) if i.driver_name not in [*dialog_manager.dialog_data.values()]]}

async def predict_ending(dialog_manager: DialogManager, **kwargs):
    name_gp = await get_name_gp(await get_actual_gp_async())
    driver_team = dialog_manager.dialog_data['selected_team']
    driver_engine = dialog_manager.dialog_data['selected_engine']
    first_driver = dialog_manager.dialog_data['first_driver']
    second_driver = dialog_manager.dialog_data['second_driver']
    third_driver = dialog_manager.dialog_data['third_driver']
    fourth_driver = dialog_manager.dialog_data['fourth_driver']
    gap = int(dialog_manager.dialog_data['gap'])
    lapped = int(dialog_manager.dialog_data['laps'])
    return {'name_gp': name_gp, 'driver_team': driver_team, 'driver_engine': driver_engine, 'first_driver': first_driver, 'second_driver': second_driver, 'third_driver': third_driver, 'fourth_driver': fourth_driver, 'gap': gap, 'lapped': lapped}


async def select_team(callback: CallbackQuery, button: Button, dialog_manager: DialogManager, item: str):
    dialog_manager.dialog_data['selected_team'] = item.rsplit(' ', 1)[0].strip()
    dialog_manager.dialog_data['select1_engine'] = item.split()[-1].strip()
    await dialog_manager.switch_to(UserSG.send_predict_engine)

def is_correct_gap(text: str) -> str:
    if text.isdigit() and 0 <= int(text) <=600:
        return text
    raise ValueError

def is_correct_laps(text: str) -> str:
    if text.isdigit() and 0 <= int(text) < 20:
        return text
    raise ValueError

async def select_engine(callback: CallbackQuery, button: Button, dialog_manager: DialogManager, item: str):
    dialog_manager.dialog_data['selected_engine'] = item.rsplit(' ', 1)[0].strip()
    dialog_manager.dialog_data['select2_engine'] = item.split()[-1].strip()
    await dialog_manager.switch_to(UserSG.send_predict_first)

async def select_first_driver(callback: CallbackQuery, button: Button, dialog_manager: DialogManager, item: str):
    dialog_manager.dialog_data['first_driver'] = item.split(':')[0].strip()
    dialog_manager.dialog_data['select3_engine'] = item.split(':')[-1].strip()
    await dialog_manager.switch_to(UserSG.send_predict_second)

async def select_second_driver(callback: CallbackQuery, button: Button, dialog_manager: DialogManager, item: str):
    dialog_manager.dialog_data['select4_engine'] = item.split(':')[-1].strip()
    if all(engine == dialog_manager.dialog_data['select1_engine'] for engine in
           [dialog_manager.dialog_data['select2_engine'], dialog_manager.dialog_data['select3_engine'], dialog_manager.dialog_data['select4_engine']]):
        await callback.message.answer('В вашем выборе 4 одинаковых двигателя!\nВыберите другого гонщика или вернитесь назад, чтобы изменить выбор на прошлых шагах')
        dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
        await dialog_manager.switch_to(UserSG.send_predict_second)
    else:
        dialog_manager.dialog_data['second_driver'] = item.split(':')[0].strip()
        await dialog_manager.switch_to(UserSG.send_predict_third)

async def select_third_driver(callback: CallbackQuery, button: Button, dialog_manager: DialogManager, item: str):
    dialog_manager.dialog_data['select5_engine'] = item.split(':')[-1].strip()
    values = [dialog_manager.dialog_data['select1_engine'], dialog_manager.dialog_data['select2_engine'], dialog_manager.dialog_data['select3_engine'],
              dialog_manager.dialog_data['select4_engine'], dialog_manager.dialog_data['select5_engine']]
    if any(values.count(x) == 4 for x in set(values)):
        await callback.message.answer('В вашем выборе 4 одинаковых двигателя!\nВыберите другого гонщика или вернитесь назад, чтобы изменить выбор на прошлых шагах')
        dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
        await dialog_manager.switch_to(UserSG.send_predict_third)
    else:
        dialog_manager.dialog_data['third_driver'] = item.split(':')[0].strip()
        await dialog_manager.switch_to(UserSG.send_predict_fourth)

async def select_fourth_driver(callback: CallbackQuery, button: Button, dialog_manager: DialogManager, item: str):
    dialog_manager.dialog_data['select6_engine'] = item.split(':')[-1].strip()
    values = [dialog_manager.dialog_data['select1_engine'], dialog_manager.dialog_data['select2_engine'], dialog_manager.dialog_data['select3_engine'],
              dialog_manager.dialog_data['select4_engine'], dialog_manager.dialog_data['select5_engine'], dialog_manager.dialog_data['select6_engine']]
    if any(values.count(x) == 4 for x in set(values)):
        await callback.message.answer('В вашем выборе 4 одинаковых двигателя!\nВыберите другого гонщика или вернитесь назад, чтобы изменить выбор на прошлых шагах')
        dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
        await dialog_manager.switch_to(UserSG.send_predict_fourth)
    else:
        dialog_manager.dialog_data['fourth_driver'] = item.split(':')[0].strip()
        await dialog_manager.switch_to(UserSG.send_predict_gap)

async def select_gap(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    dialog_manager.dialog_data['gap'] = int(text)
    await dialog_manager.switch_to(UserSG.send_predict_laps)

async def select_laps(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    dialog_manager.dialog_data['laps'] = int(text)
    await dialog_manager.switch_to(UserSG.send_predict_ending)

async def button_user_confirm_predict(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    gp = await get_actual_gp_async()
    end_time = await get_end_grandprix_by_id(gp)
    if end_time < datetime.now():
        await callback.answer(
            text=f'К сожалению Вы не успели сделать прогноз на {await get_name_gp(gp)} GP, окончание приема заявок было до {end_time}')
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
        gap = int(dialog_manager.dialog_data['gap'])
        lapped = int(dialog_manager.dialog_data['laps'])
        #tg_id, gp, first_driver, second_driver, third_driver, fourth_driver, driver_team, driver_engine, gap,lapped, penalty, time
        await send_predict(tg_id=callback.from_user.id, gp=gp, first_driver=first_driver, second_driver=second_driver, third_driver=third_driver, fourth_driver=fourth_driver,driver_team=driver_team,driver_engine=driver_engine, gap=gap, lapped=lapped, penalty=penalty, time=datetime.now())
        await callback.message.answer(f'Спасибо, принято!\nВаш прогноз на <b>{await get_name_gp(gp)} GP:</b> \nКоманда: <b>{driver_team}</b>\nДвигатель: <b>{driver_engine}</b>\nПервый пилот: <b>{first_driver}</b>\nВторой пилот: <b>{second_driver}</b>\nТретий пилот: <b>{third_driver}</b>\nЧетвертый пилот: <b>{fourth_driver}</b>\nОтставание от лидера: <b>{gap}</b>\nКоличество круговых: <b>{lapped}</b>')
        dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
        await dialog_manager.switch_to(UserSG.start, dialog_manager.dialog_data.clear())

async def button_user_menu(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
    await dialog_manager.switch_to(UserSG.start, dialog_manager.dialog_data.clear())

async def button_about(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(UserSG.about_fantasy)

async def button_feedback(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(UserSG.feedback)


async def button_admin(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(state=AdminSG.start)

async def button_exit_user(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await callback.message.answer('Вы, вышли из пользовательского меню!')
    await dialog_manager.done()

