from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message, PhotoSize
from aiogram.filters import Command, CommandStart, StateFilter, BaseFilter
from lexicon.lexicon_ru import LEXICON_RU
from keyboards.inline_keyboards import create_inline_kb
from database.database import select_drivers, add_user, get_users, send_predict
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.fsm.storage.redis import RedisStorage, Redis
from database.database import get_all_users, get_users_by_name

admin_router: Router = Router()


class FSMFillForm(StatesGroup):
    # Создаем экземпляры класса State, последовательно
    # перечисляя возможные состояния, в которых будет находиться
    # бот в разные моменты взаимодейтсвия с пользователем
    admin_mode = State()  # Состояние нахождения в админке
    find_user = State()


class IsAdmin(BaseFilter):
    async def __call__(self, message: Message, all_admins) -> bool:
        return message.from_user.id in all_admins


# Этот хэндлер будет срабатывать на команду /admin
# и переводить бота в состояние ожидания ввода имени
@admin_router.message(IsAdmin(), Command(commands='admin'), StateFilter(default_state))
async def results_command(message: Message, state: FSMContext):
    await message.answer(text='Меню администратора', reply_markup=create_inline_kb(2,
                                                                                   'Управление пользователями'))
    await state.set_state(FSMFillForm.admin_mode)


@admin_router.callback_query(StateFilter(FSMFillForm.admin_mode), F.data == 'Управление пользователями')
async def user_setup(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer(text='Меню управления пользователями',
                                  reply_markup=create_inline_kb(2, 'Показать всех пользователей', 'Найти пользователя'))

@admin_router.callback_query(StateFilter(FSMFillForm.admin_mode), F.data == 'Показать всех пользователей')
async def show_users(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    for item in await get_all_users():
        await callback.message.answer(text=f'id_telegram: {item['id_telegram']}, name: {item['name']}')

@admin_router.callback_query(StateFilter(FSMFillForm.admin_mode), F.data == 'Найти пользователя')
async def find_user(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer(text='Введите полное имя')
    await state.set_state(FSMFillForm.find_user)

@admin_router.message(StateFilter(FSMFillForm.find_user))
async def user_setup(message: Message, state: FSMContext):
    await message.delete()
    for item in await get_users_by_name(message.text):
        await message.answer(text=f'id_telegram: {item['id_telegram']}, name: {item['name']}')




'''
@admin_router.callback_query(StateFilter(FSMFillForm.admin_mode), F.data == 'Управление пользователями')
async def user_setup(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer(text='Введите фамилию участника')
    await callback.answer()
'''
