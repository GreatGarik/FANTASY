from openpyxl import Workbook
import os
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message, FSInputFile
from aiogram.filters import Command, CommandStart, StateFilter
from lexicon.lexicon_ru import LEXICON_RU
from keyboards.inline_keyboards import create_inline_kb
from database.database import select_drivers, update_user, get_users, send_predict, get_predict, add_result, \
    show_result, get_actual_gp, add_points, show_result, show_points, get_result, check_res, show_points_all
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.fsm.storage.redis import RedisStorage, Redis
from dataprocessing.calculation_gp_drivers import calculation_drivers

router: Router = Router()

# Инициализируем Redis
redis = Redis(host='127.0.0.1')

# Инициализируем хранилище (создаем экземпляр класса MemoryStorage)
storage = RedisStorage(redis=redis)


class FSMFillForm(StatesGroup):
    # Создаем экземпляры класса State, последовательно
    # перечисляя возможные состояния, в которых будет находиться
    # бот в разные моменты взаимодейтсвия с пользователем
    fill_name = State()  # Состояние ожидания ввода имени
    fill_second_name = State()  # Состояние ожидания ввода фамилии
    fill_vk = State()  # Состояние ожидания ссылки на аккаунт VK
    select_first = State()
    select_second = State()
    select_third = State()
    select_fourth = State()
    select_team = State()
    select_engine = State()
    select_gap = State()
    select_lapped = State()
    end_select = State()


# Этот хэндлер срабатывает на команду /start
@router.message(CommandStart(), StateFilter(default_state))
async def process_start_command(message: Message):
    await message.answer(text=LEXICON_RU['start_answer'])


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


# Этот хэндлер срабатывает на команду /help
@router.message(Command(commands=['help']))
async def process_help_command(message: Message):
    await message.answer(text=LEXICON_RU['help_answer'])


# Этот хэндлер будет срабатывать на команду /registration
# и переводить бота в состояние ожидания ввода имени
@router.message(Command(commands='registration'), StateFilter(default_state))
async def process_fillform_command(message: Message, state: FSMContext):
    await message.answer(text='Пожалуйста, введите ваше имя')
    # Устанавливаем состояние ожидания ввода имени
    await state.set_state(FSMFillForm.fill_name)


# Этот хэндлер будет срабатывать, если введено корректное имя
# и переводить в состояние ожидания ввода возраста
@router.message(StateFilter(FSMFillForm.fill_name), F.text.isalpha())
async def process_name_sent(message: Message, state: FSMContext):
    # Сохраняем введенное имя в хранилище по ключу "name"
    await state.update_data(name=message.text.title())
    await message.answer(text='Спасибо!\n\nА теперь введите вашу фамилию')
    # Устанавливаем состояние ожидания ввода возраста
    await state.set_state(FSMFillForm.fill_second_name)


# Этот хэндлер будет срабатывать, если во время ввода имени
# будет введено что-то некорректное
@router.message(StateFilter(FSMFillForm.fill_name))
async def warning_not_name(message: Message):
    await message.answer(
        text='То, что вы отправили не похоже на имя\n\n'
             'Пожалуйста, введите ваше имя\n\n'
             'Если вы хотите прервать заполнение анкеты - '
             'отправьте команду /cancel')


# Этот хэндлер будет срабатывать, если введена корректная фамилия
# и переводить в состояние ожидания ввода вк
@router.message(StateFilter(FSMFillForm.fill_second_name), F.text.isalpha())
async def process_name_sent(message: Message, state: FSMContext):
    # Cохраняем введенное имя в хранилище по ключу "second_name"
    await state.update_data(second_name=message.text.capitalize())
    await message.answer(text='Спасибо!\n\nА теперь введите ссылку на ваш профиль Вконтакте')
    # Устанавливаем состояние ожидания ввода вк
    await state.set_state(FSMFillForm.fill_vk)


# Этот хэндлер будет срабатывать, если во время ввода фамилии
# будет введено что-то некорректное
@router.message(StateFilter(FSMFillForm.fill_second_name))
async def warning_not_name(message: Message):
    await message.answer(
        text='То, что вы отправили не похоже на фамилию\n\n'
             'Пожалуйста, введите вашу фамилию\n\n'
             'Если вы хотите прервать заполнение анкеты - '
             'отправьте команду /cancel')


# Этот хэндлер будет срабатывать на ввод ВК
# записывать данные и выводить из машины состояний
@router.message(StateFilter(FSMFillForm.fill_vk), F.text.startswith('https://vk.com/id'))
async def process_wish_news_press(message: Message, state: FSMContext):
    # Cохраняем данные о вк
    await state.update_data(vk_id=message.text)
    # Добавляем в базу данных анкету пользователя
    # по ключу id пользователя
    user = await state.get_data()
    update_user(message.from_user.id, **user)

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


# Этот хэндлер будет срабатывать, если во время ввода вк
# будет введено что-то некорректное
@router.message(StateFilter(FSMFillForm.fill_vk))
async def warning_not_name(message: Message):
    await message.answer(
        text='То, что вы отправили не похоже на ссылку на профиль в ВК\n\n'
             'Пожалуйста, введите ссылку на ваш профиль Вконтакте\n'
             'Если вы хотите прервать заполнение анкеты - '
             'отправьте команду /cancel')


'''

//... ХЭНДЛЕРЫ ПРОГНОЗА НАЧАЛО ///

'''


# Этот хэндлер срабатывает на команду /predict и начинаем собирать прогноз
# Проверяем зарегистрирован ли пользователь и отправляем кнопки с Командами по алфавиту
@router.message(Command(commands=['predict']), StateFilter(default_state))
async def predict_team(message: Message, state: FSMContext):
    if get_users(message.from_user.id):
        await message.answer(
            text='Выберите Команду',
            reply_markup=create_inline_kb(1, *sorted(
                {i.driver_team + ' (' + i.driver_engine + ')' for i in select_drivers()})))
        await state.set_state(FSMFillForm.select_engine)
    else:
        await message.answer(text='Вы не зарегистрированы')


# Сохраняем команду, отправляем кнопки с двигателями
@router.callback_query(StateFilter(FSMFillForm.select_engine),
                       F.data.in_({i.driver_team + ' (' + i.driver_engine + ')' for i in select_drivers()}))
async def predict_engine(callback: CallbackQuery, state: FSMContext):
    await state.update_data(driver_team=callback.data.split('(')[0].strip())
    await state.update_data(select1_engine=callback.data.split()[-1].strip('()'))
    await callback.message.delete()
    await callback.message.answer(text='Спасибо!\nТеперь выберите двигатель',
                                  reply_markup=create_inline_kb(1,
                                                                *sorted({i.driver_engine for i in select_drivers()})))
    await state.set_state(FSMFillForm.select_first)


# Сохраняем двигатель, отправляем кнопки с выбором первого пилота
@router.callback_query(StateFilter(FSMFillForm.select_first), F.data.in_({i.driver_engine for i in select_drivers()}))
async def predict_first(callback: CallbackQuery, state: FSMContext):
    await state.update_data(driver_engine=callback.data)
    await state.update_data(select2_engine=callback.data)
    await callback.message.delete()
    await callback.message.answer(text='Спасибо!\nТеперь выберите первого пилота',
                                  reply_markup=create_inline_kb(1, *[i.driver_name  + ' (' + i.driver_engine + ')' for i in select_drivers()]))
    await state.set_state(FSMFillForm.select_second)


# Сохраняем первого пилота, отправляем кнопки с выбором второго пилота
@router.callback_query(StateFilter(FSMFillForm.select_second), F.data.in_([i.driver_name  + ' (' + i.driver_engine + ')' for i in select_drivers()]))
async def predict_second(callback: CallbackQuery, state: FSMContext):
    await state.update_data(first_driver=callback.data.split('(')[0].strip())
    await state.update_data(select3_engine=callback.data.split('(')[-1].strip('()'))
    await callback.message.delete()
    predict = await state.get_data()
    await callback.message.answer(text='Спасибо!\nТеперь выберите второго пилота',
                                  reply_markup=create_inline_kb(1, *[i.driver_name  + ' (' + i.driver_engine + ')' for i in select_drivers() if
                                                                     i.driver_name not in [*predict.values()]]))
    await state.set_state(FSMFillForm.select_third)


# Сохраняем второго пилота, отправляем кнопки с выбором третьего пилота
@router.callback_query(StateFilter(FSMFillForm.select_third), F.data.in_([i.driver_name  + ' (' + i.driver_engine + ')' for i in select_drivers()]))
async def predict_third(callback: CallbackQuery, state: FSMContext):
    await state.update_data(second_driver=callback.data.split('(')[0].strip())
    await state.update_data(select4_engine=callback.data.split('(')[-1].strip('()'))
    await callback.message.delete()
    predict = await state.get_data()
    if len(set([predict['select1_engine'], predict['select2_engine'], predict['select3_engine'],predict['select4_engine']])) == 1:
        await callback.message.answer(text='Вы выбрали 4 участника с одним мотором, начните выбор заново с команды /predict')
        await state.clear()
    else:
        await callback.message.answer(text='Спасибо!\nТеперь выберите третьего пилота',
                                      reply_markup=create_inline_kb(1, *[i.driver_name  + ' (' + i.driver_engine + ')' for i in select_drivers()[10:] if
                                                                         i.driver_name not in [*predict.values()]]))
        await state.set_state(FSMFillForm.select_fourth)


# Сохраняем третьего пилота, отправляем кнопки с выбором четвертого пилота
@router.callback_query(StateFilter(FSMFillForm.select_fourth),
                       F.data.in_([i.driver_name  + ' (' + i.driver_engine + ')' for i in select_drivers()][10:]))
async def predict_fourth(callback: CallbackQuery, state: FSMContext):
    await state.update_data(third_driver=callback.data.split('(')[0].strip())
    await state.update_data(select5_engine=callback.data.split('(')[-1].strip('()'))
    await callback.message.delete()
    predict = await state.get_data()
    values = [predict['select1_engine'], predict['select2_engine'], predict['select3_engine'], predict['select4_engine'], predict['select5_engine']]
    if any(values.count(x) == 4 for x in set(values)):
        await callback.message.answer(
            text='Вы выбрали 4 участника с одним мотором, начните выбор заново с команды /predict')
        await state.clear()
    else:
        await callback.message.answer(text='Спасибо!\nТеперь выберите четвертого пилота',
                                      reply_markup=create_inline_kb(1, *[i.driver_name  + ' (' + i.driver_engine + ')' for i in select_drivers()[15:] if
                                                                         i.driver_name not in [*predict.values()]]))
        await state.set_state(FSMFillForm.select_gap)


# Сохраняем четвертого пилота, отправляем текст с выбором отставания от лидера
@router.callback_query(StateFilter(FSMFillForm.select_gap), F.data.in_([i.driver_name  + ' (' + i.driver_engine + ')' for i in select_drivers()][15:]))
async def predict_gap(callback: CallbackQuery, state: FSMContext):
    await state.update_data(fourth_driver=callback.data.split('(')[0].strip())
    await state.update_data(select6_engine=callback.data.split('(')[-1].strip('()'))
    await callback.message.delete()
    predict = await state.get_data()
    values = [predict['select1_engine'], predict['select2_engine'], predict['select3_engine'], predict['select4_engine'], predict['select5_engine'], predict['select6_engine']]
    if any(values.count(x) == 4 for x in set(values)):
        await callback.message.answer(
            text='Вы выбрали 4 участника с одним мотором, начните выбор заново с команды /predict')
        await state.clear()
    else:
        await callback.message.answer(text='Спасибо!\nТеперь введите отставание от лидера')
        await state.set_state(FSMFillForm.select_lapped)


# Сохраняем отставание, отправляем текст с выбором количества круговых
@router.message(StateFilter(FSMFillForm.select_lapped), F.text.isdigit())
async def predict_gap(message: CallbackQuery, state: FSMContext):
    await state.update_data(gap=message.text)
    await message.answer(text='Спасибо!\nТеперь введите количество круговых')
    await state.set_state(FSMFillForm.end_select)


# Сохранение количества круговых и запись прогноза в БД, выход
@router.message(StateFilter(FSMFillForm.end_select), F.text.isdigit())
async def predict_lap(message: CallbackQuery, state: FSMContext):
    await state.update_data(lapped=message.text)
    await message.answer(text='Спасибо!\nВроде все')
    await state.update_data(penalty=0)
    predict = await state.get_data()
    await message.answer(text=f'Спасибо!\nВы выбрали {predict}')

    # Пишем прогноз в базу
    gp = get_actual_gp()
    send_predict(message.from_user.id, gp, **predict)

    # Завершаем машину состояний
    await state.clear()
    # Отправляем в чат сообщение с предложением посмотреть свою анкету
    await message.answer(
        text='Чтобы посмотреть свой прогноз '
             ' - отправьте команду /viewpredict'
    )


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
        await message.answer(f' Ваше имя: {user.name}, Ссылка ВК: {user.vk_link}, Ваша команда: {user.user_team}',
                             disable_web_page_preview=True)
    else:
        await message.answer(text='Вы не зарегистрированы')


# Этот хэндлер будет срабатывать на отправку команды /viewresult
@router.message(Command(commands='viewresult'), StateFilter(default_state))
async def process_viewresult_command(message: Message):
    gp = get_actual_gp()
    data = show_result(gp)

    text_for_answer = f'POS|DRIVER              |D1|D2|D3|D4|TM|EN|DF|LP|PN|PTS|CPT|\n'
    for index, (user, result, points) in enumerate(data, 1):
        text_for_answer += f'{index:<3}|{user.name:<20}|{result.first_driver:<2}|{result.second_driver:<2}|{result.third_driver:<2}|{result.fourth_driver:<2}|{result.driver_team:<2}|{result.driver_engine:<2}|{result.gap:<2}|{result.lapped:<2}|{result.penalty:<2}|{result.total:<3}|{points.points:<3}|\n'
    await message.answer(f'<code>{text_for_answer}</code>', isable_web_page_preview=True)


# Этот хэндлер будет срабатывать на отправку команды /resultxls
@router.message(Command(commands='resultxls'), StateFilter(default_state))
async def process_resultcsv_command(message: Message):
    gp = get_actual_gp()
    data = show_result(gp)

    # Указываем имя файла
    xls_filename = 'results.xlsx'

    # Создаем новый Excel файл
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Results"

    # Записываем заголовки
    headers = ['POS', 'DRIVER', 'DR1', 'DR2', 'DR3', 'DR4', 'TM', 'ENG', 'DIFF', 'LAP', 'PEN', 'PTS', 'CH.PTS']
    sheet.append(headers)

    # Записываем данные
    for index, (user, result, points) in enumerate(data, 1):
        sheet.append([
            index,
            user.name,
            result.first_driver,
            result.second_driver,
            result.third_driver,
            result.fourth_driver,
            result.driver_team,
            result.driver_engine,
            result.gap,
            result.lapped,
            result.penalty,
            result.total,
            points.points
        ])

    # Сохраняем файл
    workbook.save(xls_filename)

    # Отправляем XLS файл
    await message.answer_document(
        document=FSInputFile(path=xls_filename),
        caption='Результаты в формате XLS',
        filename='results.xlsx'
    )

    # Удаляем файл после отправки
    os.remove(xls_filename)

# Этот хэндлер будет срабатывать на отправку команды /calculation
@router.message(Command(commands='calculation'), StateFilter(default_state))
async def process_calculation_command(message: Message):
    gp = get_actual_gp()
    if check_res(gp):
        await message.answer(f'Вы уже сделали расчет для этого GP', isable_web_page_preview=True)
    else:
        calculation_drivers(gp)
        await message.answer(f'Расчет результатов выполнен')

# Этот хэндлер будет срабатывать на отправку команды /championship
@router.message(Command(commands='championship'), StateFilter(default_state))
async def process_championship_command(message: Message):
    points_all: dict = show_points()
    text_for_answer = f'POS|DRIVER              |PTS|\n'
    for index, user in enumerate(sorted(points_all, key=lambda x: sum([i for i in x.values() if isinstance(i, int)]), reverse=True), 1):
        text_for_answer += f'{index:<3}|{user['User']:<20}|{sum([i for i in user.values() if isinstance(i, int)]):<3}|\n'
    await message.answer(f'<code>{text_for_answer}</code>', isable_web_page_preview=True)

# Этот хэндлер будет срабатывать на отправку команды /championship_full
@router.message(Command(commands='championship_full'), StateFilter(default_state))
async def process_championship_full_command(message: Message):
    points_list: dict = show_points_all()
    #print(points_list)
    for entry in points_list:
        entry['Total Points'] = sum(entry[key] for key in entry if key != 'User')
    print(1)
        # Сортируем по общему количеству очков
    points_list.sort(key=lambda x: x['Total Points'], reverse=True)
    print(2)
    # Заголовки таблицы
    header = ['Driver'] + [key for key in points_list[0] if key != 'User' and key != 'Total Points'] + ['Total Points']
    print(3)
    # Печатаем заголовки
    print(f"{header[0]:<25} {header[-1]:<10} {' | '.join(header[2:])}")
    print("-" * 50)


    # Печатаем строки с данными
    for entry in points_list:
        row = [entry['User'], entry['Total Points']] + [entry[key] for key in header[2:]]
        print(f"{row[0]:<25}|{row[1]:<10} {' | '.join(map(str, row[2:]))}")


    text_for_answer = f'POS|DRIVER              |PTS|\n'
    for index, user in enumerate(sorted(points_list, key=lambda x: sum([i for i in x.values() if isinstance(i, int)]), reverse=True), 1):
        text_for_answer += f'{index:<3}|{user['User']:<20}|{sum([i for i in user.values() if isinstance(i, int)]):<3}|\n'
    #await message.answer(f'<code>{text_for_answer}</code>', isable_web_page_preview=True)



# # Хэндлер для текстовых сообщений, которые не попали в другие хэндлеры
@router.message()
async def answer_all(message: Message):
    await message.answer(text=LEXICON_RU['unknown_command'])
