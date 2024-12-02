from aiogram.utils.chat_member import USERS
from certifi import where
from sqlalchemy import create_engine, select, update
from sqlalchemy.orm import sessionmaker
from database.models import *


# Создаем базу данных
engine = create_engine("sqlite:///fantasy.db", echo=False)

# Создаем сессию
Session = sessionmaker(engine)



with Session() as session:
    for _ in range(57):
        user_id, name, second_name = input().split()
        try:
            session.add(User(name=name + ' ' + second_name, id_telegram=user_id))
            session.commit()
        except:
            pass