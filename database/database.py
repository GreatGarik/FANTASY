import platform
from collections import defaultdict
from typing import Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from aiogram.utils.chat_member import USERS
from certifi import where
from datetime import datetime
from sqlalchemy import create_engine, select, update, case, func, delete, asc, desc, and_, literal, or_, outerjoin, insert
from sqlalchemy.orm import sessionmaker, selectinload, aliased
from database.models import *
from config_data.config import Config, load_config
from sqlalchemy.exc import NoResultFound
'''
# Определяем текущую операционную систему
current_os = platform.system()

# Устанавливаем параметры подключения в зависимости от ОС
if current_os == "Windows":
    # Подключение к SQLite на Windows
    database_url = "sqlite:///fantasy.db"
    async_database_url = "sqlite+aiosqlite:///fantasy.db"
elif current_os == "Linux":
    # Загружаем конфиг в переменную config
    config: Config = load_config()
    # Подключение к PostgreSQL на Ubuntu
    database_url = f"postgresql://{config.tg_bot.db_user}:{config.tg_bot.db_password}@localhost:5432/{config.tg_bot.db_name}"
    async_database_url = f"postgresql+asyncpg://{config.tg_bot.db_user}:{config.tg_bot.db_password}@localhost:5432/{config.tg_bot.db_name}"
else:
    raise Exception("Unsupported operating system")
'''
# Загружаем конфиг в переменную config
config: Config = load_config()
# Подключение к PostgreSQL на Ubuntu
database_url = f"postgresql://{config.tg_bot.db_user}:{config.tg_bot.db_password}@localhost:5432/{config.tg_bot.db_name}"
async_database_url = f"postgresql+asyncpg://{config.tg_bot.db_user}:{config.tg_bot.db_password}@localhost:5432/{config.tg_bot.db_name}"

# Создаем движки
engine = create_engine(database_url, echo=False)
engine2 = create_async_engine(async_database_url, echo=False)

# Создаем сессии
Session = sessionmaker(engine)
async_session = sessionmaker(bind=engine2, class_=AsyncSession, expire_on_commit=False)


# Выбор гонщиков для прогноза со срезами по местам
async def select_drivers_async(start=0, stop=None, active=None):
    async with async_session() as session:
        async with session.begin():
            # Формируем запрос для выбора гонщиков
            if active is not None:
                statement = select(Driver).where(Driver.driver_nextgp == active).order_by(Driver.driver_position.asc())
            else:
                statement = select(Driver).order_by(Driver.driver_position.asc())

            # Выполняем запрос и получаем все результаты
            result = await session.execute(statement)
            db_object = result.scalars().all()

            # Обработка случая, когда stop равно None
            if stop is None:
                stop = len(db_object)

            # Проверка на корректность значений start и stop
            if start < 0 or stop < 0 or start >= len(db_object):
                return []  # Возвращаем пустой список, если индексы некорректны

            # Возврат среза результатов
            return db_object[start:stop]


# Выбор команд и моторов для прогноза
async def select_team_engine(pilot):
    async with async_session() as session:
        async with session.begin():
            statement = select(Driver).where(Driver.driver_name == pilot, Driver.driver_nextgp == True)
            result = await session.execute(statement)
            db_object = result.scalars().one()
            return db_object.driver_team, db_object.driver_engine


async def select_all_teams_engines():
    async with async_session() as session:
        async with session.begin():
            statement = select(Driver).where(Driver.driver_nextgp == True).order_by(Driver.driver_position)
            result = await session.execute(statement)
            drivers = result.scalars().all()

            # Создаем словарь, где ключ - имя пилота, а значение - список команда, двигатель
            teams_engines_dict = {
                driver.driver_name: [driver.driver_team, driver.driver_engine]
                for driver in drivers
            }
            return teams_engines_dict


# Запрос актуального GP
async def get_actual_gp_async():
    async with async_session() as session:
        async with session.begin():
            statement = select(Grandprix).where(Grandprix.nextgp)
            result = await session.execute(statement)
            db_object = result.scalars().one()
            return db_object.id


# Добавление юзера
async def add_user_async(user_id, name: str, lastname: str):
    """
    Добавляет пользователя, если его нет.
    Если пользователь с таким id_telegram уже существует - обновляет только имя.
    """
    async with async_session() as session:
        async with session.begin():
            full_name = f"{name} {lastname}"

            # Ищем пользователя по telegram id
            query = select(User).where(User.id_telegram == user_id)
            result = await session.execute(query)
            existing_user = result.scalar_one_or_none()

            if existing_user:
                # Обновляем только имя существующего пользователя
                existing_user.name = full_name
            else:
                # Создаем нового пользователя со значениями по умолчанию
                new_user = User(
                    id_telegram=user_id,
                    name=full_name,
                    number=None,
                    banned=False,
                    active=False,
                    can_change_name=False
                )
                session.add(new_user)




# Добавление реквеста юзера
async def add_user_request (user_id: int):
    async with async_session() as session:
        async with session.begin():
            try:
                request = Request(user_id=user_id)
                session.add(request)
                # Коммит будет выполнен автоматически при выходе из блока session.begin()
            except Exception as e:
                # Обработка исключений, если необходимо
                raise e



# Запись прогноза на гонку
async def send_predict(tg_id, gp, first_driver, second_driver, third_driver, fourth_driver, driver_team, driver_engine, gap,
                       lapped, penalty, select_duel1, select_duel2, select_duel3, time):
    async with async_session() as session:
        async with session.begin():
            try:
                new_predict = Predict(
                    user_id=tg_id,
                    first_driver=first_driver,
                    second_driver=second_driver,
                    third_driver=third_driver,
                    fourth_driver=fourth_driver,
                    driver_team=driver_team,
                    driver_engine=driver_engine,
                    gap=gap,
                    lapped=lapped,
                    gp=gp,
                    penalty=penalty,
                    time=time,
                    select_duel1=select_duel1,
                    select_duel2=select_duel2,
                    select_duel3=select_duel3
                )
                session.add(new_predict)
                await session.commit()
            except Exception as e:
                print(e)
'''
async def get_predict(gp=None):
    async with async_session() as session:
        async with session.begin():
            statement = select(Predict).where(Predict.gp == gp).order_by(asc(Predict.time))
            result = await session.execute(statement)
            db_object = result.scalars().all()
            return db_object
'''

async def get_predict(gp=None):
    async with async_session() as session:
        async with session.begin():
            # Создаем запрос с объединением таблиц Predict и User
            statement = (
                select(Predict)
                .join(User, User.id_telegram == Predict.user_id)  # Объединяем по telegram_id
                .where(Predict.gp == gp)
                .where(and_(User.banned == False, User.active == True))  # Условие, чтобы не возвращать забаненных пользователей
                .order_by(asc(Predict.time))
            )
            result = await session.execute(statement)
            db_object = result.scalars().all()
            return db_object


# Заполнение таблицы с очками по этапам
async def add_points(user_id, points, gp=None):
    async with async_session() as session:
        async with session.begin():
            try:
                team_res = await session.execute(
                    select(Team).where(
                        or_(Team.first == user_id, Team.second == user_id, Team.third == user_id)
                    ).limit(1)
                )
                team = team_res.scalars().first()
                team_id = team.id if team else None

                point_entry = Point(user_id=user_id, race_id=gp, points=points, actual_team=team_id)
                session.add(point_entry)
                await session.commit()
            except Exception as e:
                await session.rollback()
                print(e)

# Заполнение таблицы с очками по этапам - места
async def add_points_places(user_id, place, gp=None):
    async with async_session() as session:
        async with session.begin():
            try:
                # Найти существующую запись по user_id и race_id (gp)
                point_entry = await session.execute(
                    select(Point).where(Point.user_id == user_id, Point.race_id == gp)
                )
                point_entry = point_entry.scalars().first()


                point_entry.place = place
                await session.commit()

            except Exception as e:
                await session.rollback()
                raise e


async def add_team_points(team_id, points: list, place, gp=None):
    async with async_session() as session:
        async with session.begin():
            try:
                session.add(TeamPoint(team_id=team_id, race_id=gp, points=sum(points), results=points, place=place))
                await session.commit()
            except Exception as e:
                print(e)


# Заполнение таблицы результатов GP
async def add_result(tg_id, first_driver: str, second_driver: str, third_driver: str, fourth_driver: str,
                     driver_team: str, driver_engine: str, gap: int, lapped: int, select_duel1 : int, select_duel2 : int, select_duel3: int, counter_best,
                     max1_best, max2_best, max3_best, max1_not_best, max2_not_best, max3_not_best,
                     max4_not_best, counter_lap_gap, max_lap_gap, penalty, gp=None):
    total = sum(
        [first_driver, second_driver, third_driver, fourth_driver, driver_team, driver_engine, gap, lapped, select_duel1, select_duel2, select_duel3]) - (
                penalty if penalty else 0)

    async with async_session() as session:
        async with session.begin():
            try:
                result_entry = Result(user_id=tg_id, first_driver=first_driver, second_driver=second_driver,
                                      third_driver=third_driver, fourth_driver=fourth_driver, driver_team=driver_team,
                                      driver_engine=driver_engine, gap=gap, lapped=lapped, select_duel1=select_duel1, select_duel2=select_duel2, select_duel3=select_duel3,
                                      total=total,
                                      counter_best=counter_best, max1_best=max1_best, max2_best=max2_best,
                                      max3_best=max3_best, max1_not_best=max1_not_best, max2_not_best=max2_not_best,
                                      max3_not_best=max3_not_best, max4_not_best=max4_not_best,
                                      counter_lap_gap=counter_lap_gap, max_lap_gap=max_lap_gap,
                                      penalty=penalty, gp=gp)
                session.add(result_entry)
                await session.commit()
            except Exception as e:
               print(e)


# Возврат списка пользователей и их очков по GP
async def show_points_all(year):
    async with async_session() as session:
        # Получаем все гран-при
        result = await session.execute(select(Grandprix).where(Grandprix.year == year).order_by(Grandprix.id))
        grandprix = result.scalars().all()

        # Получаем всех пользователей
        result = await session.execute(select(User).where(and_(User.banned == False, User.active == True)))
        users = result.scalars().all()

        points_list = []
        for user in users:
            user_entry = {'User': user.name}
            user_entry['Number'] = user.number

            # Находим команду пользователя
            result = await session.execute(
                select(Team).where(
                    (Team.first == user.id) |
                    (Team.second == user.id) |
                    (Team.third == user.id)
                )
            )
            team = result.scalar_one_or_none()

            # Добавляем информацию о команде в user_entry
            user_entry['Team'] = team.name if team else 'PERSONAL ENTRY'

            # Инициализируем очки для каждого гран-при
            for gp in grandprix:
                # Находим очки для текущего гран-при
                result = await session.execute(
                    select(Point).where(Point.user_id == user.id, Point.race_id == gp.id)
                )
                point = result.scalar_one_or_none()
                user_entry[gp.gp_name_abr] = point.points if point else None
                user_entry['place' + gp.gp_name_abr] = point.place if point else None

            points_list.append(user_entry)

        return points_list


# Возврат списка пользователей и их очков по GP
async def show_points_team_all(year):
    async with async_session() as session:
        # Получаем все гран-при
        result = await session.execute(select(Grandprix).where(Grandprix.year == year).order_by(Grandprix.id))
        grandprix = result.scalars().all()

        # Получаем все команды
        result = await session.execute(select(Team))
        teams = result.scalars().all()

        points_list = []
        for team in teams:
            user_entry = {'Team': team.name}
            all_res = []
            # Инициализируем очки для каждого гран-при
            for gp in grandprix:
                # Находим очки для текущего гран-при
                result = await session.execute(
                    select(TeamPoint).where(TeamPoint.team_id == team.id, TeamPoint.race_id == gp.id)
                )
                point = result.scalar_one_or_none()
                user_entry[gp.gp_name_abr] = point.points if point else None
                all_res.extend(sorted(point.results, reverse=True) if point else [])
            user_entry['all_res'] = all_res

            points_list.append(user_entry)

        return points_list


# Получение результатов GP без очков чемпионата
async def get_result(gp=None):
    async with async_session() as session:
        async with session.begin():
            query = select(User, Result).where(Result.gp == gp)
            query = query.join(User, Result.user_id == User.id_telegram).order_by(
                Result.total.desc(),
                Result.counter_best.desc(),
                Result.max1_best.desc(),
                Result.max2_best.desc(),
                Result.max3_best.desc(),
                Result.max1_not_best.desc(),
                Result.max2_not_best.desc(),
                Result.max3_not_best.desc(),
                Result.max4_not_best.desc(),
                (Result.select_duel1 + Result.select_duel2 + Result.select_duel3).desc(),
                Result.counter_lap_gap.desc(),
                (Result.select_duel1 + Result.select_duel2 + Result.select_duel3 + Result.lapped).desc(),
                Result.id
            )

            result = await session.execute(query)
            return result.all()


# Получение результатов GP вместе с очками чемпионата
async def show_result(gp=None):
    async with async_session() as session:
        # Формируем основной запрос
        query = select(User, Result, Point).where(Result.gp == gp, Point.race_id == gp)

        # Добавляем соединения и порядок сортировки
        query = query.join(User, Result.user_id == User.id_telegram).order_by(
            Result.total.desc(),
            Result.counter_best.desc(),
            Result.max1_best.desc(),
            Result.max2_best.desc(),
            Result.max3_best.desc(),
            Result.max1_not_best.desc(),
            Result.max2_not_best.desc(),
            Result.max3_not_best.desc(),
            Result.max4_not_best.desc(),
            (Result.select_duel1 + Result.select_duel2 + Result.select_duel3).desc(),
            Result.counter_lap_gap.desc(),
            (Result.select_duel1 + Result.select_duel2 + Result.select_duel3 + Result.lapped).desc(),
            Result.id
        ).outerjoin(Point)

        # Выполняем запрос
        result = await session.execute(query)

        # Извлекаем результаты
        results = result.all()

        return results


# Получение пользователя по его id в телеграме или всех, если id не задан
async def get_users_async(id_telegram=None, active=True):
    async with async_session() as session:
        async with session.begin():
            if id_telegram:
                try:
                    statement = select(User).where(User.id_telegram == id_telegram)
                    result = await session.execute(statement)
                    return result.scalars().one_or_none()
                except Exception as e:
                    # Обработка исключений, если необходимо
                    return None
            else:
                if active:
                    result = await session.execute(select(User).where(and_(User.banned == False, User.active == True)))
                else:
                    result = await session.execute(select(User).where(and_(User.banned == False)))
                return result.scalars().all()


async def get_new_users_async():
    async with async_session() as session:
        async with session.begin():
            # Создаем запрос для получения всех пользователей,
            query = (
                select(User)
                .order_by(User.id)  # Упорядочиваем по id
            )
            result = await session.execute(query)
            users = result.scalars().all()  # Получаем всех пользователей

            # Если пользователей нет, возвращаем None
            if not users:
                return None

            # Возвращаем последние 10 пользователей в виде списка словарей
            last_10_users = users[-10:]  # Получаем последние 10 пользователей
            return [{'id': user.id, 'id_telegram': user.id_telegram, 'name': user.name, 'number': user.number if user.number else 'N/A'} for user in last_10_users]


async def get_users_from_requests():
    async with async_session() as session:
        async with session.begin():
            stmt = (
                select(User)
                .join(Request, Request.user_id == User.id_telegram)
                .order_by(Request.id)
            )
            res = await session.execute(stmt)
            users = res.scalars().unique().all()  # unique() на случай повторов
            if not users:
                return None
            return [
                {'id': u.id, 'id_telegram': u.id_telegram, 'name': u.name}
                for u in users
            ]

async def get_users_async_no_team():
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(User).where(User.banned == False, User.number.is_(None)))
            return result.scalars().all()



# Проверка просчитаны ли уже результаты на заданный GP
async def check_res(gp):
    async with async_session() as session:
        async with session.begin():
            statement = select(Point).where(Point.race_id == gp)
            result = await session.execute(statement)
            res = result.scalars().all()
            return bool(res)


# Просмотр команды пользователя
async def get_user_team(id_telegram):
    async with async_session() as session:
        async with session.begin():
            # Получаем пользователя
            user_stmt = select(User).where(User.id_telegram == id_telegram)
            user_result = await session.execute(user_stmt)
            user = user_result.scalars().first()

            if user:
                # Получаем команду, в которой состоит пользователь
                team_stmt = select(Team).where(
                    (Team.first == user.id) |
                    (Team.second == user.id) |
                    (Team.third == user.id)
                )
                team_result = await session.execute(team_stmt)
                team = team_result.scalars().first()

                if team:
                    return team.name

        return 'PERSONAL ENTRY'


async def get_team(id_telegram):
    async with async_session() as session:
        async with session.begin():
            # Получаем пользователя по id_telegram
            user_query = select(User).filter(User.id_telegram == id_telegram)
            user_result = await session.execute(user_query)
            user = user_result.scalars().first()

            if user:
                # Получаем команду, в которой участвует пользователь
                team_query = select(Team).filter(
                    (Team.first == user.id) |
                    (Team.second == user.id) |
                    (Team.third == user.id)
                )
                team_result = await session.execute(team_query)
                team = team_result.scalars().first()

                return team
            else:
                return None


async def is_prediced(user_id, gp):
    async with async_session() as session:
        async with session.begin():
            statement = select(Predict).where(Predict.gp == gp, Predict.user_id == user_id)
            result = await session.execute(statement)
            res = result.scalars().all()
            return bool(res)  # Возвращает True, если есть результаты, иначе False


# Добавление команды
async def add_team(user_id, name: str, new_number: str, logo: str = None, background_color: str = '000000',
                   text_color: str = 'FFFFFF', number_color: str = None, number_font: str = None,
                   number_italic: bool = False):
    async with async_session() as session:
        try:
            # Получаем пользователя по user_id
            result = await session.execute(select(User).where(User.id_telegram == user_id))
            user = result.scalars().one_or_none()

            if not user:
                raise ValueError(f"User with id_telegram {user_id} not found.")

            # Создаем новую команду
            new_team = Team(
                name=name,
                first=user.id,
                captain=user.id,
                logo=logo,
                background_color=background_color,
                text_color=text_color,
                number_color=number_color,
                number_font=number_font,
                number_italic=number_italic
            )
            session.add(new_team)

            # Обновляем номер пользователя
            user.number = int(new_number)

            # Фиксируем изменения в базе данных
            await session.commit()
        except NoResultFound:
            print(f"User with id_telegram {user_id} not found.")
        except Exception as e:
            print(f"An error occurred: {e}")
            await session.rollback()


async def get_teams_fonts_colors() -> Dict[str, Dict[str, Any]]:
    async with async_session() as session:
        teams_dict = {}
        result = await session.execute(select(Team))  # Получаем все команды из базы данных
        teams = result.scalars().all()

        for team in teams:
            teams_dict[team.name] = {
                'logo': team.logo,
                'background_color': team.background_color,
                'text_color': team.text_color,
                'number_color': team.number_color,
                'number_font': team.number_font,
                'number_italic': team.number_italic,
            }

        return teams_dict


async def clear_results(gp):
    async with async_session() as session:
        async with session.begin():
            # Удаляем строки по условию
            await session.execute(delete(Result).where(Result.gp == gp))

            await session.execute(delete(TeamPoint).where(TeamPoint.race_id == gp))

            await session.execute(delete(Point).where(Point.race_id == gp))

            await session.execute(delete(Places).where(Places.race_id == gp))

            await session.execute(delete(TeamPlaces).where(TeamPlaces.race_id == gp))


            # Сбрасываем значения max1, max2 и max3 для определенного гран-при
            await session.execute(
                update(Grandprix).where(Grandprix.id == gp).values(
                    max1=None, max2=None, max3=None
                )
            )

            await session.commit()


async def get_name_gp(gp):
    async with async_session() as session:
        async with session.begin():
            statement = select(Grandprix).where(Grandprix.id == gp)
            result = await session.execute(statement)
            res = result.scalars().first()
            return res.gp_name if res else None  # Возвращает имя gp или None, если не найдено


async def get_maximus(gp: int) -> dict:
    async with async_session() as session:
        async with session.begin():
            statement = select(Grandprix).where(Grandprix.id == gp)
            result = await session.execute(statement)
            res = result.scalars().first()

            if res:
                return {'max1': res.max1, 'max2': res.max2, 'max3': res.max3}
            else:
                return {'max1': None, 'max2': None, 'max3': None}  # или обработка случая, когда res не найден


async def add_maximus(gp, maximus):
    async with async_session() as session:
        async with session.begin():
            grandprix = await session.get(Grandprix, gp)

            if grandprix:
                # Обновляем значения
                grandprix.max1 = maximus['MAX1']
                grandprix.max2 = maximus['MAX2']
                grandprix.max3 = maximus['MAX3']
                await session.commit()


async def get_all_users():
    # Получаем всех пользователей
    async with async_session() as session:
        result = await session.execute(select(User).where(and_(User.banned == False, User.active == True)))
        users = result.scalars().all()

        # Формируем список результатов
        users_list = []

        for user in users:
            user_entry = {
                'User': user.name,
                'Number': user.number,
                'Team': 'PERSONAL ENTRY'  # Значение по умолчанию
            }

            # Находим команду пользователя
            team_query = (
                select(Team)
                .filter(
                    (Team.first == user.id) |
                    (Team.second == user.id) |
                    (Team.third == user.id)
                )
            )
            team_result = await session.execute(team_query)
            team = team_result.scalars().first()

            # Добавляем информацию о команде в user_entry
            if team:
                user_entry['Team'] = team.name

            users_list.append(user_entry)

        return users_list



async def get_users_by_name(user_name: str):
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(User).where(User.name.ilike(f'%{user_name}%')))
            users = result.scalars().all()  # Получаем всех пользователей с указанным именем

            # Если пользователей нет, возвращаем None
            if not users:
                return None

            # Возвращаем список словарей с данными пользователей
            return [{'id':user.id, 'id_telegram': user.id_telegram, 'name': user.name, 'number': user.number if user.number else 'N/A'} for user in users]


async def change_user_name_async(id_telegram: int, new_name: str):
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(User).where(User.id_telegram == id_telegram))
            user_instance = result.scalars().first()  # Получаем пользователя
            user_instance.name = new_name  # Обновляем имя напрямую
            await session.commit()  # Сохраняем изменения

async def change_user_number_async(id_telegram: int, new_number: int|None):
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(User).where(User.id_telegram == id_telegram))
            user_instance = result.scalars().first()  # Получаем пользователя
            user_instance.number = new_number  # Обновляем имя напрямую
            await session.commit()  # Сохраняем изменения


async def get_grandprix_list(year: int):
    async with async_session() as session:
        async with session.begin():
            # Выполняем асинхронный запрос для получения всех гран-при за указанный год
            result = await session.execute(select(Grandprix.id, Grandprix.gp_name).where(Grandprix.year == year).order_by(Grandprix.id))
            # Извлекаем данные из результата
            grandprix_list = result.all()
            # Преобразуем в список кортежей
            return [(gp_name, gp_id) for gp_id, gp_name in grandprix_list]

async def update_driver_positions(text: str):
    # Разделяем текст на строки и удаляем лишние пробелы
    driver_names = [name.strip() for name in text.splitlines() if name.strip()]

    async with async_session() as session:
        async with session.begin():
            # Проверяем наличие всех пилотов
            existing_drivers = await session.execute(select(Driver.driver_name))
            existing_driver_names = {driver for driver in existing_drivers.scalars().all()}

            # Находим отсутствующих водителей
            missing_drivers = set(driver_names) - existing_driver_names
            if missing_drivers:
                return f"В базе не найдены следующие пилоты: {', '.join(missing_drivers)}. Исправьте и заново откройте прогноз"


            # Проверяем наличие активных пилотов
            existing_drivers = await session.execute(select(Driver.driver_name).where(Driver.driver_nextgp.is_(True)))
            existing_driver_names = {driver for driver in existing_drivers.scalars().all()}

            # Находим отсутствующих водителей
            missing_drivers = set(driver_names) - existing_driver_names
            if missing_drivers:
                return f"Не найдены пилоты среди участников следующего этапа: {', '.join(missing_drivers)}. Исправьте и заново откройте прогноз"

            # Обновляем позиции водителей
            for position, driver_name in enumerate(driver_names, start=1):
                stmt = (
                    update(Driver)
                    .where(Driver.driver_name == driver_name)
                    .values(driver_position=position)
                )
                await session.execute(stmt)
            return 'OK'


async def update_grandprix(gp_id: int, time_start: datetime, time_penalty: datetime, time_end: datetime):
    async with async_session() as session:
        async with session.begin():
            # Получаем запись по id
            result = await session.execute(select(Grandprix).where(Grandprix.id == gp_id))
            grandprix = result.scalars().first()

            if grandprix:
                # Устанавливаем значения
                grandprix.nextgp = True
                grandprix.time_penalty = time_penalty
                grandprix.time_end = time_end
                grandprix.time_start = time_start

                await session.execute(update(Grandprix).where(Grandprix.id != gp_id).values(nextgp=False))

                # Сохраняем изменения
                await session.commit()

async def get_end_grandprix_by_id(gp_id: int):
    async with async_session() as session:
        async with session.begin():
            # Получаем запись гран-при по ID
            result = await session.execute(select(Grandprix).where(Grandprix.id == gp_id))
            grandprix = result.scalars().first()
            return grandprix.time_end

async def get_penalty_grandprix_by_id(gp_id: int):
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(Grandprix).where(Grandprix.id == gp_id))
            grandprix = result.scalars().first()
            return grandprix.time_penalty

async def get_start_grandprix_by_id(gp_id: int):
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(Grandprix).where(Grandprix.id == gp_id))
            grandprix = result.scalars().first()
            return grandprix.time_start

async def get_all_teams() -> List[Tuple[int, str]]:
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(Team.name, Team.id).order_by(Team.name))
            teams = result.all()
            return teams


async def get_all_teams_players():
    async with async_session() as session:
        async with session.begin():
            # Выполняем запрос для получения команд с участниками
            result = await session.execute(
                select(Team)
                .options(selectinload(Team.first_user), selectinload(Team.second_user), selectinload(Team.third_user))
                .order_by(Team.name)  # Сортируем команды по имени
            )

            teams = result.scalars().all()  # Получаем все команды

            # Формируем список команд с участниками
            teams_with_members = []
            for team in teams:
                members = []
                if team.first_user:
                    members.append({'name': team.first_user.name, 'number': team.first_user.number})
                if team.second_user:
                    members.append({'name': team.second_user.name, 'number': team.second_user.number})
                if team.third_user:
                    members.append({'name': team.third_user.name, 'number': team.third_user.number})

                teams_with_members.append({
                    'team_name': team.name,
                    'members': members
                })

            return teams_with_members



async def update_team(team_id: int, **kwargs):
    async with async_session() as session:
        async with session.begin():
            # Получаем команду по ID
            result = await session.execute(select(Team).where(Team.id == team_id))
            team = result.scalar_one_or_none()

            if team is None:
                raise ValueError("Team not found")

            # Обновляем только те поля, которые были переданы
            for key, value in kwargs.items():
                if hasattr(team, key):
                    setattr(team, key, value)

            # Сохраняем изменения
            await session.commit()


async def create_team_only_name(team_name: str):
    async with async_session() as session:
        async with session.begin():
            new_team = Team(
                name=team_name,
                text_color='FFFFFF',  # Устанавливаем цвет текста в белый
                logo='',  # Например, пустая строка для логотипа
                background_color='000000',  # Пустая строка для фона
                number_color='000000',  # Пустая строка для цвета номера
                number_font='000000',  # Пустая строка для шрифта номера
                number_italic=False  # По умолчанию не курсив
            )

            session.add(new_team)
            await session.commit()

async def get_team_members(team_id: int) -> list:
    async with async_session() as session:
        async with session.begin():
            # Получаем команду по ID
            team = await session.get(Team, team_id)
            keys = ['first', 'second', 'third']
            # Создаем список участников
            members = []
            for user_id, key in zip([team.first, team.second, team.third], keys):
                if user_id is not None:
                    user = await session.get(User, user_id)
                    if user:
                        members.append((user.name, key))
                else:
                    members.append(('Нет участника', key))

            return members

async def update_or_remove_team_member(team_id: int, position: str, user_id: Optional[int] = None):
    # Проверяем, что переданная позиция корректна
    if position not in ['first', 'second', 'third']:
        raise ValueError("Position must be 'first', 'second', or 'third'.")

    async with async_session() as session:
        async with session.begin():
            # Получаем команду по ID
            result = await session.execute(select(Team).where(Team.id == team_id))
            team = result.scalar_one_or_none()

            if team is None:
                raise ValueError("Team not found.")

            # Если передан user_id, заменяем участника, иначе удаляем
            if user_id is not None:
                if position == 'first':
                    team.first = user_id
                elif position == 'second':
                    team.second = user_id
                elif position == 'third':
                    team.third = user_id
            else:
                if position == 'first':
                    team.first = None
                elif position == 'second':
                    team.second = None
                elif position == 'third':
                    team.third = None

            # Сохраняем изменения в базе данных
            await session.commit()


async def update_driver_nextgp(driver_name_1: str, driver_name_2: str):
    async with async_session() as session:
        async with session.begin():
            # Находим первого гонщика
            result_1 = await session.execute(select(Driver).where(Driver.driver_name == driver_name_1))
            driver_1 = result_1.scalar_one_or_none()

            # Находим второго гонщика
            result_2 = await session.execute(select(Driver).where(Driver.driver_name == driver_name_2))
            driver_2 = result_2.scalar_one_or_none()

            # Проверяем, что оба гонщика найдены
            if driver_1 is None:
                raise ValueError(f"Driver with name '{driver_name_1}' not found.")
            if driver_2 is None:
                raise ValueError(f"Driver with name '{driver_name_2}' not found.")

            # Устанавливаем значения driver_nextgp
            driver_1.driver_nextgp = False
            driver_2.driver_nextgp = True

            # Сохраняем изменения в базе данных
            await session.commit()

async def create_f1_driver(driver_name: str, driver_team: str):
    async with async_session() as session:
        async with session.begin():
            # Получаем информацию о двигателе на основании команды
            result = await session.execute(select(Driver).where(Driver.driver_team == driver_team))
            team_driver = result.scalars().first()
            result = await session.execute(select(func.max(Driver.driver_position)))
            max_position = result.scalar_one_or_none()
            if team_driver is None:
                raise ValueError(f"No drivers found for team '{driver_team}'.")

            # Используем информацию о двигателе из первого гонщика команды
            driver_engine = team_driver.driver_engine
            engine_short = team_driver.engine_short

            # Создаем нового гонщика
            new_driver = Driver(
                driver_name=driver_name,
                driver_position=max_position + 1,
                driver_team=driver_team,
                driver_engine=driver_engine,
                engine_short=engine_short,
                driver_nextgp=False  # Устанавливаем nextgp в False
            )
            session.add(new_driver)  # Добавляем нового гонщика в сессию
            await session.commit()  # Сохраняем изменения в базе данных

async def update_driver_team(driver_name: str, new_team: str):
    async with async_session() as session:
        async with session.begin():
            # Находим гонщика по имени
            result = await session.execute(select(Driver).where(Driver.driver_name == driver_name))
            driver = result.scalar_one_or_none()

            if driver is None:
                raise ValueError(f"Driver with name '{driver_name}' not found.")

            # Получаем информацию о двигателе для новой команды
            engine_result = await session.execute(select(Driver).where(Driver.driver_team == new_team))
            new_team_driver = engine_result.scalars().first()

            if new_team_driver is None:
                raise ValueError(f"No drivers found for team '{new_team}'.")

            # Обновляем информацию о гонщике
            driver.driver_team = new_team
            driver.driver_engine = new_team_driver.driver_engine
            driver.engine_short = new_team_driver.engine_short

            # Сохраняем изменения в базе данных
            await session.commit()

async def update_grandprix_result(grandprix_id: int, result_type: str, result_text: str):
    async with async_session() as session:
        async with session.begin():
            driver_names = [name.strip() for name in result_text.splitlines() if name.strip() and not name.startswith(('bestlap:', 'gap:', 'laps:'))]
            # Проверяем наличие активных пилотов
            existing_drivers = await session.execute(select(Driver.driver_name).where(Driver.driver_nextgp.is_(True)))
            existing_driver_names = {driver for driver in existing_drivers.scalars().all()}

            # Находим отсутствующих водителей
            missing_drivers = set(name.rstrip('DNF:') for name in driver_names) - existing_driver_names
            if missing_drivers:
                return f"Не найдены пилоты среди участников этапа: {', '.join(missing_drivers)}. Введите корректные результаты"

            # Определяем, какое поле обновлять
            if result_type == 'sprint':
                column_to_update = Grandprix.sprint_result
            elif result_type == 'qualifying':
                column_to_update = Grandprix.quali_result
            elif result_type == 'race':
                column_to_update = Grandprix.race_result
            else:
                raise ValueError("Invalid result type. Choose 'sprint', 'qualifying', or 'race'.")


            stmt = update(Grandprix).where(Grandprix.id == grandprix_id).values({column_to_update: result_text})
            await session.execute(stmt)
            await session.commit()  # Фиксация изменений
            return 'OK'

async def get_grandprix_results(grandprix_id: int):
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(Grandprix).where(Grandprix.id == grandprix_id)
            )
            grandprix = result.scalars().first()  # Получаем первый результат

            if grandprix:
                return {
                    "sprint_result": grandprix.sprint_result,
                    "quali_result": grandprix.quali_result,
                    "race_result": grandprix.race_result,
                }
            else:
                return None  # Если гонка не найдена

async def get_predictions_by_gp(gp_id: int):
    async with async_session() as session:
        async with session.begin():
            # Выполняем запрос с объединением таблиц
            stmt = (
                select(Predict, User)
                .join(User, User.id_telegram == Predict.user_id)
                .where(Predict.gp == gp_id)
                .order_by(asc(Predict.time))
            )
            result = await session.execute(stmt)
            predictions = result.all()

            # Формируем список результатов
            predictions_list = [
                {
                    "id_telegram": user.id_telegram,  # Используем id_telegram из объекта User
                    "user": user.name,  # Здесь добавляем имя пользователя
                    "first_driver": pred.first_driver,
                    "second_driver": pred.second_driver,
                    "third_driver": pred.third_driver,
                    "fourth_driver": pred.fourth_driver,
                    "driver_team": pred.driver_team,
                    "driver_engine": pred.driver_engine,
                    "select_duel1": pred.select_duel1,
                    "select_duel2": pred.select_duel2,
                    "select_duel3": pred.select_duel3,
                    #"gap": pred.gap,
                    "lapped": pred.lapped,
                    "penalty": pred.penalty,
                    "time": pred.time,
                }
                for pred, user in predictions
            ]

            return predictions_list


async def is_sprint(gp_id: int) -> bool:
    async with async_session() as session:  # Открываем сессию
        async with session.begin():  # Начинаем транзакцию
            result = await session.execute(select(Grandprix).where(Grandprix.id == gp_id))
            grandprix = result.scalars().first()
            return grandprix.sprint if grandprix else False



async def change_user_banned_status(id_telegram: int, banned: bool):
    async with async_session() as session:
        async with session.begin():
            # Обновляем статус banned для указанного пользователя
            stmt = update(User).where(User.id_telegram == id_telegram).values(banned=banned)
            await session.execute(stmt)
            await session.commit()


async def approving_the_request(id_telegram: int, approve: bool):
    async with async_session() as session:
        async with session.begin():
            # Обновляем поле active у пользователя
            stmt = update(User).where(User.id_telegram == id_telegram).values(active=approve)
            await session.execute(stmt)

            # Находим id пользователя и удаляем его заявки по FK Request.user_id
            del_stmt = delete(Request).where(Request.user_id == id_telegram)
            await session.execute(del_stmt)

async def can_change_name(id_telegram: int, can_change: bool):
    async with async_session() as session:
        async with session.begin():
            # Обновляем поле active у пользователя
            stmt = update(User).where(User.id_telegram == id_telegram).values(can_change_name=can_change)
            await session.execute(stmt)

async def is_user_banned(id_telegram: int) -> bool:
    async with async_session() as session:
        async with session.begin():
            statement = select(User).where(User.id_telegram == id_telegram)
            result = await session.execute(statement)
            user = result.scalars().first()
            return user.banned if user else False

async def is_user_active(id_telegram: int) -> bool:
    async with async_session() as session:
        async with session.begin():
            statement = select(User).where(User.id_telegram == id_telegram)
            result = await session.execute(statement)
            user = result.scalars().first()
            return user.active if user else False


async def is_can_change_name(id_telegram: int) -> bool:
    async with async_session() as session:
        async with session.begin():
            statement = select(User).where(User.id_telegram == id_telegram)
            result = await session.execute(statement)
            user = result.scalars().first()
            return user.can_change_name if user else False

async def is_user_in_request(id_telegram: int) -> bool:
    async with async_session() as session:
        async with session.begin():
            statement = select(Request).where(Request.user_id == id_telegram)
            result = await session.execute(statement)
            user = result.scalars().first()
            return True if user else False


async def delete_team_from_db(team_id: int):
    async with async_session() as session:
        async with session.begin():
            # Создаем запрос на удаление команды с указанным id
            await session.execute(delete(TeamPoint).where(TeamPoint.team_id == team_id))

            stmt = delete(Team).where(Team.id == team_id)

            # Выполняем запрос
            await session.execute(stmt)

            # Сохраняем изменения в базе данных
            await session.commit()

# Шедулер
async def delete_old_scheduled_messages():
    async with async_session() as session:
        async with session.begin():
            now = datetime.now()
            await session.execute(delete(ScheduledMessage).where(ScheduledMessage.send_time < now))
            await session.commit()

async def get_scheduled_messages():
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(ScheduledMessage))
            return result.scalars().all()

async def add_scheduled_message(chat_id: int, text: str, send_time: datetime):
    async with async_session() as session:
        async with session.begin():
            message = ScheduledMessage(chat_id=chat_id, text=text, send_time=send_time)
            session.add(message)
            await session.commit()

async def add_duel(participant1: str, participant2: str, num: int, gp: int):
    async with async_session() as session:
        async with session.begin():
            new_duel = Duel(participant1=participant1, participant2=participant2, num=num, gp=gp)
            session.add(new_duel)
            await session.commit()

async def delete_duels_by_gp(gp_value: int):
    async with async_session() as session:               # async_session — ваша фабрика сессий
        async with session.begin():
            stmt = delete(Duel).where(Duel.gp == gp_value)
            await session.execute(stmt)
            await session.commit()

async def get_duel_pair(num_value: Optional[int] = None, gp_value: int = None) -> List[List[str]] | List[str]:
    async with async_session() as session:
        async with session.begin():
            if num_value is None:
                stmt = select(Duel.participant1, Duel.participant2).where(Duel.gp == gp_value)
                result = await session.execute(stmt)
                return [[row.participant1, row.participant2] for row in result.fetchall()]
            else:
                stmt = select(Duel.participant1, Duel.participant2).where(
                    Duel.num == num_value,
                    Duel.gp == gp_value
                )
                result = await session.execute(stmt)
                row = result.first()
                return [row.participant1, row.participant2]



async def get_user_places_by_year(year):
    async with async_session() as session:
        async with session.begin():
            TeamFirst = aliased(Team)
            TeamSecond = aliased(Team)
            TeamThird = aliased(Team)

            stmt = (
                select(
                    User,
                    Point.place,
                    func.coalesce(TeamFirst.name, TeamSecond.name, TeamThird.name, literal('')).label('team_name')
                )
                .join(Point, Point.user_id == User.id)
                .join(Grandprix, Grandprix.id == Point.race_id)
                .outerjoin(TeamFirst, TeamFirst.first == User.id)
                .outerjoin(TeamSecond, TeamSecond.second == User.id)
                .outerjoin(TeamThird, TeamThird.third == User.id)
                .where(Grandprix.year == year)
            )

            result = await session.execute(stmt)
            rows = result.all()
            return [(row[0], row[1], row[2] if row[2] else 'PERSONAL ENTRY') for row in rows]


async def counts_selects(year: Optional[int] = None):
    async with async_session() as session:
        async with session.begin():
            # Список уникальных значений из drivers
            drivers = [r.driver_name for r in (await session.execute(select(Driver.driver_name).distinct())).fetchall()]
            teams = [r.driver_team for r in (await session.execute(select(Driver.driver_team).distinct())).fetchall()]
            engines = [r.driver_engine for r in (await session.execute(select(Driver.driver_engine).distinct())).fetchall()]

            # Подготовка year фильтра (Predict.gp IN (SELECT id FROM grandprix WHERE year = :year))
            if year is not None:
                gp_subq = select(Grandprix.id).where(Grandprix.year == year)
            else:
                gp_subq = None

            # Общее число прогнозов (с учётом фильтра по году)
            if gp_subq is not None:
                total_q = select(func.count()).select_from(Predict).where(Predict.gp.in_(gp_subq))
            else:
                total_q = select(func.count()).select_from(Predict)
            total_predicts = int((await session.execute(total_q)).scalar_one())

            drivers_counts = []
            for name in drivers:
                if name is None:
                    continue
                where_clause = (
                    (Predict.first_driver == name) |
                    (Predict.second_driver == name) |
                    (Predict.third_driver == name) |
                    (Predict.fourth_driver == name)
                )
                if gp_subq is not None:
                    where_clause = and_(where_clause, Predict.gp.in_(gp_subq))
                cnt_q = select(func.count()).select_from(Predict).where(where_clause)
                cnt = (await session.execute(cnt_q)).scalar_one()
                drivers_counts.append((name, int(cnt)))

            teams_counts = []
            for team in teams:
                if team is None:
                    continue
                where_clause = (Predict.driver_team == team)
                if gp_subq is not None:
                    where_clause = and_(where_clause, Predict.gp.in_(gp_subq))
                cnt_q = select(func.count()).select_from(Predict).where(where_clause)
                cnt = (await session.execute(cnt_q)).scalar_one()
                teams_counts.append((team, int(cnt)))

            engines_counts = []
            for eng in engines:
                if eng is None:
                    continue
                where_clause = (Predict.driver_engine == eng)
                if gp_subq is not None:
                    where_clause = and_(where_clause, Predict.gp.in_(gp_subq))
                cnt_q = select(func.count()).select_from(Predict).where(where_clause)
                cnt = (await session.execute(cnt_q)).scalar_one()
                engines_counts.append((eng, int(cnt)))

    return {
        "total_predicts": total_predicts,
        "drivers": drivers_counts,
        "teams": teams_counts,
        "engines": engines_counts
    }

async def get_team_places_by_name(year: int) -> Dict[str, List[int]]:
    """
    Асинхронно возвращает словарь {team_name: [place, ...]} только для Grandprix.year == year.
    Points с actual_team == None попадают в ключ "PERSONAL ENTRIES".
    """
    async with async_session() as session:
        async with session.begin():
            team_alias = Team
            gp_alias = Grandprix

            stmt = (
                select(Point.place, team_alias.name)
                .select_from(
                    outerjoin(
                        outerjoin(Point, team_alias, team_alias.id == Point.actual_team),
                        gp_alias,
                        gp_alias.id == Point.race_id
                    )
                )
                .where(gp_alias.year == year)
            )

            result = defaultdict(list)
            rows = (await session.execute(stmt)).all()
            for place, team_name in rows:
                key = team_name if team_name is not None else "PERSONAL ENTRIES"
                result[key].append(place)

            return dict(result)


async def add_places_after_gp(points_list: list[dict], gp: int):
    async with async_session() as session:
        async with session.begin():
            # Проверка: есть ли хоть одна запись с таким gp (race_id)
            exists_stmt = select(Places.id).where(Places.race_id == gp).limit(1)
            exists_res = await session.execute(exists_stmt)
            if exists_res.scalar_one_or_none() is not None:
                # Если есть запись — ничего не писать
                return

            # Собираем словари для вставки
            rows = []
            for place_val, person in enumerate(points_list, start=1):
                name = person.get('User')

                # ищем user.id через экземпляр сессии
                stmt = select(User.id).where(User.name == name)
                res = await session.execute(stmt)
                user_id = res.scalar_one_or_none()
                if user_id is None:
                    continue

                rows.append({
                    "user_id": int(user_id),
                    "race_id": gp,
                    "place": int(place_val),
                })

            if rows:
                await session.execute(insert(Places), rows)


async def add_places_after_gp_teams(points_list: list[dict], gp: int):
    async with async_session() as session:
        async with session.begin():
            # Проверка: есть ли хоть одна запись с таким gp (race_id)
            exists_stmt = select(TeamPlaces.id).where(TeamPlaces.race_id == gp).limit(1)
            exists_res = await session.execute(exists_stmt)
            if exists_res.scalar_one_or_none() is not None:
                # Если есть запись — ничего не писать
                return

            # Собираем словари для вставки
            rows = []
            for place_val, person in enumerate(points_list, start=1):
                team = person.get('Team')

                # ищем team.id через экземпляр сессии
                stmt = select(Team.id).where(Team.name == team)
                res = await session.execute(stmt)
                team_id = res.scalar_one_or_none()
                if team_id is None:
                    continue

                rows.append({
                    "team_id": int(team_id),
                    "race_id": gp,
                    "place": int(place_val),
                })

            if rows:
                await session.execute(insert(TeamPlaces), rows)

async def show_places_all(year):
    async with async_session() as session:
        result = await session.execute(select(Grandprix).where(Grandprix.year == year).order_by(Grandprix.id))
        grandprix = result.scalars().all()

        result = await session.execute(select(User).where(and_(User.banned == False, User.active == True)))
        users = result.scalars().all()

        places_list = []
        for user in users:
            user_entry = {'User': user.name}
            user_entry['Number'] = user.number

            result = await session.execute(
                select(Team).where(
                    (Team.first == user.id) |
                    (Team.second == user.id) |
                    (Team.third == user.id)
                )
            )
            team = result.scalar_one_or_none()
            user_entry['Team'] = team.name if team else 'PERSONAL ENTRY'

            for gp in grandprix:
                result = await session.execute(
                    select(Point).where(Point.user_id == user.id, Point.race_id == gp.id)
                )
                point = result.scalar_one_or_none()
                # Сохраняем место вместо очков
                user_entry[gp.gp_name_abr] = point.place if point else None
                user_entry['place' + gp.gp_name_abr] = point.place if point else None

            places_list.append(user_entry)

        return places_list

# Возврат списка команд и их мест по GP
async def show_places_team_all(year):
    async with async_session() as session:
        result = await session.execute(select(Grandprix).where(Grandprix.year == year).order_by(Grandprix.id))
        grandprix = result.scalars().all()

        result = await session.execute(select(Team))
        teams = result.scalars().all()

        places_list = []
        for team in teams:
            team_entry = {'Team': team.name}
            all_res = []
            for gp in grandprix:
                # Находим запись места для команды в данном GP
                result = await session.execute(
                    select(TeamPlaces).where(TeamPlaces.team_id == team.id, TeamPlaces.race_id == gp.id)
                )
                tp = result.scalar_one_or_none()
                team_entry[gp.gp_name_abr] = tp.place if tp else None
                if tp and tp.place is not None:
                    all_res.append(tp.place)
            team_entry['all_res'] = all_res
            places_list.append(team_entry)

        return places_list

async def count_top3_finishes_by_team(year: int) -> List[Dict[str, Any]]:
    """
    Возвращает список dict:
      {'team_id': int, 'Team': str, 'wins': int, 'seconds': int, 'thirds': int, 'total': int}
    для всех команд, у которых есть записи в team_points за указанный year.
    """
    async with async_session() as session:
        # получить этапы за год
        gps_stmt = select(Grandprix.id).where(Grandprix.year == year)
        gps_res = await session.execute(gps_stmt)
        gp_ids = [row[0] for row in gps_res.all()]
        if not gp_ids:
            return []

        # получить team_points для этих этапов
        tp_stmt = select(TeamPoint.team_id, TeamPoint.place).where(TeamPoint.race_id.in_(gp_ids))
        tp_res = await session.execute(tp_stmt)
        rows = tp_res.all()  # список кортежей (team_id, place)

        if not rows:
            return []

        counts: Dict[int, Dict[str, int]] = defaultdict(lambda: {'wins': 0, 'seconds': 0, 'thirds': 0, 'total': 0})
        for team_id, place in rows:
            if place is None:
                continue
            counts[team_id]['total'] += 1
            if place == 1:
                counts[team_id]['wins'] += 1
            elif place == 2:
                counts[team_id]['seconds'] += 1
            elif place == 3:
                counts[team_id]['thirds'] += 1

        # получить имена команд
        team_ids = list(counts.keys())
        team_stmt = select(Team.id, Team.name).where(Team.id.in_(team_ids))
        team_res = await session.execute(team_stmt)
        team_map = {tid: name for tid, name in team_res.all()}

        # собрать результат
        result: List[Dict[str, Any]] = []
        for tid, vals in counts.items():
            result.append({
                'team_id': tid,
                'Team': team_map.get(tid, str(tid)),
                'wins': vals['wins'],
                'seconds': vals['seconds'],
                'thirds': vals['thirds'],
                'total': vals['total'],
            })

        return result


async def show_places_team_from_team_points(year: int) -> List[Dict]:
    """
    Возвращает список dict-ов вида:
    {
        'Team': team_name,
        'gp_<abbr_or_id>': place_or_none,
        ...
    }
    где ключи этапов в том же порядке, что и gp_keys в основной функции (abbreviation если доступно).
    """
    async with async_session() as session:
        gp_q = await session.execute(select(Grandprix).where(Grandprix.year == year).order_by(Grandprix.id))
        gps = gp_q.scalars().all()

        gp_keys = []
        gp_id_to_key = {}
        for gp in gps:
            key = gp.gp_name_abr or f'gp_{gp.id}'
            gp_keys.append(key)
            gp_id_to_key[gp.id] = key

        # Получаем все команды
        teams_q = await session.execute(select(Team).order_by(Team.name))
        teams = teams_q.scalars().all()

        result = []
        for team in teams:
            row = {'Team': team.name}
            for k in gp_keys:
                row[k] = None

            tp_q = await session.execute(
                select(TeamPoint).where(TeamPoint.team_id == team.id, TeamPoint.race_id.in_(list(gp_id_to_key.keys())))
            )
            tps = tp_q.scalars().all()
            for tp in tps:
                key = gp_id_to_key.get(tp.race_id)
                if key:
                    row[key] = tp.place
            result.append(row)
    return result


async def get_places_from_points(year: int) -> List[dict]:
    """
    Получает места пользователей из таблицы points за указанный год

    Returns:
        List[dict] - список словарей в формате:
        {
            'User': имя пользователя,
            'Team': название команды,
            'Number': номер пользователя,
            'GP_abbreviation': место_в_гонке,
            # ... для всех гонок года
        }
    """
    async with async_session() as session:
        # Получаем все гонки за указанный год, сортируем по id (самый надежный)
        gp_query = (
            select(Grandprix)
            .where(Grandprix.year == year)
            .order_by(asc(Grandprix.id))  # Сортируем по id
        )
        gp_result = await session.execute(gp_query)
        grand_prixes = gp_result.scalars().all()

        if not grand_prixes:
            return []

        # Получаем всех пользователей
        users_query = (
            select(User)
            .options(selectinload(User.points))
        )
        users_result = await session.execute(users_query)
        users = users_result.scalars().all()

        # Создаем мапу gp_id -> аббревиатура для ключей
        # Используем gp_name_abr (3-буквенная аббревиатура)
        gp_map = {gp.id: gp.gp_name_abr for gp in grand_prixes}

        # Собираем результат
        result = []

        for user in users:
            # Базовые данные пользователя
            # Проверяем, какие поля есть в модели User
            user_name = getattr(user, 'name', getattr(user, 'username', ''))
            user_team = getattr(user, 'team', '')
            user_number = getattr(user, 'number', '')

            user_data = {
                'User': user_name,
                'Team': user_team,
                'Number': user_number,
            }

            # Добавляем поля для каждой гонки
            for gp in grand_prixes:
                user_data[gp.gp_name_abr] = None  # По умолчанию пусто

            # Заполняем места из таблицы points
            for point in user.points:
                if point.race_id in gp_map:
                    gp_key = gp_map[point.race_id]
                    # Сохраняем место (place) из модели Point
                    user_data[gp_key] = point.place

            result.append(user_data)

        return result