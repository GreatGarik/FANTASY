from aiogram.utils.chat_member import USERS
from certifi import where
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String, ForeignKey

# Создаем базу данных
engine = create_engine("sqlite:///fantasy.db", echo=False)


# Создаем базовый класс для моделей
class Base(DeclarativeBase):
    pass


# Определяем модель пользователей
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    id_telegram = Column(Integer, unique=True)
    vk_link = Column(String)
    name = Column(String)
    user_team = Column(String)


# Определяем модель гонщиков
class Driver(Base):
    __tablename__ = 'drivers'

    id = Column(Integer, primary_key=True, index=True)
    driver_name = Column(String)
    driver_points = Column(Integer)
    driver_team = Column(String)
    driver_engine = Column(String)
    driver_nextgp = Column(String(1))

# Определяем модель гран-при
class Grandprix(Base):
    __tablename__ = 'grandprix'

    id = Column(Integer, primary_key=True, index=True)
    gp_name = Column(String)
    year = Column(Integer)

class Predict(Base):
    __tablename__ = 'predicts'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    first_driver = Column(String)
    second_driver = Column(String)
    third_driver = Column(String)
    fourth_driver = Column(String)
    driver_team = Column(String)
    driver_engine = Column(String)
    gap = Column(Integer)
    lapped = Column(Integer)


# Создаем таблицы в базе данных
Base.metadata.create_all(bind=engine)


# Создаем сессию
Session = sessionmaker(engine)

def select_drivers(start=None, stop=None):
    with Session() as session:

        statement = select(Driver).where(Driver.driver_nextgp=='Y')
        db_object = session.scalars(statement).all()
        return db_object[start:stop]
    

def update_user(user_id, name, second_name, vk_id):
    with Session() as session:
        try:
            session.add(User(name=name+' '+second_name, id_telegram= user_id, vk_link=vk_id))
            session.commit()
        except:
            pass

def send_predict(tg_id, first_driver, second_driver, third_driver, fourth_driver, driver_team, driver_engine, gap, lapped):
    with Session() as session:
        try:
            session.add(Predict(user_id=tg_id, first_driver = first_driver, second_driver=second_driver,
                                third_driver=third_driver, fourth_driver=fourth_driver,driver_team=driver_team,
                                driver_engine=driver_engine, gap=gap, lapped=lapped))
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