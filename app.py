import asyncio

from fastapi import FastAPI, HTTPException

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

from services.translator_service import TranslatorService
from services.translation_service import TranslationService
from services.rabbitmq_repository import RabbitMQRepository


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


# ------------------------------------------------------------------------------------
# Инициализация
# ------------------------------------------------------------------------------------
rabbitmq_repo = RabbitMQRepository(settings.rabbitmq_url)
translator_service = TranslatorService()
translation_service = TranslationService(rabbitmq_repo, translator_service)


# ------------------------------------------------------------------------------------
# Логика жизненного цикла приложения
# ------------------------------------------------------------------------------------
async def app_lifespan(app: FastAPI):
    # Инициализация очередей
    await rabbitmq_repo.declare_queue(translation_service.response_queue)
    consume_task = asyncio.create_task(translation_service.start_consumer())
    print("✅ Приложение запущено")

    yield

    # Завершаем таск и закрываем соединение с RabbitMQ
    if not consume_task.cancelled():
        consume_task.cancel()

    await rabbitmq_repo.disconnect()
    print("✅ Приложение остановлено")


# ------------------------------------------------------------------------------------
# Инициализация приложения FastAPI с `lifespan`
# ------------------------------------------------------------------------------------
app = FastAPI(lifespan=app_lifespan)


# ------------------------------------------------------------------------------------
# Модель данных
# ------------------------------------------------------------------------------------
class TranslationRequest(BaseModel):
    text: str
    target_lang: str


# ------------------------------------------------------------------------------------
# Эндпоинт для отправки сообщения в очередь
# ------------------------------------------------------------------------------------
@app.post("/tran")
async def translate_request(request: TranslationRequest):
    try:
        await translation_service.send_translation_request(
            request.text, request.target_lang
        )
        return {"status": "Message sent to queue"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
