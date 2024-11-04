from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String

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



# Создаем таблицы в базе данных
Base.metadata.create_all(bind=engine)