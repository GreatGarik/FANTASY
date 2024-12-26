import platform
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String, ForeignKey
from championship2025 import gps
from drivers import drivers
from models import *
from .config_data.config import Config, load_config
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

# Определяем текущую операционную систему
current_os = platform.system()
#current_os = "Windows"


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

# Заполняем пилотов
with Session() as session:
    for driver in drivers:
        new_driver = Driver(driver_name=driver['driver'], driver_points=driver['position'], driver_team=driver['team'],
                            driver_engine=driver['engine'], engine_short=driver['position'], driver_nextgp=driver['nextGP'])
        session.add(new_driver)

    for item in gps:
        new_gp = Grandprix(gp_name=item['gp'], year=item['year'], nextgp=item['nextgp'])
        session.add(new_gp)


    session.commit()
