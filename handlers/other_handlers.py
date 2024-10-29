from aiogram import Router
from aiogram.types import Message
from aiogram.utils.chat_member import ADMINS

router: Router = Router()

# Хэндлер для текстовых сообщений, которые отправляют незнакомцы.
@router.message(lambda message: message.from_user.id != ADMINS)
async def send_answer(message: Message):
    await message.answer(text='Я тебя не знаю, а мой создатель запретил мне разговаривать с незнакомцами!')