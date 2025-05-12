from googletrans import Translator


class TranslatorService:
    """Сервис для перевода текста"""

    def __init__(self):
        self.translator = Translator()

    async def translate(self, text: str, target_lang: str) -> str:
        """Выполняет перевод текста"""
        try:
            translation = await self.translator.translate(text, dest=target_lang)
            return translation.text
        except Exception as e:
            print(f"❌ Ошибка перевода: {e}")
            return f"Ошибка: {e}"
