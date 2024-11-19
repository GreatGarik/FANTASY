from typing import Optional, List
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import create_engine, select, update, case
from sqlalchemy.orm import Session, sessionmaker

# Создаем базовый класс для моделей
class Base(DeclarativeBase):
    pass

# Подключаемся к базе данных
engine = create_engine("sqlite:///fantasy.db", echo=False)

# Создаем сессию
Session = sessionmaker(engine)
# Определяем модель пользователей
class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_telegram: Mapped[int] = mapped_column(Integer, unique=True)
    vk_link: Mapped[str] = mapped_column(String(60))
    name: Mapped[str] = mapped_column(String(60))
    user_team: Mapped[Optional[str]] = mapped_column(String(60))

    points: Mapped[List['Point']] = relationship('Point', back_populates='user')

# Определяем модель Очков
class Point(Base):
    __tablename__ = 'points'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    race_id: Mapped[int] = mapped_column(ForeignKey('grandprix.id'))
    year: Mapped[int] = mapped_column(Integer)
    points: Mapped[int] = mapped_column(Integer)

    user: Mapped[User] = relationship('User', back_populates='points')

# Показ очков
def show_points():
    with Session() as session:
        result = session.query(User).outerjoin(Point).all()
        for user in result:
            print(f'User: {user.name}')
            for point in user.points:
                print(f'  Point: {point.points}')


show_points()