from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String

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

#for i in select_drivers(10):
#    print(i.driver_name)