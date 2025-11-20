"""
Тесты для модуля exceptions.py
"""
import pytest
from exceptions import (
    QuoteGeneratorException,
    EmptyTopicException,
    EmptyContentException,
    TopicNotFoundException,
    InvalidDataException
)


class TestExceptions:
    """Тесты для пользовательских исключений."""
    
    def test_quote_generator_exception_base(self):
        """Тест базового исключения."""
        exc = QuoteGeneratorException("Тест")
        assert isinstance(exc, Exception)
        assert str(exc) == "Тест"
    
    def test_empty_topic_exception_default(self):
        """Тест EmptyTopicException с сообщением по умолчанию."""
        exc = EmptyTopicException()
        assert isinstance(exc, QuoteGeneratorException)
        assert "Тема не может быть пустой" in str(exc)
    
    def test_empty_topic_exception_custom(self):
        """Тест EmptyTopicException с пользовательским сообщением."""
        exc = EmptyTopicException("Кастомное сообщение")
        assert str(exc) == "Кастомное сообщение"
    
    def test_empty_content_exception_default(self):
        """Тест EmptyContentException с сообщением по умолчанию."""
        exc = EmptyContentException()
        assert isinstance(exc, QuoteGeneratorException)
        assert "Содержимое" in str(exc)
    
    def test_empty_content_exception_custom(self):
        """Тест EmptyContentException с пользовательским сообщением."""
        exc = EmptyContentException("Кастомное сообщение")
        assert str(exc) == "Кастомное сообщение"
    
    def test_topic_not_found_exception(self):
        """Тест TopicNotFoundException."""
        exc = TopicNotFoundException("Несуществующая тема")
        assert isinstance(exc, QuoteGeneratorException)
        assert exc.topic == "Несуществующая тема"
        assert "Несуществующая тема" in str(exc)
    
    def test_topic_not_found_exception_custom_message(self):
        """Тест TopicNotFoundException с пользовательским сообщением."""
        exc = TopicNotFoundException("Тема", "Кастомное сообщение")
        assert exc.topic == "Тема"
        assert "Кастомное сообщение" in str(exc)
    
    def test_invalid_data_exception_default(self):
        """Тест InvalidDataException с сообщением по умолчанию."""
        exc = InvalidDataException()
        assert isinstance(exc, QuoteGeneratorException)
        assert "Невалидные данные" in str(exc)
    
    def test_invalid_data_exception_custom(self):
        """Тест InvalidDataException с пользовательским сообщением."""
        exc = InvalidDataException("Ошибка загрузки")
        assert str(exc) == "Ошибка загрузки"
    
    def test_exception_inheritance(self):
        """Тест иерархии наследования исключений."""
        assert issubclass(EmptyTopicException, QuoteGeneratorException)
        assert issubclass(EmptyContentException, QuoteGeneratorException)
        assert issubclass(TopicNotFoundException, QuoteGeneratorException)
        assert issubclass(InvalidDataException, QuoteGeneratorException)
        assert issubclass(QuoteGeneratorException, Exception)

