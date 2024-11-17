from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message, PhotoSize
from aiogram.filters import Command, CommandStart, StateFilter
from lexicon.lexicon_ru import LEXICON_RU
from keyboards.inline_keyboards import create_inline_kb
from database.database import select_drivers, update_user, get_users, send_predict, get_predict, add_result, show_result, get_actual_gp
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.fsm.storage.redis import RedisStorage, Redis
from dataprocessing.get_data import get_res_gp


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


# Этот хэндлер срабатывает на команду /predict
@router.message(Command(commands=['predict']), StateFilter(default_state))
async def process_predict_command(message: Message, state: FSMContext):
    if get_users(message.from_user.id):
        await message.answer(
            text='Выберите первого пилота',
            reply_markup=create_inline_kb(1, *[i.driver_name for i in select_drivers()])
        )
        await state.set_state(FSMFillForm.select_first)
    else:
        await message.answer(text='Вы не зарегистрированы')


# Сохранение первого
@router.callback_query(StateFilter(FSMFillForm.select_first), F.data.in_([i.driver_name for i in select_drivers()]))
async def process_name_sent(callback: CallbackQuery, state: FSMContext):
    await state.update_data(first_driver=callback.data)
    await callback.message.delete()
    await callback.message.answer(text='Спасибо!\n\nА теперь введите второго пилота',
                                  reply_markup=create_inline_kb(1, *[i.driver_name for i in select_drivers()]))
    await state.set_state(FSMFillForm.select_second)


# Сохранение второго
@router.callback_query(StateFilter(FSMFillForm.select_second), F.data.in_([i.driver_name for i in select_drivers()]))
async def process_name_sent(callback: CallbackQuery, state: FSMContext):
    await state.update_data(second_driver=callback.data)
    await callback.message.delete()
    await callback.message.answer(text='Спасибо!\n\nА теперь введите третьего пилота',
                                  reply_markup=create_inline_kb(1, *[i.driver_name for i in select_drivers()][10:]))
    await state.set_state(FSMFillForm.select_third)


# Сохранение третьего
@router.callback_query(StateFilter(FSMFillForm.select_third),
                       F.data.in_([i.driver_name for i in select_drivers()][10:]))
async def process_name_sent(callback: CallbackQuery, state: FSMContext):
    await state.update_data(third_driver=callback.data)
    await callback.message.delete()
    await callback.message.answer(text='Спасибо!\n\nА теперь введите четвертого пилота',
                                  reply_markup=create_inline_kb(1, *[i.driver_name for i in select_drivers()][15:]))
    await state.set_state(FSMFillForm.select_fourth)


# Сохранение четвертого
@router.callback_query(StateFilter(FSMFillForm.select_fourth),
                       F.data.in_([i.driver_name for i in select_drivers()][15:]))
async def process_name_sent(callback: CallbackQuery, state: FSMContext):
    await state.update_data(fourth_driver=callback.data)
    await callback.message.delete()
    await callback.message.answer(text='Спасибо!\n\nА теперь введите команду',
                                  reply_markup=create_inline_kb(1, *{i.driver_team for i in select_drivers()}))
    await state.set_state(FSMFillForm.select_team)


# Сохранение команды
@router.callback_query(StateFilter(FSMFillForm.select_team), F.data.in_({i.driver_team for i in select_drivers()}))
async def process_name_sent(callback: CallbackQuery, state: FSMContext):
    await state.update_data(driver_team=callback.data)
    await callback.message.delete()
    await callback.message.answer(text='Спасибо!\n\nА теперь введите двигатель',
                                  reply_markup=create_inline_kb(1, *{i.driver_engine for i in select_drivers()}))
    await state.set_state(FSMFillForm.select_engine)


# Сохранение двигателя
@router.callback_query(StateFilter(FSMFillForm.select_engine), F.data.in_({i.driver_engine for i in select_drivers()}))
async def process_name_sent(callback: CallbackQuery, state: FSMContext):
    await state.update_data(driver_engine=callback.data)
    await callback.message.delete()
    await callback.message.answer(text='Спасибо!\n\nА теперь введите отставание')
    await state.set_state(FSMFillForm.select_engine)


# Сохранение отставания
@router.message(StateFilter(FSMFillForm.select_engine), F.text.isdigit())
async def process_name_sent(message: CallbackQuery, state: FSMContext):
    await state.update_data(gap=message.text)
    await message.answer(text='Спасибо!\n\nА теперь введите количество круговых')
    await state.set_state(FSMFillForm.select_gap)


# Сохранение количества круговых
@router.message(StateFilter(FSMFillForm.select_gap), F.text.isdigit())
async def process_name_sent(message: CallbackQuery, state: FSMContext):
    await state.update_data(lapped=message.text)
    await message.answer(text='Спасибо!\n\nА вроде все')
    await state.set_state(FSMFillForm.select_lapped)
    user = await state.get_data()
    await message.answer(text=f'Спасибо!\n Вы выбрали {user}')
    await state.update_data(penalty=0)

    # Пишем прогноз в базу
    gp = get_actual_gp()
    send_predict(message.from_user.id, gp, **user)

    # Завершаем машину состояний
    await state.clear()
    # Отправляем в чат сообщение с предложением посмотреть свою анкету
    await message.answer(
        text='Чтобы посмотреть свой прогноз '
             ' - отправьте команду /viewpredict'
    )


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

# Этот хэндлер будет срабатывать на отправку команды /calculation
@router.message(Command(commands='viewresult'), StateFilter(default_state))
async def process_showdata_command(message: Message):
    gp = get_actual_gp()
    data = show_result(gp)

    text_for_answer = f''
    for index, (user, result) in enumerate(data, 1):
        text_for_answer += f'{index:<2}) {user.name:<20}| {result.first_driver:<2}| {result.second_driver:<2}| {result.third_driver:<2}| {result.fourth_driver:<2}| {result.driver_team:<2}| {result.driver_engine:<2}| {result.gap:<2}| {result.lapped:<2}| {result.penalty:<2}| {result.total:<3}| \n'
        #print(user.name, result.first_driver, result.second_driver, result.third_driver, result.fourth_driver,
         #     result.driver_team, result.driver_engine, result.gap, result.lapped, result.total)
    await message.answer(f'<code>{text_for_answer}</code>', isable_web_page_preview=True)

@router.message(Command(commands='calculation'), StateFilter(default_state))
async def process_showdata_command(message: Message):
    deltas = {0: 10, 1: 7, 2: 5, 3: 3, 4: 2, 5: 1}
    gp = get_actual_gp()
    predicts_from_db = get_predict(gp)
    print(len(predicts_from_db))
    results_predict_gp = get_res_gp()

    names = [i.driver_name for i in select_drivers()]
    first_max = max([results_predict_gp[name] for  name in names])
    names = [i.driver_name for i in select_drivers()[10:]]
    second_max = max([results_predict_gp[name] for  name in names])
    names = [i.driver_name for i in select_drivers()[15:]]
    third_max = max([results_predict_gp[name] for  name in names])

    for predict in predicts_from_db:
        counter_best = 0
        max_best = []
        max_not_best = []
        counter_lap_gap = 0
        if results_predict_gp.get(predict.first_driver) == first_max or results_predict_gp.get(predict.second_driver) == first_max:
            counter_best += 1
            max_best.append(first_max)

        if results_predict_gp.get(predict.first_driver) == first_max and results_predict_gp.get(predict.second_driver) == first_max:
            max_not_best.append(first_max)
        elif results_predict_gp.get(predict.first_driver) != first_max and results_predict_gp.get(predict.second_driver) != first_max:
            max_not_best.append(results_predict_gp.get(predict.first_driver))
            max_not_best.append(results_predict_gp.get(predict.second_driver))
        elif results_predict_gp.get(predict.first_driver) != first_max:
            max_not_best.append(results_predict_gp.get(predict.first_driver))
        else:
            max_not_best.append(results_predict_gp.get(predict.second_driver))

        if results_predict_gp.get(predict.third_driver) == second_max:
            counter_best += 1
            max_best.append(second_max)
        else:
            max_not_best.append(results_predict_gp.get(predict.third_driver))

        if results_predict_gp.get(predict.fourth_driver) == third_max:
            counter_best += 1
            max_best.append(third_max)
        else:
            max_not_best.append(results_predict_gp.get(predict.fourth_driver))

        if results_predict_gp['gap'] == predict.gap:
            counter_lap_gap += 1
        if results_predict_gp['laps'] == predict.lapped:
            counter_lap_gap += 1

        if len(max_best) < 3:
            max_best.extend([0] * (3 - len(max_best)))

        if len(max_not_best) < 4:
            max_not_best.extend([0] * (4 - len(max_not_best)))

        max1_best, max2_best, max3_best = sorted(max_best, reverse=True)
        max1_not_best, max2_not_best, max3_not_best, max4_not_best = sorted(max_not_best, reverse=True)


        delta_gap = abs(results_predict_gp['gap'] - predict.gap)
        delta_laps = abs(results_predict_gp['laps'] - predict.lapped)
        max_lap_gap = max(deltas.get(delta_gap, 0), deltas.get(delta_laps, 0))

        add_result(predict.user_id, results_predict_gp.get(predict.first_driver), results_predict_gp.get(predict.second_driver),
                   results_predict_gp.get(predict.third_driver), results_predict_gp.get(predict.fourth_driver),
                   results_predict_gp.get('team_' + predict.driver_team),results_predict_gp.get('engine_' + predict.driver_engine),
                   deltas.get(delta_gap, 0), deltas.get(delta_laps, 0), counter_best, max1_best, max2_best, max3_best, max1_not_best, max2_not_best, max3_not_best, max4_not_best, counter_lap_gap ,max_lap_gap, predict.penalty, gp)



# # Хэндлер для текстовых сообщений, которые не попали в другие хэндлеры
@router.message()
async def answer_all(message: Message):
    await message.answer(text=LEXICON_RU['unknown_command'])
