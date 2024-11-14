from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String, ForeignKey
from championship2022 import gps
from drivers import drivers
from models import *

# Создаем базу данных
engine = create_engine("sqlite:///../fantasy.db", echo=True)




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

    for item in gps:
        new_gp = Grandprix(gp_name=item['gp'], year=item['year'], nextgp=item['nextgp'])
        session.add(new_gp)


    session.commit()
