"""
Тесты для модуля quote_generator.py
"""
import pytest
import os
import tempfile
from quote_generator import QuoteGenerator
from exceptions import (
    EmptyTopicException,
    EmptyContentException,
    TopicNotFoundException,
    InvalidDataException
)


@pytest.fixture
def temp_db():
    """Создание временной БД для тестов."""
    fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    yield db_path
    # Очистка после теста
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture
def generator(temp_db):
    """Создание генератора с временной БД."""
    return QuoteGenerator(temp_db)


class TestQuoteGenerator:
    """Тесты для класса QuoteGenerator."""
    
    def test_init(self, generator):
        """Тест инициализации генератора."""
        assert generator is not None
        assert generator.db is not None
    
    def test_get_topics_initial(self, generator):
        """Тест получения тем при инициализации (должны быть примеры)."""
        topics = generator.get_topics()
        assert isinstance(topics, list)
        assert len(topics) > 0
        assert "Наука" in topics
        assert "Философия" in topics
        assert "Мотивация" in topics
    
    def test_add_quote_success(self, generator):
        """Тест успешного добавления цитаты."""
        generator.add_quote("Тест", "Тестовая цитата")
        quotes = generator.get_quotes_by_topic("Тест")
        assert len(quotes) == 1
        assert quotes[0]["content"] == "Тестовая цитата"
    
    def test_add_quote_empty_topic(self, generator):
        """Тест добавления цитаты с пустой темой."""
        with pytest.raises(EmptyTopicException):
            generator.add_quote("", "Содержимое")
    
    def test_add_quote_empty_content(self, generator):
        """Тест добавления цитаты с пустым содержимым."""
        with pytest.raises(EmptyContentException):
            generator.add_quote("Тема", "")
    
    def test_add_quote_whitespace_only(self, generator):
        """Тест добавления цитаты только с пробелами."""
        with pytest.raises(EmptyTopicException):
            generator.add_quote("   ", "Содержимое")
        
        with pytest.raises(EmptyContentException):
            generator.add_quote("Тема", "   ")
    
    def test_get_quotes_by_topic_existing(self, generator):
        """Тест получения цитат по существующей теме."""
        generator.add_quote("Новая тема", "Цитата 1")
        generator.add_quote("Новая тема", "Цитата 2")
        
        quotes = generator.get_quotes_by_topic("Новая тема")
        assert len(quotes) == 2
        assert quotes[0]["content"] in ["Цитата 1", "Цитата 2"]
        assert quotes[1]["content"] in ["Цитата 1", "Цитата 2"]
    
    def test_get_quotes_by_topic_not_found(self, generator):
        """Тест получения цитат по несуществующей теме."""
        with pytest.raises(TopicNotFoundException):
            generator.get_quotes_by_topic("Несуществующая тема")
    
    def test_get_quotes_by_topic_empty(self, generator):
        """Тест получения цитат с пустой темой."""
        with pytest.raises(EmptyTopicException):
            generator.get_quotes_by_topic("")
    
    def test_get_random_quote_with_topic(self, generator):
        """Тест получения случайной цитаты по теме."""
        generator.add_quote("Случайная", "Цитата 1")
        generator.add_quote("Случайная", "Цитата 2")
        
        quote = generator.get_random_quote("Случайная")
        assert quote is not None
        assert quote["content"] in ["Цитата 1", "Цитата 2"]
    
    def test_get_random_quote_all_topics(self, generator):
        """Тест получения случайной цитаты из всех тем."""
        quote = generator.get_random_quote()
        assert quote is not None
        assert "content" in quote
        assert "date" in quote
    
    def test_get_random_quote_empty_topic(self, generator):
        """Тест получения случайной цитаты из несуществующей темы."""
        quote = generator.get_random_quote("Несуществующая")
        assert quote is None
    
    def test_activity_logging(self, generator):
        """Тест логирования активности."""
        generator.add_quote("Логирование", "Тестовая цитата")
        
        logs = generator.activity_log
        assert len(logs) > 0
        assert logs[0]["action"] == "add"
        assert logs[0]["topic"] == "Логирование"
    
    def test_get_activity_stats(self, generator):
        """Тест получения статистики активности."""
        generator.add_quote("Статистика1", "Цитата 1")
        generator.add_quote("Статистика1", "Цитата 2")
        generator.add_quote("Статистика2", "Цитата 3")
        
        stats = generator.get_activity_stats()
        assert isinstance(stats, dict)
        assert "Статистика1" in stats
        assert stats["Статистика1"] >= 2  # Минимум 2 добавления
    
    def test_multiple_topics(self, generator):
        """Тест работы с несколькими темами."""
        generator.add_quote("Тема1", "Цитата 1")
        generator.add_quote("Тема2", "Цитата 2")
        generator.add_quote("Тема3", "Цитата 3")
        
        topics = generator.get_topics()
        assert "Тема1" in topics
        assert "Тема2" in topics
        assert "Тема3" in topics
        
        assert len(generator.get_quotes_by_topic("Тема1")) == 1
        assert len(generator.get_quotes_by_topic("Тема2")) == 1
        assert len(generator.get_quotes_by_topic("Тема3")) == 1
    
    def test_quote_content_preservation(self, generator):
        """Тест сохранения содержимого цитаты."""
        long_content = "Это очень длинная цитата, которая содержит много текста и должна быть полностью сохранена в базе данных."
        generator.add_quote("Длинная", long_content)
        
        quotes = generator.get_quotes_by_topic("Длинная")
        assert quotes[0]["content"] == long_content
    
    def test_special_characters(self, generator):
        """Тест работы со специальными символами."""
        special_content = "Цитата с спец. символами: !@#$%^&*()_+-=[]{}|;':\",./<>?"
        generator.add_quote("Спец. символы", special_content)
        
        quotes = generator.get_quotes_by_topic("Спец. символы")
        assert quotes[0]["content"] == special_content
    
    def test_unicode_content(self, generator):
        """Тест работы с Unicode символами."""
        unicode_content = "Цитата с эмодзи: 😀 🎉 🚀 и кириллицей: Привет!"
        generator.add_quote("Unicode", unicode_content)
        
        quotes = generator.get_quotes_by_topic("Unicode")
        assert quotes[0]["content"] == unicode_content

