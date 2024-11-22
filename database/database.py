from aiogram.utils.chat_member import USERS
from certifi import where
from sqlalchemy import create_engine, select, update, case
from sqlalchemy.orm import Session, sessionmaker
from database.models import *

# Подключаемся к базе данных
engine = create_engine("sqlite:///fantasy.db", echo=False)

# Создаем сессию
Session = sessionmaker(engine)

# Выбор гонщиков для прогноза со срезами по местам
def select_drivers(start=None, stop=None):
    with Session() as session:
        statement = select(Driver).where(Driver.driver_nextgp == 'Y').order_by(Driver.driver_points.desc())
        db_object = session.scalars(statement).all()
        return db_object[start:stop]

# Выбор команд и моторов для прогноза
def select_team_engine(pilot):
    with Session() as session:
        statement = select(Driver).where(Driver.driver_name == pilot, Driver.driver_nextgp == 'Y')
        db_object = session.scalars(statement).one()
        return db_object.driver_team, db_object.driver_engine

# Запрос актуального GP
def get_actual_gp():
    with Session() as session:
        statement = select(Grandprix).where(Grandprix.nextgp)
        db_object = session.scalars(statement).one()
        return db_object.id

# Добавление юзера
def add_user(user_id, name: str, lastname: str):
    with Session() as session:
        try:
            session.add(User(name=name + ' ' + lastname, id_telegram=user_id))
            session.commit()
        except:
            pass

# Запись прогноза на гонку
def send_predict(tg_id, gp, first_driver, second_driver, third_driver, fourth_driver, driver_team, driver_engine, gap,
                 lapped, penalty):
    with Session() as session:
        try:
            session.add(Predict(user_id=tg_id, first_driver=first_driver, second_driver=second_driver,
                                third_driver=third_driver, fourth_driver=fourth_driver, driver_team=driver_team,
                                driver_engine=driver_engine, gap=gap, lapped=lapped, gp=gp, penalty=penalty))
            session.commit()
        except Exception as e:
            print(e)

# Получение прогноза на гонку
def get_predict(gp=None):
    with Session() as session:
        statement = select(Predict).where(Predict.gp == gp)
        db_object = session.scalars(statement).all()
        return db_object

# Заполнение таблицы с очками по этапам
def add_points(user_id, year, points, gp=None):
    with Session() as session:
        try:
            session.add(Point(user_id=user_id, race_id=gp, year=year, points=points))
            session.commit()
        except Exception as e:
            print(e)

# Заполнение таблицы результатов GP
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

# Возврат списка мз пользователей и их очков
def show_points():
    with Session() as session:
        result = session.query(User).outerjoin(Point).all()
        points_list = [
            {
                'User': user.name,
                **{point.race_id: point.points for point in user.points}
            }
            for user in result
        ]
        return points_list

# Возврат списка пользователей и их очков по GP
def show_points_all(year):
    with Session() as session:
        # Получаем все гран-при 2024 года
        grandprix = session.query(Grandprix).filter(Grandprix.year == year).all()

        # Получаем всех пользователей
        users = session.query(User).all()

        # Формируем список результатов
        points_list = []

        for user in users:
            user_entry = {'User': user.name}
            # Инициализируем очки для каждого гран-при 2024 года
            for gp in grandprix:
                # Находим очки для текущего гран-при
                points = next((point.points for point in user.points if point.race_id == gp.id), 0)
                user_entry[gp.gp_name_abr] = points
            points_list.append(user_entry)

        return points_list

# Получение результатов GP без очков чемпионата
def get_result(gp=None):
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
                                                                              Result.max_lap_gap.desc(),
                                                                              Result.id).all()

        return query

# Получение результатов GP вместе с очками чемпионата
def show_result(gp=None):
    with Session() as session:
        query = session.query(User, Result, Point).where(Result.gp == gp, Point.race_id == gp)
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
                                                                              Result.max_lap_gap.desc(),
                                                                              Result.id).outerjoin(Point).all()

        return query

# Получение пользователя по его id в телеграме или всех, если id не задан
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


# Проверка просчитаны ли уже результаты на заданный GP
def check_res(gp):
    with Session() as session:
        statement = select(Point).where(Point.race_id == gp)
        res = session.scalars(statement).all()
        if res:
            return True
        else:
            return

# Просмотр команды пользователя
def get_user_team(id_telegram):
    with Session() as session:
        user = session.query(User).filter(User.id_telegram == id_telegram).first()
        team = session.query(Team).filter(
                (Team.first == user.id) |
                (Team.second == user.id) |
                (Team.third == user.id)
            ).first()
        if team:
            return team.name
        else:
            return 'PERSONAL ENTRY'

def is_prediced(user_id, gp):
    with Session() as session:
        statement = select(Predict).where(Predict.gp == gp, Predict.user_id == user_id)
        res = session.scalars(statement).all()
        if res:
            return True
        else:
            return


# Добавление команды
def add_team(user_id, name: str, number: int, captain: bool):
    with Session() as session:
        user = session.scalars(select(User).where(User.id_telegram == user_id)).one().id
        try:
            session.add(Team(name=name, first=user, number=number, captain=captain))
            session.commit()
        except Exception as e:
            print(e)
