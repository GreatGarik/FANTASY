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
    gp = Column(Integer, ForeignKey('grandprix.id'))


# Определяем модель гран-при
class Grandprix(Base):
    __tablename__ = 'grandprix'

    id = Column(Integer, primary_key=True, index=True)
    gp_name = Column(String)
    year = Column(Integer)
    nextgp = Column(Boolean)
