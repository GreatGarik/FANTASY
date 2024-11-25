from typing import Optional, List
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


# Создаем базовый класс для моделей
class Base(DeclarativeBase):
    pass


# Определяем модель пользователей
class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_telegram: Mapped[int] = mapped_column(Integer, unique=True)
    name: Mapped[str] = mapped_column(String(60))
    number: Mapped[int] = mapped_column(Integer, unique=True)
    #team: Mapped[int] = mapped_column(Integer, ForeignKey('teams.id'))

    points: Mapped[List['Point']] = relationship('Point', back_populates='user')
    # Связи с командами
    teams_first: Mapped[List['Team']] = relationship('Team', back_populates='first_user', foreign_keys='Team.first')
    teams_second: Mapped[List['Team']] = relationship('Team', back_populates='second_user', foreign_keys='Team.second')
    teams_third: Mapped[List['Team']] = relationship('Team', back_populates='third_user', foreign_keys='Team.third')


# Определяем модель гонщиков
class Driver(Base):
    __tablename__ = 'drivers'

    id: Mapped[int] = mapped_column(primary_key=True)
    driver_name: Mapped[str] = mapped_column(String(60))
    driver_points: Mapped[int] = mapped_column(Integer)
    driver_team: Mapped[str] = mapped_column(String(60))
    driver_engine: Mapped[str] = mapped_column(String(60))
    engine_short: Mapped[str] = mapped_column(String(3))
    driver_nextgp: Mapped[str] = mapped_column(String(1))




# Определяем модель гонщиков
class Result(Base):
    __tablename__ = 'results'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer)
    first_driver: Mapped[int] = mapped_column(Integer)
    second_driver: Mapped[int] = mapped_column(Integer)
    third_driver: Mapped[int] = mapped_column(Integer)
    fourth_driver: Mapped[int] = mapped_column(Integer)
    driver_team: Mapped[int] = mapped_column(Integer)
    driver_engine: Mapped[int] = mapped_column(Integer)
    gap: Mapped[int] = mapped_column(Integer)
    lapped: Mapped[int] = mapped_column(Integer)
    total: Mapped[int] = mapped_column(Integer)
    counter_best: Mapped[int] = mapped_column(Integer)
    max1_best: Mapped[int] = mapped_column(Integer)
    max2_best: Mapped[int] = mapped_column(Integer)
    max3_best: Mapped[int] = mapped_column(Integer)
    max1_not_best: Mapped[int] = mapped_column(Integer)
    max2_not_best: Mapped[int] = mapped_column(Integer)
    max3_not_best: Mapped[int] = mapped_column(Integer)
    max4_not_best: Mapped[int] = mapped_column(Integer)
    max_lap_gap: Mapped[int] = mapped_column(Integer)
    counter_lap_gap: Mapped[int] = mapped_column(Integer)
    penalty: Mapped[int] = mapped_column(Integer)
    gp: Mapped[int] = mapped_column(Integer)



# Определяем модель прогнозов
class Predict(Base):
    __tablename__ = 'predicts'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer)
    first_driver: Mapped[str] = mapped_column(String)
    second_driver: Mapped[str] = mapped_column(String)
    third_driver: Mapped[str] = mapped_column(String)
    fourth_driver: Mapped[str] = mapped_column(String)
    driver_team: Mapped[str] = mapped_column(String)
    driver_engine: Mapped[str] = mapped_column(String)
    gap: Mapped[int] = mapped_column(Integer)
    lapped: Mapped[int] = mapped_column(Integer)
    penalty: Mapped[int] = mapped_column(Integer)
    gp: Mapped[int] = mapped_column(Integer)



# Определяем модель гран-при
class Grandprix(Base):
    __tablename__ = 'grandprix'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    gp_name: Mapped[str] = mapped_column(String(60))
    year: Mapped[int] = mapped_column(Integer)
    gp_name_abr: Mapped[str] = mapped_column(String(3))
    nextgp: Mapped[bool] = mapped_column(Boolean)

    race = relationship('Point', back_populates='gp')
    race_team: Mapped['TeamPoint'] = relationship('TeamPoint', back_populates='gp_team')

# Определяем модель команд
class Team(Base):
    __tablename__ = 'teams'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(60))
    first: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('users.id'))
    second: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('users.id'))
    third: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('users.id'))
    logo: Mapped[str] = mapped_column(String(60))
    captain: Mapped[bool] = mapped_column(Boolean)
    number: Mapped[int] = mapped_column(Integer)

    team_points: Mapped[List['TeamPoint']] = relationship('TeamPoint', back_populates='team')
    # Связи с пользователями
    first_user: Mapped[Optional[User]] = relationship('User', back_populates='teams_first', foreign_keys=[first])
    second_user: Mapped[Optional[User]] = relationship('User', back_populates='teams_second', foreign_keys=[second])
    third_user: Mapped[Optional[User]] = relationship('User', back_populates='teams_third', foreign_keys=[third])

# Определяем модель Командных Очков
class TeamPoint(Base):
    __tablename__ = 'team_points'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    team_id: Mapped[int] = mapped_column(ForeignKey('teams.id'))
    race_id: Mapped[int] = mapped_column(ForeignKey('grandprix.id'))
    points: Mapped[int] = mapped_column(Integer)

    team: Mapped[User] = relationship('Team', back_populates='team_points')
    gp_team: Mapped[Grandprix] = relationship('Grandprix', back_populates='race_team')

# Определяем модель Очков
class Point(Base):
    __tablename__ = 'points'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    race_id: Mapped[int] = mapped_column(ForeignKey('grandprix.id'))
    points: Mapped[int] = mapped_column(Integer)

    user: Mapped[User] = relationship('User', back_populates='points')
    gp: Mapped[Grandprix] = relationship('Grandprix', back_populates='race')


