from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import *

# Создаем базу данных
engine = create_engine("sqlite:///fantasy.db", echo=False)
for_replace = [
    ('(З) McLaren', 'McLaren'),
    ('(К) Ferrari', 'Ferrari'),
    ('(С) Red Bull Racing', 'RedBull'),
    ('(З) Mercedes', 'Mercedes'),
    ('(З) Aston Martin', 'AstonMartin'),
    ('(Р) Alpine', 'Alpine'),
    ('(К) Haas', 'Haas'),
    ('(С) RB', 'RB'),
    ('(З) Williams', 'Williams'),
    ('(К) Kick Sauber', 'Sauber'),
    ('(С) Red Bull Powertrains', 'RedBull'),
    ('(З) Mercedes', 'Mercedes'),
    ('(К) Ferrari', 'Ferrari'),
    ('(Р) Renault', 'Renault'),
    ('(С) #1 Max Verstappen', 'Max Verstappen'),
    ('(З) #4 Lando Norris', 'Lando Norris'),
    ('(К) #16 Charles Leclerc', 'Charles Leclerc'),
    ('(З) #81 Oscar Piastri', 'Oscar Piastri'),
    ('(К) #55 Carlos Sainz', 'Carlos Sainz'),
    ('(З) #63 George Russell', 'George Russell'),
    ('(З) #44 Lewis Hamilton', 'Lewis Hamilton'),
    ('(С) #11 Sergio Perez', 'Sergio Pérez'),
    ('(З) #14 Fernando Alonso', 'Fernando Alonso'),
    ('(К) #27 Nico Hulkenberg', 'Nico Hülkenberg'),
    ('(С) #22 Yuki Tsunoda', 'Yuki Tsunoda'),
    ('(Р) #10 Pierre Gasly', 'Pierre Gasly'),
    ('(З) #18 Lance Stroll', 'Lance Stroll'),
    ('(Р) #31 Esteban Ocon', 'Esteban Ocon'),
    ('(К) #20 Kevin Magnussen', 'Kevin Magnussen'),
    ('(З) #23 Alexander Albon', 'Alexander Albon'),
    ('(З) #43 Franco Colapinto', 'Franco Colapinto'),
    ('(С) #30 Liam Lawson', 'Liam Lawson'),
    ('(К) #24 Zhou Guanyu', 'Zhou Guanyu'),
    ('(К) #77 Valtteri Bottas', 'Valtteri Bottas'),
    ('(Р) #7 Jack Doohan', 'Jack Doohan')
]

# Создаем сессию
Session = sessionmaker(engine)

with Session() as session:
    result = session.query(User.name, User.id_telegram).all()
    user_dict = {name.lower(): id_telegram for name, id_telegram in result}


    for _ in range(100):
        gp = 22
        txt = input()
        for a, b in for_replace:
            txt = txt.replace(a, b)

        fn, sn , driver_team, driver_engine, p1n, p1f, p2n, p2f, p3n, p3f, p4n, p4f, gap, lapped = txt.split()
        first_driver = p1n + ' ' + p1f
        second_driver = p2n + ' ' + p2f
        third_driver = p3n + ' ' + p3f
        fourth_driver = p4n + ' ' + p4f
        if driver_team == 'RedBull':
            driver_team = 'Red Bull'
        if driver_team == 'AstonMartin':
            driver_team = 'Aston Martin'
        if driver_engine == 'RedBull':
            driver_engine = 'Red Bull'
        tg_id = user_dict.get(fn.lower() + ' ' + sn.lower(), 0)

        try:
            session.add(Predict(user_id=tg_id, first_driver=first_driver, second_driver=second_driver,
                                third_driver=third_driver, fourth_driver=fourth_driver, driver_team=driver_team,
                                driver_engine=driver_engine, gap=gap, lapped=lapped, gp=gp, penalty=0))
            session.commit()
        except Exception as e:
            print(e)
