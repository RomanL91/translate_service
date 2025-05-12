import json
import aio_pika

from typing import Any


class RabbitMQRepository:
    """RabbitMQ Repository"""

    def __init__(self, url: str):
        self.url = url
        self.connection = None
        self.channel = None

    async def connect(self):
        """Создает подключение и канал"""
        if not self.connection:
            self.connection = await aio_pika.connect_robust(self.url)
            self.channel = await self.connection.channel()
            print("✅ RabbitMQ подключение установлено.")
        return self.channel

    async def disconnect(self):
        """Закрывает подключение"""
        if self.connection:
            await self.connection.close()
            self.connection = None
            self.channel = None
            print("✅ RabbitMQ подключение закрыто.")

    async def publish_message(self, queue_name: str, message: Any):
        """Отправляет сообщение в очередь"""
        channel = await self.connect()
        await channel.default_exchange.publish(
            aio_pika.Message(body=json.dumps(message).encode()),
            routing_key=queue_name,
        )
        print(f"✅ Сообщение отправлено в очередь '{queue_name}': {message}")

    async def consume_messages(self, queue_name: str, callback):
        """Читает сообщения из очереди и обрабатывает их"""
        channel = await self.connect()
        queue = await channel.declare_queue(queue_name, durable=True)
        print(f"✅ Слушаем очередь '{queue_name}'...")

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    try:
                        payload = json.loads(message.body.decode())
                        await callback(payload)
                    except Exception as e:
                        print(f"❌ Ошибка при обработке сообщения: {e}")
