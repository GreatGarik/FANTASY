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
    counter_best: Mapped[int] = mapped_column()
    max1_best: Mapped[int] = mapped_column()
    max2_best: Mapped[int] = mapped_column()
    max3_best: Mapped[int] = mapped_column()
    max1_not_best: Mapped[int] = mapped_column()
    max2_not_best: Mapped[int] = mapped_column()
    max3_not_best: Mapped[int] = mapped_column()
    max4_not_best: Mapped[int] = mapped_column()
    max_lap_gap: Mapped[int] = mapped_column()
    counter_lap_gap: Mapped[int] = mapped_column()
    penalty: Mapped[int] = mapped_column()
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
    penalty: Mapped[int] = mapped_column(Integer)
    gp: Mapped[int] = mapped_column()


# Определяем модель гран-при
class Grandprix(Base):
    __tablename__ = 'grandprix'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    gp_name: Mapped[str] = mapped_column(String)
    year: Mapped[int] = mapped_column(Integer)
    nextgp: Mapped[bool] = mapped_column(Boolean)

# Определяем модель команд
class Team(Base):
    __tablename__ = 'teams'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String)
    first: Mapped[int] = mapped_column(Integer, ForeignKey(User.id))
    second: Mapped[int] = mapped_column(Integer, ForeignKey(User.id))
    thirst: Mapped[int] = mapped_column(Integer, ForeignKey(User.id))
    logo: Mapped[str] = mapped_column(String)
    captain: Mapped[int] = mapped_column(Integer, ForeignKey(User.id))

# Определяем модель Очков
class Point(Base):
    __tablename__ = 'points'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id))
    race_id: Mapped[int] = mapped_column(ForeignKey(Grandprix.id))
    year: Mapped[int] = mapped_column(Integer)
    points: Mapped[int] = mapped_column()

