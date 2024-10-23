from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    bot_token: SecretStr
    group_id: SecretStr
    admins: str
    db_url: str

    db_host: str
    db_port: str
    db_name: str
    db_user: str
    db_password: str

    postgres_user: str
    postgres_password: str
    postgres_db: str

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


config = Settings()
