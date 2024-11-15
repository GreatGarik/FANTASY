from aiogram.utils.chat_member import USERS
from certifi import where
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from database.models import *

# Создаем базу данных
engine = create_engine("sqlite:///fantasy.db", echo=False)

# Создаем сессию
Session = sessionmaker(engine)


def select_drivers(start=None, stop=None):
    with Session() as session:
        statement = select(Driver).where(Driver.driver_nextgp == 'Y')
        db_object = session.scalars(statement).all()
        return db_object[start:stop]

def select_team_engine(pilot):
    with Session() as session:
        statement = select(Driver).where(Driver.driver_name == pilot)
        db_object = session.scalars(statement).one()
        return db_object.driver_team, db_object.driver_engine


def update_user(user_id, name: str, second_name: str, vk_id):
    with Session() as session:
        try:
            session.add(User(name=name + ' ' + second_name, id_telegram=user_id, vk_link=vk_id))
            session.commit()
        except:
            pass


def send_predict(tg_id, first_driver, second_driver, third_driver, fourth_driver, driver_team, driver_engine, gap,
                 lapped, gp=9):
    with Session() as session:
        try:
            session.add(Predict(user_id=tg_id, first_driver=first_driver, second_driver=second_driver,
                                third_driver=third_driver, fourth_driver=fourth_driver, driver_team=driver_team,
                                driver_engine=driver_engine, gap=gap, lapped=lapped, gp=gp))
            session.commit()
        except Exception as e:
            print(e)

def get_predict(gp=None):
    with Session() as session:
        statement = select(Predict).where()
        db_object = session.scalars(statement).all()
        return db_object

def add_result(tg_id, first_driver: int, second_driver: int, third_driver: int, fourth_driver: int, driver_team: int, driver_engine: int, gap: int,
                 lapped: int, gp=9):
    total = sum([first_driver, second_driver, third_driver, fourth_driver, driver_team, driver_engine, gap, lapped])
    with Session() as session:
        try:
            session.add(Result(user_id=tg_id, first_driver=first_driver, second_driver=second_driver,
                                third_driver=third_driver, fourth_driver=fourth_driver, driver_team=driver_team,
                                driver_engine=driver_engine, gap=gap, lapped=lapped, total=total, gp=gp))
            session.commit()
        except Exception as e:
            print(e)


def get_users(id_telegram=None):
    with Session() as session:
        if id_telegram:
            try:
                statement = select(User).where(User.id_telegram == id_telegram)
                return session.scalars(statement).one()
            except:
                return
        else:
            statement = select(User)
            db_object = session.scalars(statement).all()
            return db_object
