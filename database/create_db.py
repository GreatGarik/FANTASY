from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String, ForeignKey
from drivers import drivers

# Создаем базу данных
engine = create_engine("sqlite:///../fantasy.db", echo=True)


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


# Определяем модель гран-при
class Grandprix(Base):
    __tablename__ = 'grandprix'

    id = Column(Integer, primary_key=True, index=True)
    gp_name = Column(String)
    year = Column(Integer)


# Создаем таблицы в базе данных
Base.metadata.create_all(bind=engine)

# Создаем сессию
Session = sessionmaker(engine)

# Заполняем пилотов
with Session() as session:
    for driver in drivers:
        new_driver = Driver(driver_name=driver['driver'], driver_points=driver['points'], driver_team=driver['team'],
                            driver_engine=driver['engine'], driver_nextgp=driver['nextGP'])
        session.add(new_driver)
    session.commit()
