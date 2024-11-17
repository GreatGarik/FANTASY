from aiogram.utils.chat_member import USERS
from certifi import where
from sqlalchemy import create_engine, select, update, case
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


def get_actual_gp():
    with Session() as session:
        statement = select(Grandprix).where(Grandprix.nextgp)
        db_object = session.scalars(statement).one()
        return db_object.id


def update_user(user_id, name: str, second_name: str, vk_id):
    with Session() as session:
        try:
            session.add(User(name=name + ' ' + second_name, id_telegram=user_id, vk_link=vk_id))
            session.commit()
        except:
            pass


def send_predict(tg_id, gp, first_driver, second_driver, third_driver, fourth_driver, driver_team, driver_engine, gap,
                 lapped):
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
        statement = select(Predict).where(Predict.gp == gp)
        db_object = session.scalars(statement).all()
        return db_object


def add_result(tg_id, first_driver: int, second_driver: int, third_driver: int, fourth_driver: int, driver_team: int,
               driver_engine: int, gap: int,
               lapped: int, counter_best, max1_best, max2_best, max3_best, max1_not_best, max2_not_best, max3_not_best,
               max4_not_best, counter_lap_gap, max_lap_gap, penalty, gp=None):
    total = sum(
        [first_driver, second_driver, third_driver, fourth_driver, driver_team, driver_engine, gap, lapped]) - penalty
    with Session() as session:
        try:
            session.add(Result(user_id=tg_id, first_driver=first_driver, second_driver=second_driver,
                               third_driver=third_driver, fourth_driver=fourth_driver, driver_team=driver_team,
                               driver_engine=driver_engine, gap=gap, lapped=lapped, total=total,
                               counter_best=counter_best, max1_best=max1_best, max2_best=max2_best, max3_best=max3_best,
                               max1_not_best=max1_not_best, max2_not_best=max2_not_best, max3_not_best=max3_not_best,
                               max4_not_best=max4_not_best, counter_lap_gap=counter_lap_gap, max_lap_gap=max_lap_gap,
                               penalty=penalty, gp=gp))
            session.commit()
        except Exception as e:
            print(e)


def show_result(gp=None):
    with Session() as session:
        query = session.query(User, Result).where(Result.gp == gp)
        # query = query.join(User, Result.user_id == User.id_telegram).order_by(Result.total.desc(),  case((Result.first_driver > Result.second_driver, Result.first_driver), else_=Result.second_driver).desc(), Result.third_driver.desc(), Result.fourth_driver.desc(), Result.driver_team.desc(), Result.driver_engine.desc(), Result.gap.desc(), Result.lapped.desc(), Result.id)
        query = query.join(User, Result.user_id == User.id_telegram).order_by(Result.total.desc(),
                                                                              Result.counter_best.desc(),
                                                                              Result.max1_best.desc(),
                                                                              Result.max2_best.desc(),
                                                                              Result.max3_best.desc(),
                                                                              Result.max1_not_best.desc(),
                                                                              Result.max2_not_best.desc(),
                                                                              Result.max3_not_best.desc(),
                                                                              Result.max4_not_best.desc(),
                                                                              Result.counter_lap_gap.desc(),
                                                                              Result.max_lap_gap.desc(), Result.id)
        return query.all()


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
