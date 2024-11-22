from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message, PhotoSize
from aiogram.filters import Command, CommandStart, StateFilter
from lexicon.lexicon_ru import LEXICON_RU
from keyboards.inline_keyboards import create_inline_kb
from database.database import select_drivers, add_user, get_users, send_predict
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.fsm.storage.redis import RedisStorage, Redis

router: Router = Router()

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

# Этот хэндлер будет срабатывать на команду /registration
# и переводить бота в состояние ожидания ввода имени
@router.message(Command(commands='results'), StateFilter(default_state))
async def process_fillform_command(message: Message, state: FSMContext):
    await message.answer(text='Пожалуйста, введите ваше имя')
    # Устанавливаем состояние ожидания ввода имени
    await state.set_state(FSMFillForm.fill_name)