from aiogram import Router, F, Bot, types
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.filters import Command, CommandStart, StateFilter
from lexicon.lexicon_ru import LEXICON_RU
from keyboards.inline_keyboards import create_inline_kb
from database.database import select_drivers, add_user, get_users, send_predict, \
    get_actual_gp, show_points, get_user_team, add_team, get_name_gp, get_end_grandprix_by_id, get_penalty_grandprix_by_id, get_start_grandprix_by_id
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from string import ascii_letters, digits
from datetime import datetime

router: Router = Router()


class FSMFillForm(StatesGroup):
    # Создаем экземпляры класса State, последовательно
    # перечисляя возможные состояния, в которых будет находиться
    # бот в разные моменты взаимодейтсвия с пользователем
    fill_name = State()  # Состояние ожидания ввода имени
    fill_second_name = State()  # Состояние ожидания ввода фамилии
    select_first = State()
    select_second = State()
    select_third = State()
    select_fourth = State()
    select_team = State()
    select_engine = State()
    select_gap = State()
    select_lapped = State()
    end_select = State()
    fill_team_name = State()
    fill_team_number = State()


# Этот хэндлер срабатывает на команду /start
@router.message(CommandStart(), StateFilter(default_state))
async def process_start_command(message: Message):
    await message.answer(text=LEXICON_RU['start_answer'], reply_markup=types.ReplyKeyboardRemove())


# Этот хэндлер будет срабатывать на команду "/cancel" в любых состояниях,
# кроме состояния по умолчанию, и отключать машину состояний
@router.message(Command(commands='cancel'), ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, state: FSMContext):
    await message.answer(
        text='Вы вышли из ввода данных\n\n'
             'Чтобы снова перейти к заполнению -  '
             'отправьте соответствующую команду'
    )
    # Сбрасываем состояние и очищаем данные, полученные внутри состояний
    await state.clear()


url_button_reglament = InlineKeyboardButton(
    text='Ссылка на регламент Fantasy',
    url='https://docs.google.com/document/d/1s-qmH73Ji6zAX7U-M1q4unNKITnjgvIoIp_kPwkxx1Q')

# Создаем объект инлайн-клавиатуры
keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[url_button_reglament]]
)


# Этот хэндлер срабатывает на команду /help
@router.message(Command(commands=['help']))
async def process_help_command(message: Message):
    await message.answer(text=LEXICON_RU['help_answer'], reply_markup=keyboard)

'''
///... ХЭНДЛЕРЫ РЕГИСТРАЦИИ НАЧАЛО ///
'''


# Этот хэндлер будет срабатывать на команду /registration
# и переводить бота в состояние ожидания ввода имени
@router.message(Command(commands='registration'), StateFilter(default_state))
async def process_fillform_command(message: Message, state: FSMContext):
    if not get_users(message.from_user.id):
        await message.answer(text='Пожалуйста, введите ваше имя латинским буквами')
        # Устанавливаем состояние ожидания ввода имени
        await state.set_state(FSMFillForm.fill_name)
    else:
        user = get_users(message.from_user.id)
        await message.answer(text=f'Вы уже зарегистрированы как {user.name}')


# Этот хэндлер будет срабатывать, если введено корректное имя
@router.message(StateFilter(FSMFillForm.fill_name), lambda message: all(char in ascii_letters for char in message.text))
async def process_lastname_sent(message: Message, state: FSMContext):
    # Сохраняем введенное имя в хранилище по ключу "name"
    await state.update_data(name=message.text.capitalize())
    await message.answer(text='Спасибо!\n\nА теперь введите вашу фамилию латинским буквами')
    await state.set_state(FSMFillForm.fill_second_name)


# Этот хэндлер будет срабатывать, если во время ввода имени
# будет введено что-то некорректное
@router.message(StateFilter(FSMFillForm.fill_name))
async def warning_not_name(message: Message):
    await message.answer(
        text='То, что вы отправили не похоже на имя латинским буквами\n\n'
             'Пожалуйста, введите ваше имя\n\n'
             'Если вы хотите прервать заполнение анкеты - '
             'отправьте команду /cancel')


# Этот хэндлер будет срабатывать на ввод фамилии
# записывать данные и выводить из машины состояний
@router.message(StateFilter(FSMFillForm.fill_second_name),
                lambda message: all(char in ascii_letters for char in message.text))
async def process_wish_news_press(message: Message, state: FSMContext):
    # Cохраняем данные о вк
    await state.update_data(lastname=message.text.upper())
    # Добавляем в базу данных анкету пользователя
    # по ключу id пользователя
    user = await state.get_data()
    add_user(message.from_user.id, **user)

    # Завершаем машину состояний
    await state.clear()
    # Отправляем в чат сообщение о сохранении данных
    await message.answer(
        text='Спасибо! Ваши данные сохранены!\n\n'
    )
    # Отправляем в чат сообщение с предложением посмотреть свою анкету
    await message.answer(
        text='Чтобы посмотреть данные вашей '
             'анкеты - отправьте команду /showdata'
    )


# Этот хэндлер будет срабатывать, если во время ввода фамилии
# будет введено что-то некорректное
@router.message(StateFilter(FSMFillForm.fill_second_name))
async def warning_not_name(message: Message):
    await message.answer(
        text='То, что вы отправили не похоже на фамилию латинским буквами\n\n'
             'Пожалуйста, введите вашу фамилию\n\n'
             'Если вы хотите прервать заполнение анкеты - '
             'отправьте команду /cancel')


'''

///... ХЭНДЛЕРЫ РЕГИСТРАЦИИ КОНЕЦ ///

'''

'''

///... ХЭНДЛЕРЫ РЕГИСТРАЦИИ КОМАНДЫ НАЧАЛО ///

'''


# Этот хэндлер будет срабатывать на команду /create_team
@router.message(Command(commands='create_team'), StateFilter(default_state))
async def process_createteam_command(message: Message, state: FSMContext):
    if not get_users(message.from_user.id):
        await message.answer(text='Вы не зарегистрированы, зарегистрируйтесь перед созданием команды.')
    else:
        if get_user_team(message.from_user.id) == 'PERSONAL ENTRY':
            await message.answer(text='Пожалуйста, введите название команды латинским буквами')
            await state.set_state(FSMFillForm.fill_team_name)
        else:
            await message.answer(text=f'Вы уже находитесь в команде <b>{get_user_team(message.from_user.id)}</b>')


# Этот хэндлер будет срабатывать, если введено корректное название
@router.message(StateFilter(FSMFillForm.fill_team_name),
                lambda message: all(char in ascii_letters + digits + "' " for char in message.text))
async def process_lastname_sent(message: Message, state: FSMContext):
    # Сохраняем введенное имя в хранилище по ключу "name"
    await state.update_data(name=message.text)
    await message.answer(text='Спасибо!\nВведите номер гонщика')
    await state.set_state(FSMFillForm.fill_team_number)


# Этот хэндлер будет срабатывать, если во время ввода имени
@router.message(StateFilter(FSMFillForm.fill_team_name))
async def warning_not_name(message: Message):
    await message.answer(
        text='То, что вы отправили не похоже на название команды латинским буквами\n\n'
             'Пожалуйста, введите название команды\n\n'
             'Если вы хотите прервать заполнение анкеты - '
             'отправьте команду /cancel')


@router.message(StateFilter(FSMFillForm.fill_team_number), F.text.isdigit())
async def process_wish_news_press(message: Message, state: FSMContext):
    await state.update_data(number=message.text)
    data_team = await state.get_data()
    add_team(user_id=message.from_user.id, name=data_team['name'], new_number=data_team['number'], text_color='ffffff')

    # Завершаем машину состояний
    await state.clear()
    # Отправляем в чат сообщение о сохранении данных
    await message.answer(
        text=f'Спасибо! Ваша команда <b>{get_user_team(message.from_user.id)}</b> зарегистрирована!'
    )


# Этот хэндлер будет срабатывать, если что-то ввели не так
# будет введено что-то некорректное
@router.message(StateFilter(FSMFillForm.fill_second_name))
async def warning_not_name(message: Message):
    await message.answer(
        text='То, что вы отправили не похоже на фамилию латинским буквами\n\n'
             'Пожалуйста, введите вашу фамилию\n\n'
             'Если вы хотите прервать заполнение анкеты - '
             'отправьте команду /cancel')


'''
///... ХЭНДЛЕРЫ РЕГИСТРАЦИИ КОМАНДЫ КОНЕЦ ///
'''

'''
///... ДОБАВЛЕНИЕ ЧЛЕНА КОМАНДЫ ///

@router.message(Command(commands='add_teammate'), StateFilter(default_state))
async def process_add_teammate_command(message: Message, state: FSMContext):
    print(get_team(message.from_user.id).__dict__)
    if not get_users(message.from_user.id):
        await message.answer(text='Вы не зарегистрированы, зарегистрируйтесь для выполнения действия команды.')
    else:
        if get_user_team(message.from_user.id) != 'PERSONAL ENTRY' and get_team(message.from_user.id).captain \
            and not all([get_team(message.from_user.id).first, get_team(message.from_user.id).second, get_team(message.from_user.id).third]):
            await message.answer(text='Пожалуйста, введите имя гонщика, которого Вы хотите добавить')
            await state.set_state(FSMFillForm.fill_team_name)
        else:
            await message.answer(text=f'Вы не являетесь капитаном команды')
'''

'''
///... ХЭНДЛЕРЫ ПРОГНОЗА НАЧАЛО ///
'''


# Этот хэндлер срабатывает на команду /predict и начинаем собирать прогноз
# Проверка зарегистрирован ли пользователь и отправляем кнопки с Командами по алфавиту
@router.message(Command(commands=['predict']), StateFilter(default_state))
async def predict_team(message: Message, state: FSMContext):
    if get_users(message.from_user.id):
        actual_gp: int = get_actual_gp()
        end_time = await get_end_grandprix_by_id(actual_gp)
        start_time = await get_start_grandprix_by_id(actual_gp)
        # if not is_prediced(message.from_user.id, actual_gp):
        if datetime.now() > start_time:
            if datetime.now() < end_time:
                penalty_time = await get_penalty_grandprix_by_id(actual_gp)
                await message.answer(text=f'Окончание приема прогноза на {get_name_gp(actual_gp)} GP закончится {end_time}\n Без штрафа прогноз можно подать до {penalty_time}')
                await message.answer(
                    text='Выберите Команду',
                    reply_markup=create_inline_kb(1, *sorted(
                        {i.driver_team + '  ' + i.engine_short for i in select_drivers()})))
                await state.set_state(FSMFillForm.select_engine)
            else:
                await message.answer(
                    text=f'В данный момент прогноз на {get_name_gp(actual_gp)} GP не принимается\n Прием прогнозов закончился {end_time}')
        else:
            await message.answer(text=f'В данный момент прогноз на {get_name_gp(actual_gp)} GP еще не принимается\n Прием прогнозов начнется {start_time}')

    # else:
    #   await message.answer(text='Вы уже отправили прогноз на актуальный GP')
    else:
        await message.answer(text='Вы не зарегистрированы')


# Сохраняем команду, отправляем кнопки с двигателями
@router.callback_query(StateFilter(FSMFillForm.select_engine),
                       F.data.in_({i.driver_team + '  ' + i.engine_short for i in select_drivers()}))
async def predict_engine(callback: CallbackQuery, state: FSMContext):
    await state.update_data(driver_team=callback.data.rsplit(' ', 1)[0].strip())
    await state.update_data(select1_engine=callback.data.split()[-1].strip())
    await callback.message.delete()
    await callback.message.answer(text='Спасибо!\nТеперь выберите двигатель',
                                  reply_markup=create_inline_kb(1,
                                                                *sorted(
                                                                    {i.driver_engine + '  ' + i.engine_short for i in
                                                                     select_drivers()})))
    await state.set_state(FSMFillForm.select_first)


# Сохраняем двигатель, отправляем кнопки с выбором первого пилота
@router.callback_query(StateFilter(FSMFillForm.select_first),
                       F.data.in_({i.driver_engine + '  ' + i.engine_short for i in select_drivers()}))
async def predict_first(callback: CallbackQuery, state: FSMContext):
    await state.update_data(driver_engine=callback.data.rsplit(' ', 1)[0].strip())
    await state.update_data(select2_engine=callback.data.split()[-1].strip())
    await callback.message.delete()
    await callback.message.answer(text='Спасибо!\nТеперь выберите первого пилота',
                                  reply_markup=create_inline_kb(1,
                                                                *[
                                                                    i.driver_name + ' (' + i.driver_team + ')' + '  ' + i.engine_short
                                                                    for i in
                                                                    select_drivers()]))
    await state.set_state(FSMFillForm.select_second)


# Сохраняем первого пилота, отправляем кнопки с выбором второго пилота
@router.callback_query(StateFilter(FSMFillForm.select_second),
                       F.data.in_([i.driver_name + ' (' + i.driver_team + ')' + '  ' + i.engine_short for i in
                                   select_drivers()]))
async def predict_second(callback: CallbackQuery, state: FSMContext):
    await state.update_data(first_driver=callback.data.split('(')[0].strip())
    await state.update_data(select3_engine=callback.data.split()[-1].strip())
    await callback.message.delete()
    predict = await state.get_data()
    await callback.message.answer(text='Спасибо!\nТеперь выберите второго пилота',
                                  reply_markup=create_inline_kb(1,
                                                                *[
                                                                    i.driver_name + ' (' + i.driver_team + ')' + '  ' + i.engine_short
                                                                    for i in
                                                                    select_drivers() if
                                                                    i.driver_name not in [*predict.values()]]))
    await state.set_state(FSMFillForm.select_third)


# Сохраняем второго пилота, отправляем кнопки с выбором третьего пилота
@router.callback_query(StateFilter(FSMFillForm.select_third),
                       F.data.in_([i.driver_name + ' (' + i.driver_team + ')' + '  ' + i.engine_short for i in
                                   select_drivers()]))
async def predict_third(callback: CallbackQuery, state: FSMContext):
    await state.update_data(second_driver=callback.data.split('(')[0].strip())
    await state.update_data(select4_engine=callback.data.split()[-1].strip())
    await callback.message.delete()
    predict = await state.get_data()
    if all(engine == predict['select1_engine'] for engine in
           [predict['select2_engine'], predict['select3_engine'], predict['select4_engine']]):
        await callback.message.answer(
            text='Вы выбрали 4 участника с одним мотором, начните выбор заново с команды /predict')
        await state.clear()
    else:
        await callback.message.answer(text='Спасибо!\nТеперь выберите третьего пилота',
                                      reply_markup=create_inline_kb(1,
                                                                    *[
                                                                        i.driver_name + ' (' + i.driver_team + ')' + '  ' + i.engine_short
                                                                        for i
                                                                        in select_drivers()[10:] if
                                                                        i.driver_name not in [*predict.values()]]))
        await state.set_state(FSMFillForm.select_fourth)


# Сохраняем третьего пилота, отправляем кнопки с выбором четвертого пилота
@router.callback_query(StateFilter(FSMFillForm.select_fourth),
                       F.data.in_([i.driver_name + ' (' + i.driver_team + ')' + '  ' + i.engine_short for i in
                                   select_drivers()][10:]))
async def predict_fourth(callback: CallbackQuery, state: FSMContext):
    await state.update_data(third_driver=callback.data.split('(')[0].strip())
    await state.update_data(select5_engine=callback.data.split()[-1].strip())
    await callback.message.delete()
    predict = await state.get_data()
    values = [predict['select1_engine'], predict['select2_engine'], predict['select3_engine'],
              predict['select4_engine'], predict['select5_engine']]
    if any(values.count(x) == 4 for x in set(values)):
        await callback.message.answer(
            text='Вы выбрали 4 участника с одним мотором, начните выбор заново с команды /predict')
        await state.clear()
    else:
        await callback.message.answer(text='Спасибо!\nТеперь выберите четвертого пилота',
                                      reply_markup=create_inline_kb(1,
                                                                    *[
                                                                        i.driver_name + ' (' + i.driver_team + ')' + '  ' + i.engine_short
                                                                        for i
                                                                        in select_drivers()[15:] if
                                                                        i.driver_name not in [*predict.values()]]))
        await state.set_state(FSMFillForm.select_gap)


# Сохраняем четвертого пилота, отправляем текст с выбором отставания от лидера
@router.callback_query(StateFilter(FSMFillForm.select_gap),
                       F.data.in_([i.driver_name + ' (' + i.driver_team + ')' + '  ' + i.engine_short for i in
                                   select_drivers()][15:]))
async def predict_gap(callback: CallbackQuery, state: FSMContext):
    await state.update_data(fourth_driver=callback.data.split('(')[0].strip())
    await state.update_data(select6_engine=callback.data.split()[-1].strip())
    await callback.message.delete()
    predict = await state.get_data()
    values = [predict['select1_engine'], predict['select2_engine'], predict['select3_engine'],
              predict['select4_engine'], predict['select5_engine'], predict['select6_engine']]
    if any(values.count(x) == 4 for x in set(values)):
        await callback.message.answer(
            text='Вы выбрали 4 участника с одним мотором, начните выбор заново с команды /predict')
        await state.clear()
    else:
        await callback.message.answer(text='Спасибо!\nТеперь введите отставание от лидера в секундах (целое число)')
        await state.set_state(FSMFillForm.select_lapped)


# Если что-то пошло не так при выборе на инлайн кнопках
@router.message(StateFilter(FSMFillForm.select_engine, FSMFillForm.select_first, FSMFillForm.select_second,
                            FSMFillForm.select_third, FSMFillForm.select_fourth, FSMFillForm.select_gap))
async def predict_engine_(message: CallbackQuery, state: FSMContext):
    await message.answer(text='Используйте кнопки меню для выбора')


# Сохраняем отставание, отправляем текст с выбором количества круговых
@router.message(StateFilter(FSMFillForm.select_lapped), F.text.isdigit())
async def predict_gap(message: CallbackQuery, state: FSMContext):
    await state.update_data(gap=message.text)
    await message.answer(text='Спасибо!\nТеперь введите количество круговых')
    await state.set_state(FSMFillForm.end_select)


# Если вместо отрыва ввели что-то не то
@router.message(StateFilter(FSMFillForm.select_lapped))
async def predict_gap(message: CallbackQuery, state: FSMContext):
    await message.answer(text='Вы ввели что-то неподходящее.\nВведите отставание от лидера в секундах (целое число)')


# Сохранение количества круговых и запись прогноза в БД, выход
@router.message(StateFilter(FSMFillForm.end_select), F.text.isdigit())
async def predict_lap(message: CallbackQuery, state: FSMContext):
    await state.update_data(lapped=message.text)
    gp = get_actual_gp()
    penalty_time = await get_penalty_grandprix_by_id(gp)
    end_time = await get_end_grandprix_by_id(gp)
    if datetime.now() < penalty_time:
        await state.update_data(penalty=None)
    else:
        await state.update_data(penalty=30)
    predict = await state.get_data()
    values = [predict['select1_engine'], predict['select2_engine'], predict['select3_engine'],
              predict['select4_engine'], predict['select5_engine'], predict['select6_engine']]
    if len({predict['first_driver'], predict['second_driver'], predict['third_driver'], predict['fourth_driver']}) != 4:
        await message.answer(
            text='<b>Вы выбрали несколько одинаковых гонщиков, используя старые кнопки, пожалуйста, используйте актуальные кнопки и начните выбор заново с команды /predict</b>')
        await state.clear()
    elif any(values.count(x) == 4 for x in set(values)):
        await message.answer(
            text='Вы выбрали 4 участника с одним мотором, начните выбор заново с команды /predict')
        await state.clear()
    elif end_time < datetime.now():
        await message.answer(
            text='К сожалению Вы не успели сделать прогноз на {get_name_gp(actual_gp)} GP, окончание приема заявок было до {end_time}')
        await state.clear()
    else:

        await message.answer(text=f'''Спасибо!\nВаш прогноз на <b>{get_name_gp(gp)}</b> GP: 
        Команда: <b>{predict['driver_team']}</b> 
        Двигатель: <b>{predict['driver_engine']}</b>
        Первый пилот: <b>{predict['first_driver']}</b>
        Второй пилот: <b>{predict['second_driver']}</b>
        Третий пилот: <b>{predict['third_driver']}</b>
        Четвертый пилот: <b>{predict['fourth_driver']}</b>
        Отставание от лидера: <b>{predict['gap']}</b>
        Количество круговых: <b>{predict['lapped']}</b>
        ''')
        # Удаляем служебные ключи
        for i in ['select1_engine', 'select2_engine', 'select3_engine', 'select4_engine', 'select5_engine',
                  'select6_engine']:
            predict.pop(i)

        # Пишем прогноз в базу
        time = datetime.now()
        send_predict(message.from_user.id, gp, time=time, **predict)

        # Завершаем машину состояний
        await state.clear()


# Если вместо отрыва ввели что-то не то
@router.message(StateFilter(FSMFillForm.end_select))
async def predict_gap(message: CallbackQuery, state: FSMContext):
    await message.answer(text='Вы ввели что-то неподходящее.\nВведите количество круговых')


'''

///ХЭНДЛЕРЫ ПРОГНОЗА КОНЕЦ///

'''


# Этот хэндлер будет срабатывать на отправку команды /showdata
# и отправлять в чат данные анкеты, либо сообщение об отсутствии данных
@router.message(Command(commands='showdata'), StateFilter(default_state))
async def process_showdata_command(message: Message):
    # Отправляем пользователю анкету, если она есть в "базе данных"
    if get_users(message.from_user.id):
        user = get_users(message.from_user.id)
        await message.answer(f' Ваше имя: {user.name}')
    else:
        await message.answer(text='Вы не зарегистрированы')


# Этот хэндлер будет срабатывать на отправку команды /championship
@router.message(Command(commands='championship'), StateFilter(default_state))
async def process_championship_command(message: Message):
    points_all: dict = show_points()
    text_for_answer = f'POS|DRIVER                   |CH.PTS|\n'
    for index, user in enumerate(
            sorted(points_all, key=lambda x: sum([i for i in x.values() if isinstance(i, int)]), reverse=True), 1):
        text_for_answer += f'{index:<3}|{user['User']:<25}|{sum([i for i in user.values() if isinstance(i, int)]):<3}|\n'
    await message.answer(f'<code>{text_for_answer}</code>')
