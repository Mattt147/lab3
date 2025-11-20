"""
Модуль с пользовательскими исключениями для приложения генератора цитат/фактов.
"""


class QuoteGeneratorException(Exception):
    """Базовое исключение для генератора цитат."""
    pass


class EmptyTopicException(QuoteGeneratorException):
    """Исключение при пустой теме."""
    def __init__(self, message="Тема не может быть пустой"):
        self.message = message
        super().__init__(self.message)


class EmptyContentException(QuoteGeneratorException):
    """Исключение при пустом содержимом цитаты/факта."""
    def __init__(self, message="Содержимое цитаты/факта не может быть пустым"):
        self.message = message
        super().__init__(self.message)


class TopicNotFoundException(QuoteGeneratorException):
    """Исключение при отсутствии темы."""
    def __init__(self, topic, message="Тема не найдена"):
        self.topic = topic
        self.message = f"{message}: {topic}"
        super().__init__(self.message)


class InvalidDataException(QuoteGeneratorException):
    """Исключение при невалидных данных."""
    def __init__(self, message="Невалидные данные"):
        self.message = message
        super().__init__(self.message)

