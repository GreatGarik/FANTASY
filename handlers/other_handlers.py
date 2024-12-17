from lexicon.lexicon_ru import LEXICON_RU
from aiogram import Router
from aiogram.types import Message

other_router: Router = Router()

# Хэндлер для текстовых сообщений, которые не попали в другие хэндлеры
@other_router.callback_query()
async def answer_all(message: Message):
    await message.answer(text=LEXICON_RU['unknown_button'])


# Хэндлер для текстовых сообщений, которые не попали в другие хэндлеры
@other_router.message()
async def answer_all(message: Message):
    await message.answer(text=LEXICON_RU['unknown_command'])
