"""
Модуль генератора цитат и фактов.
"""
from datetime import datetime
from typing import List, Dict, Optional
from exceptions import (
    EmptyTopicException,
    EmptyContentException,
    TopicNotFoundException,
    InvalidDataException
)
from database import Database


class QuoteGenerator:
    """Класс для управления цитатами и фактами по темам."""
    
    def __init__(self, db_file: str = "quotes.db"):
        """
        Инициализация генератора.
        
        Args:
            db_file: Путь к файлу базы данных
        """
        try:
            self.db = Database(db_file)
        except Exception as e:
            raise InvalidDataException(f"Ошибка инициализации базы данных: {e}")
    
    def get_topics(self) -> List[str]:
        """Получить список всех тем."""
        return self.db.get_all_topics()
    
    def get_quotes_by_topic(self, topic: str) -> List[Dict]:
        """
        Получить все цитаты/факты по теме.
        
        Args:
            topic: Название темы
            
        Returns:
            Список цитат/фактов
            
        Raises:
            TopicNotFoundException: Если тема не найдена
        """
        if not topic:
            raise EmptyTopicException()
        
        quotes = self.db.get_quotes_by_topic(topic)
        
        if not quotes:
            # Проверяем, существует ли тема вообще
            if not self.db.get_topic_id(topic):
                raise TopicNotFoundException(topic)
        
        return quotes
    
    def add_quote(self, topic: str, content: str):
        """
        Добавить новую цитату/факт.
        
        Args:
            topic: Тема
            content: Содержимое цитаты/факта
            
        Raises:
            EmptyTopicException: Если тема пустая
            EmptyContentException: Если содержимое пустое
        """
        if not topic or not topic.strip():
            raise EmptyTopicException()
        
        if not content or not content.strip():
            raise EmptyContentException()
        
        topic = topic.strip()
        content = content.strip()
        
        # Получаем или создаем тему
        topic_id = self.db.get_topic_id(topic)
        if not topic_id:
            topic_id = self.db.add_topic(topic)
        
        # Добавляем цитату
        self.db.add_quote(topic_id, content)
        
        # Логируем активность
        self.db.add_activity_log("add", topic, content)
    
    def get_random_quote(self, topic: Optional[str] = None) -> Optional[Dict]:
        """
        Получить случайную цитату/факт.
        
        Args:
            topic: Тема (опционально)
            
        Returns:
            Словарь с цитатой или None
        """
        quote = self.db.get_random_quote(topic)
        
        if quote:
            # Логируем просмотр
            display_topic = quote.get("topic", topic or "all")
            self.db.add_activity_log("view", display_topic, quote["content"])
        
        return quote
    
    def log_activity(self, action: str, topic: str, content: str):
        """
        Логирование активности.
        
        Args:
            action: Действие (add, view, delete)
            topic: Тема
            content: Содержимое
        """
        self.db.add_activity_log(action, topic, content)
    
    @property
    def activity_log(self) -> List[Dict]:
        """
        Получить лог активности.
        
        Returns:
            Список записей активности
        """
        return self.db.get_activity_log(limit=100)
    
    def get_activity_stats(self) -> Dict[str, int]:
        """
        Получить статистику активности по темам.
        
        Returns:
            Словарь с количеством действий по темам
        """
        return self.db.get_activity_stats()
    
    def close(self):
        """Закрыть соединение с базой данных."""
        if hasattr(self, 'db'):
            self.db.close()
    
    def __del__(self):
        """Деструктор для закрытия соединения."""
        self.close()
