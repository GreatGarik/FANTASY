from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message, PhotoSize
from aiogram.filters import Command, CommandStart, StateFilter
from lexicon.lexicon_ru import LEXICON_RU
from keyboards.inline_keyboards import create_inline_kb
from database.database import select_drivers
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.fsm.storage.redis import RedisStorage, Redis

router: Router = Router()

# Инициализируем Redis
redis = Redis(host='127.0.0.1')

# Инициализируем хранилище (создаем экземпляр класса MemoryStorage)
storage = RedisStorage(redis=redis)

class FSMFillForm(StatesGroup):
    # Создаем экземпляры класса State, последовательно
    # перечисляя возможные состояния, в которых будет находиться
    # бот в разные моменты взаимодейтсвия с пользователем
    fill_name = State()        # Состояние ожидания ввода имени
    fill_age = State()         # Состояние ожидания ввода возраста
    fill_gender = State()      # Состояние ожидания выбора пола
    upload_photo = State()     # Состояние ожидания загрузки фото
    fill_education = State()   # Состояние ожидания выбора образования
    fill_wish_news = State()   # Состояние ожидания выбора получать ли новости


# Этот хэндлер срабатывает на команду /start
@router.message(CommandStart(), StateFilter(default_state))
async def process_start_command(message: Message):
    await message.answer(text=LEXICON_RU['start_answer'])

# Этот хэндлер будет срабатывать на команду "/cancel" в любых состояниях,
# кроме состояния по умолчанию, и отключать машину состояний
@router.message(Command(commands='cancel'), ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, state: FSMContext):
    await message.answer(
        text='Вы вышли из машины состояний\n\n'
             'Чтобы снова перейти к заполнению анкеты - '
             'отправьте команду /fillform'
    )
    # Сбрасываем состояние и очищаем данные, полученные внутри состояний
    await state.clear()


# Этот хэндлер срабатывает на команду /help
@router.message(Command(commands=['help']))
async def process_help_command(message: Message):
    await message.answer(text=LEXICON_RU['help_answer'])


# Этот хэндлер срабатывает на команду /predict
@router.message(Command(commands=['predict']), StateFilter(default_state))
async def process_predict_command(message: Message, state: FSMContext):
    drivers_for_choose = [i.driver_name for i in select_drivers()]
    await message.answer(
        text='Выберите первого пилота',
        reply_markup=create_inline_kb(1, *drivers_for_choose)
    )
    await state.set_state(FSMFillForm.fill_name)

# Этот хэндлер будет срабатывать, если введено корректное имя
# и переводить в состояние ожидания ввода возраста
@router.message(StateFilter(FSMFillForm.fill_name))
async def process_name_sent(callback: CallbackQuery, state: FSMContext):
    print('test')
    # Cохраняем введенное имя в хранилище по ключу "name"
    await state.update_data(gender=callback.data)
    await callback.message.delete()
    await message.answer(text='Спасибо!\n\nА теперь введите второго пилота')
    # Устанавливаем состояние ожидания ввода возраста
    await state.set_state(FSMFillForm.fill_age)


# Этот хэндлер будет срабатывать, если во время ввода имени
# будет введено что-то некорректное
@router.message(StateFilter(FSMFillForm.fill_name))
async def warning_not_name(message: Message):
    await message.answer(
        text='То, что вы отправили не похоже на имя\n\n'
             'Пожалуйста, введите ваше имя\n\n'
             'Если вы хотите прервать заполнение анкеты - '
             'отправьте команду /cancel')


# # Хэндлер для текстовых сообщений, которые не попали в другие хэндлеры
@router.message()
async def answer_all(message: Message):
    await message.answer(text=LEXICON_RU['unknown_command'])
