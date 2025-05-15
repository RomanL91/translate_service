from pydantic_settings import BaseSettings, SettingsConfigDict


# ------------------------------------------------------------------------------------
# Конфигурация
# ------------------------------------------------------------------------------------
class AppSettings(BaseSettings):

    host: str
    port: int
    reload: bool

    rabbitmq_url: str

    translation_queue: str
    response_translation_queue: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = AppSettings()
