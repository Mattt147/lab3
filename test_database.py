"""
Тесты для модуля database.py
"""
import pytest
import os
import tempfile
from database import Database
from datetime import datetime


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
def db(temp_db):
    """Создание экземпляра Database с временной БД."""
    return Database(temp_db)


class TestDatabase:
    """Тесты для класса Database."""
    
    def test_init(self, db):
        """Тест инициализации БД."""
        assert db is not None
        assert db.conn is not None
    
    def test_init_sample_data(self, db):
        """Тест инициализации примерами данных."""
        topics = db.get_all_topics()
        assert len(topics) > 0
        assert "Наука" in topics
        assert "Философия" in topics
        assert "Мотивация" in topics
    
    def test_add_topic(self, db):
        """Тест добавления темы."""
        topic_id = db.add_topic("Новая тема")
        assert topic_id is not None
        assert isinstance(topic_id, int)
    
    def test_add_duplicate_topic(self, db):
        """Тест добавления дублирующейся темы."""
        topic_id1 = db.add_topic("Дубликат")
        topic_id2 = db.add_topic("Дубликат")
        assert topic_id1 == topic_id2
    
    def test_get_topic_id(self, db):
        """Тест получения ID темы."""
        topic_id = db.add_topic("Тест ID")
        retrieved_id = db.get_topic_id("Тест ID")
        assert retrieved_id == topic_id
    
    def test_get_topic_id_not_found(self, db):
        """Тест получения ID несуществующей темы."""
        topic_id = db.get_topic_id("Несуществующая")
        assert topic_id is None
    
    def test_get_all_topics(self, db):
        """Тест получения всех тем."""
        db.add_topic("Тема 1")
        db.add_topic("Тема 2")
        
        topics = db.get_all_topics()
        assert "Тема 1" in topics
        assert "Тема 2" in topics
    
    def test_add_quote(self, db):
        """Тест добавления цитаты."""
        topic_id = db.add_topic("Цитаты")
        quote_id = db.add_quote(topic_id, "Тестовая цитата")
        assert quote_id is not None
        assert isinstance(quote_id, int)
    
    def test_get_quotes_by_topic(self, db):
        """Тест получения цитат по теме."""
        topic_id = db.add_topic("Тестовая тема")
        db.add_quote(topic_id, "Цитата 1")
        db.add_quote(topic_id, "Цитата 2")
        
        quotes = db.get_quotes_by_topic("Тестовая тема")
        assert len(quotes) == 2
        assert quotes[0]["content"] in ["Цитата 1", "Цитата 2"]
        assert quotes[1]["content"] in ["Цитата 1", "Цитата 2"]
    
    def test_get_quotes_by_topic_empty(self, db):
        """Тест получения цитат из пустой темы."""
        db.add_topic("Пустая тема")
        quotes = db.get_quotes_by_topic("Пустая тема")
        assert len(quotes) == 0
    
    def test_get_all_quotes(self, db):
        """Тест получения всех цитат."""
        topic_id1 = db.add_topic("Тема 1")
        topic_id2 = db.add_topic("Тема 2")
        db.add_quote(topic_id1, "Цитата 1")
        db.add_quote(topic_id2, "Цитата 2")
        
        quotes = db.get_all_quotes()
        assert len(quotes) >= 2
        contents = [q["content"] for q in quotes]
        assert "Цитата 1" in contents
        assert "Цитата 2" in contents
    
    def test_get_random_quote_with_topic(self, db):
        """Тест получения случайной цитаты по теме."""
        topic_id = db.add_topic("Случайная")
        db.add_quote(topic_id, "Цитата 1")
        db.add_quote(topic_id, "Цитата 2")
        
        quote = db.get_random_quote("Случайная")
        assert quote is not None
        assert quote["content"] in ["Цитата 1", "Цитата 2"]
    
    def test_get_random_quote_all(self, db):
        """Тест получения случайной цитаты из всех."""
        quote = db.get_random_quote()
        # Должна быть хотя бы одна из примерных
        assert quote is not None
        assert "content" in quote
    
    def test_get_random_quote_empty_topic(self, db):
        """Тест получения случайной цитаты из несуществующей темы."""
        quote = db.get_random_quote("Несуществующая")
        assert quote is None
    
    def test_add_activity_log(self, db):
        """Тест добавления записи в лог активности."""
        db.add_activity_log("add", "Тема", "Содержимое")
        logs = db.get_activity_log(limit=10)
        assert len(logs) > 0
        assert logs[0]["action"] == "add"
        assert logs[0]["topic"] == "Тема"
    
    def test_get_activity_log(self, db):
        """Тест получения лога активности."""
        db.add_activity_log("add", "Тема1", "Содержимое1")
        db.add_activity_log("view", "Тема2", "Содержимое2")
        
        logs = db.get_activity_log(limit=10)
        assert len(logs) >= 2
        actions = [log["action"] for log in logs]
        assert "add" in actions or "view" in actions
    
    def test_get_activity_stats(self, db):
        """Тест получения статистики активности."""
        db.add_activity_log("add", "Тема1", "Содержимое1")
        db.add_activity_log("add", "Тема1", "Содержимое2")
        db.add_activity_log("view", "Тема2", "Содержимое3")
        
        stats = db.get_activity_stats()
        assert isinstance(stats, dict)
        assert "Тема1" in stats
        assert stats["Тема1"] >= 2
    
    def test_activity_log_content_truncation(self, db):
        """Тест обрезки длинного содержимого в логе."""
        long_content = "A" * 100
        db.add_activity_log("add", "Тема", long_content)
        
        logs = db.get_activity_log(limit=10)
        assert len(logs) > 0
        # Содержимое должно быть обрезано до 50 символов
        assert len(logs[0]["content"]) <= 50
    
    def test_close_connection(self, db):
        """Тест закрытия соединения."""
        db.close()
        assert db.conn is None

