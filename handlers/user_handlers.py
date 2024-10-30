from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.filters import Command, CommandStart
from lexicon.lexicon_ru import LEXICON_RU

router: Router = Router()


# Этот хэндлер срабатывает на команду /start
@router.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(text=LEXICON_RU['start_answer'])


# Этот хэндлер срабатывает на команду /help
@router.message(Command(commands=['help']))
async def process_help_command(message: Message):
    await message.answer(text=LEXICON_RU['help_answer'])

# Этот хэндлер срабатывает на команду /predict
@router.message(Command(commands=['predict']))
async def process_help_command(message: Message):
    await message.answer(text=LEXICON_RU['help_answer'])



# # Хэндлер для текстовых сообщений, которые не попали в другие хэндлеры
@router.message()
async def answer_all(message: Message):
    await message.answer(text=LEXICON_RU['unknown_command'])