import platform
from typing import Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from aiogram.utils.chat_member import USERS
from certifi import where
from datetime import datetime
from sqlalchemy import create_engine, select, update, case, func, delete, asc
from sqlalchemy.orm import sessionmaker
from database.models import *
from config_data.config import Config, load_config
from sqlalchemy.exc import NoResultFound

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
            statement = select(Driver).where(Driver.driver_nextgp == True)
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
    async with async_session() as session:
        async with session.begin():
            try:
                user = User(name=name + ' ' + lastname, id_telegram=user_id)
                session.add(user)
                # Коммит будет выполнен автоматически при выходе из блока session.begin()
            except Exception as e:
                # Обработка исключений, если необходимо
                raise e


# Запись прогноза на гонку
async def send_predict(tg_id, gp, first_driver, second_driver, third_driver, fourth_driver, driver_team, driver_engine, gap,
                       lapped, penalty, time):
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
                    time=time
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
                .where(User.banned == False)  # Условие, чтобы не возвращать забаненных пользователей
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
                point_entry = Point(user_id=user_id, race_id=gp, points=points)
                session.add(point_entry)
                await session.commit()
            except Exception as e:
                print(e)



async def add_team_points(team_id, points, gp=None):
    async with async_session() as session:
        async with session.begin():
            try:
                session.add(TeamPoint(team_id=team_id, race_id=gp, points=points))
                await session.commit()
            except Exception as e:
                print(e)


# Заполнение таблицы результатов GP
async def add_result(tg_id, first_driver: str, second_driver: str, third_driver: str, fourth_driver: str,
                     driver_team: str, driver_engine: str, gap: int, lapped: int, counter_best,
                     max1_best, max2_best, max3_best, max1_not_best, max2_not_best, max3_not_best,
                     max4_not_best, counter_lap_gap, max_lap_gap, penalty, gp=None):
    total = sum(
        [first_driver, second_driver, third_driver, fourth_driver, driver_team, driver_engine, gap, lapped]) - (
                penalty if penalty else 0)

    async with async_session() as session:
        async with session.begin():
            try:
                result_entry = Result(user_id=tg_id, first_driver=first_driver, second_driver=second_driver,
                                      third_driver=third_driver, fourth_driver=fourth_driver, driver_team=driver_team,
                                      driver_engine=driver_engine, gap=gap, lapped=lapped, total=total,
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
        result = await session.execute(select(User).where(User.banned == False))
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

            # Инициализируем очки для каждого гран-при
            for gp in grandprix:
                # Находим очки для текущего гран-при
                result = await session.execute(
                    select(TeamPoint).where(TeamPoint.team_id == team.id, TeamPoint.race_id == gp.id)
                )
                point = result.scalar_one_or_none()
                user_entry[gp.gp_name_abr] = point.points if point else None

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
                Result.counter_lap_gap.desc(),
                Result.max_lap_gap.desc(),
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
            Result.counter_lap_gap.desc(),
            Result.max_lap_gap.desc(),
            Result.id
        ).outerjoin(Point)

        # Выполняем запрос
        result = await session.execute(query)

        # Извлекаем результаты
        results = result.all()

        return results


# Получение пользователя по его id в телеграме или всех, если id не задан
async def get_users_async(id_telegram=None):
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
                result = await session.execute(select(User).where(User.banned == False))
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
        result = await session.execute(select(User).where(User.banned == False))
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
                text_color='#FFFFFF',  # Устанавливаем цвет текста в белый
                logo='',  # Например, пустая строка для логотипа
                background_color='',  # Пустая строка для фона
                number_color='',  # Пустая строка для цвета номера
                number_font='',  # Пустая строка для шрифта номера
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
            driver_names = [name.strip() for name in result_text.splitlines() if name.strip()]
            # Проверяем наличие активных пилотов
            existing_drivers = await session.execute(select(Driver.driver_name).where(Driver.driver_nextgp.is_(True)))
            existing_driver_names = {driver for driver in existing_drivers.scalars().all()}

            # Находим отсутствующих водителей
            missing_drivers = set(driver_names) - existing_driver_names
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
                    "gap": pred.gap,
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

async def is_user_banned(id_telegram: int) -> bool:
    async with async_session() as session:
        async with session.begin():
            statement = select(User).where(User.id_telegram == id_telegram)
            result = await session.execute(statement)
            user = result.scalars().first()
            return user.banned if user else False