from sqlalchemy import create_engine, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker, Mapped, mapped_column, declarative_base
from typing import Optional, List

# Создаем базовый класс для моделей
Base = declarative_base()


# Определяем модель User
class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(60))

    # Связь с моделью Point
    points: Mapped[List['Point']] = relationship('Point', back_populates='user')


# Определяем модель Point
class Point(Base):
    __tablename__ = 'points'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    value: Mapped[int] = mapped_column(Integer)

    # Связь с моделью User
    user: Mapped[User] = relationship('User', back_populates='points')


# Создаем базу данных и сессию
engine = create_engine('sqlite:///:memory:')  # Используйте вашу строку подключения
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


# Функция для добавления данных
def add_data():
    with Session() as session:
        user1 = User(name='Alice')
        user2 = User(name='Bob')

        point1 = Point(value=10, user=user1)
        point2 = Point(value=20, user=user1)
        point3 = Point(value=15, user=user2)

        session.add(user1)
        session.add(user2)
        session.add(point1)
        session.add(point2)
        session.add(point3)
        session.commit()


# Добавляем данные
add_data()


# Функция для получения пользователей и их очков
def get_users_with_points():
    with Session() as session:
        results = session.query(User).outerjoin(Point).all()
        for user in results:
            print(user.__dict__)
            print(f'User: {user.name}')
            for point in user.points:
                print(point.__dict__)
                print(f'  Point: {point.value}')


# Получаем пользователей и их очки
get_users_with_points()