from services.rabbitmq_repository import RabbitMQRepository
from services.translator_service import TranslatorService

from settings import settings


class TranslationService:
    """Основной сервис для управления переводами"""

    def __init__(
        self, rabbitmq_repo: RabbitMQRepository, translator_service: TranslatorService
    ):
        self.rabbitmq_repo = rabbitmq_repo
        self.translator_service = translator_service

        # имя очереди для переведенного
        self.response_queue = settings.response_translation_queue

    async def send_translation_request(self, text: str, target_lang: str):
        """Отправляет запрос на перевод в очередь"""
        message = {"text": text, "target_lang": target_lang}
        await self.rabbitmq_repo.publish_message(settings.translation_queue, message)

    async def process_translation(self, payload: dict):
        """Обрабатывает сообщение из очереди"""
        text = payload.get("text")
        target_lang = payload.get("target_lang")

        if not text or not target_lang:
            print(f"❌ Неверное сообщение: {payload}")
            return

        # Выполняем перевод
        translated_text = await self.translator_service.translate(text, target_lang)
        print(f"✅ Перевод: '{text}' -> '{translated_text}'")

        # Формируем новое сообщение с переводом
        new_message = payload.copy()
        new_message["text"] = translated_text

        # Публикуем перевод в очередь response_queue
        await self.rabbitmq_repo.publish_message(self.response_queue, new_message)

    async def start_consumer(self):
        """Запуск прослушивания очереди"""
        await self.rabbitmq_repo.consume_messages(
            settings.translation_queue, self.process_translation
        )
