from dataclasses import dataclass
from environs import Env


@dataclass
class TgBot:
    token: str  # Токен для доступа к телеграм-боту
    admin_id: int
    all_admins: list
    db_user: str
    db_password: str
    db_name: str


@dataclass
class Config:
    tg_bot: TgBot


def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(tg_bot=TgBot(token=env('BOT_TOKEN'),
                               admin_id=int(env('ADMIN_ID')),
                               all_admins=([int(i) for i in env('ALL_ADMINS').split(',')]),
                               db_user=env('DB_USERNAME'),
                               db_password=env('DB_PASSWORD'),
                               db_name=env('DB_NAME')))
