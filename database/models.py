from typing import Optional
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


# Создаем базовый класс для моделей
class Base(DeclarativeBase):
    pass


# Определяем модель пользователей
class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    id_telegram: Mapped[int] = mapped_column(unique=True)
    vk_link: Mapped[str] = mapped_column(String(60))
    name: Mapped[str] = mapped_column(String(60))
    user_team: Mapped[Optional[str]] = mapped_column(String(60))


# Определяем модель гонщиков
class Driver(Base):
    __tablename__ = 'drivers'

    id: Mapped[int] = mapped_column(primary_key=True)
    driver_name: Mapped[str] = mapped_column(String(60))
    driver_points: Mapped[int] = mapped_column()
    driver_team: Mapped[str] = mapped_column(String(60))
    driver_engine: Mapped[str] = mapped_column(String(60))
    driver_nextgp: Mapped[str] = mapped_column(String(1))

# Определяем модель гонщиков
class Result(Base):
    __tablename__ = 'results'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column()
    first_driver: Mapped[int] = mapped_column()
    second_driver: Mapped[int] = mapped_column()
    third_driver: Mapped[int] = mapped_column()
    fourth_driver: Mapped[int] = mapped_column()
    driver_team: Mapped[int] = mapped_column()
    driver_engine: Mapped[int] = mapped_column()
    gap: Mapped[int] = mapped_column()
    lapped: Mapped[int] = mapped_column()
    total: Mapped[int] = mapped_column()
    gp: Mapped[int] = mapped_column()


# Определяем модель прогнозов
class Predict(Base):
    __tablename__ = 'predicts'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column()
    first_driver: Mapped[str] = mapped_column(String)
    second_driver: Mapped[str] = mapped_column(String)
    third_driver: Mapped[str] = mapped_column(String)
    fourth_driver: Mapped[str] = mapped_column(String)
    driver_team: Mapped[str] = mapped_column(String)
    driver_engine: Mapped[str] = mapped_column(String)
    gap: Mapped[int] = mapped_column(Integer)
    lapped: Mapped[int] = mapped_column(Integer)
    gp: Mapped[int] = mapped_column()


# Определяем модель гран-при
class Grandprix(Base):
    __tablename__ = 'grandprix'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    gp_name: Mapped[str] = mapped_column(String)
    year: Mapped[int] = mapped_column(Integer)
    nextgp: Mapped[bool] = mapped_column(Boolean)

class ResultsGp(Base):
    __tablename__ = 'resultsgp'

    id: Mapped[int] = mapped_column(primary_key=True)
    event: Mapped[str] = mapped_column(String(12))
    first: Mapped[int] = mapped_column()
    second: Mapped[int] = mapped_column()
    third: Mapped[int] = mapped_column()
    fourth: Mapped[int] = mapped_column()
    fifth: Mapped[int] = mapped_column()
    sixth: Mapped[int] = mapped_column()
    seventh: Mapped[int] = mapped_column()
    eighth: Mapped[int] = mapped_column()
    ninth: Mapped[int] = mapped_column()
    tenth: Mapped[int] = mapped_column()
    eleventh: Mapped[int] = mapped_column()
    twelfth: Mapped[int] = mapped_column()
    thirteenth: Mapped[int] = mapped_column()
    fourteenth: Mapped[int] = mapped_column()
    fifteenth: Mapped[int] = mapped_column()
    sixteenth: Mapped[int] = mapped_column()
    seventeenth: Mapped[int] = mapped_column()
    eighteenth: Mapped[int] = mapped_column()
    nineteenth: Mapped[int] = mapped_column()
    twentieth: Mapped[int] = mapped_column()
    gap: Mapped[int] = mapped_column()
    lapped: Mapped[int] = mapped_column()
    gp: Mapped[int] = mapped_column()
