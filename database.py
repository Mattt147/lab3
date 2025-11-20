"""
Модуль для работы с базой данных SQLite.
"""
import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional
from exceptions import InvalidDataException


class Database:
    """Класс для работы с базой данных SQLite."""
    
    def __init__(self, db_file: str = "quotes.db"):
        """
        Инициализация подключения к БД.
        
        Args:
            db_file: Путь к файлу базы данных
        """
        self.db_file = db_file
        self.conn = None
        self.init_database()
    
    def get_connection(self) -> sqlite3.Connection:
        """Получить соединение с БД."""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_file, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row  # Для доступа по имени колонок
        return self.conn
    
    def init_database(self):
        """Инициализация структуры базы данных."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Таблица тем
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        
        # Таблица цитат/фактов
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quotes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE
            )
        """)
        
        # Таблица активности
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT NOT NULL,
                topic TEXT NOT NULL,
                content TEXT,
                timestamp TEXT NOT NULL
            )
        """)
        
        # Индексы для ускорения запросов
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_quotes_topic_id 
            ON quotes(topic_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_activity_topic 
            ON activity_log(topic)
        """)
        
        conn.commit()
        
        # Инициализация примерами данных, если БД пустая
        if self.is_database_empty():
            self.init_sample_data()
    
    def is_database_empty(self) -> bool:
        """Проверить, пуста ли база данных."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM topics")
        count = cursor.fetchone()[0]
        return count == 0
    
    def init_sample_data(self):
        """Инициализация примерами данных."""
        sample_data = {
            "Наука": [
                "Наука - это организованное знание.",
                "В науке нет широкой столбовой дороги."
            ],
            "Философия": [
                "Познай самого себя.",
                "Я знаю, что ничего не знаю."
            ],
            "Мотивация": [
                "Успех - это способность идти от неудачи к неудаче, не теряя энтузиазма."
            ]
        }
        
        for topic_name, quotes in sample_data.items():
            topic_id = self.add_topic(topic_name)
            for quote_content in quotes:
                self.add_quote(topic_id, quote_content)
    
    def add_topic(self, topic_name: str) -> int:
        """
        Добавить тему.
        
        Args:
            topic_name: Название темы
            
        Returns:
            ID созданной темы
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO topics (name, created_at)
                VALUES (?, ?)
            """, (topic_name, datetime.now().isoformat()))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            # Тема уже существует, получаем её ID
            cursor.execute("SELECT id FROM topics WHERE name = ?", (topic_name,))
            result = cursor.fetchone()
            return result[0] if result else None
    
    def get_topic_id(self, topic_name: str) -> Optional[int]:
        """
        Получить ID темы по названию.
        
        Args:
            topic_name: Название темы
            
        Returns:
            ID темы или None
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM topics WHERE name = ?", (topic_name,))
        result = cursor.fetchone()
        return result[0] if result else None
    
    def get_all_topics(self) -> List[str]:
        """
        Получить список всех тем.
        
        Returns:
            Список названий тем
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM topics ORDER BY name")
        return [row[0] for row in cursor.fetchall()]
    
    def add_quote(self, topic_id: int, content: str) -> int:
        """
        Добавить цитату/факт.
        
        Args:
            topic_id: ID темы
            content: Содержимое цитаты/факта
            
        Returns:
            ID созданной цитаты
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO quotes (topic_id, content, created_at)
            VALUES (?, ?, ?)
        """, (topic_id, content, datetime.now().isoformat()))
        conn.commit()
        return cursor.lastrowid
    
    def get_quotes_by_topic(self, topic_name: str) -> List[Dict]:
        """
        Получить все цитаты по теме.
        
        Args:
            topic_name: Название темы
            
        Returns:
            Список словарей с цитатами
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT q.id, q.content, q.created_at
            FROM quotes q
            JOIN topics t ON q.topic_id = t.id
            WHERE t.name = ?
            ORDER BY q.created_at DESC
        """, (topic_name,))
        
        quotes = []
        for row in cursor.fetchall():
            quotes.append({
                "id": row[0],
                "content": row[1],
                "date": row[2]
            })
        return quotes
    
    def get_all_quotes(self) -> List[Dict]:
        """
        Получить все цитаты из всех тем.
        
        Returns:
            Список словарей с цитатами
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT q.id, q.content, q.created_at, t.name as topic_name
            FROM quotes q
            JOIN topics t ON q.topic_id = t.id
            ORDER BY q.created_at DESC
        """)
        
        quotes = []
        for row in cursor.fetchall():
            quotes.append({
                "id": row[0],
                "content": row[1],
                "date": row[2],
                "topic": row[3]
            })
        return quotes
    
    def get_random_quote(self, topic_name: Optional[str] = None) -> Optional[Dict]:
        """
        Получить случайную цитату.
        
        Args:
            topic_name: Название темы (опционально)
            
        Returns:
            Словарь с цитатой или None
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if topic_name:
            cursor.execute("""
                SELECT q.id, q.content, q.created_at, t.name as topic_name
                FROM quotes q
                JOIN topics t ON q.topic_id = t.id
                WHERE t.name = ?
                ORDER BY RANDOM()
                LIMIT 1
            """, (topic_name,))
        else:
            cursor.execute("""
                SELECT q.id, q.content, q.created_at, t.name as topic_name
                FROM quotes q
                JOIN topics t ON q.topic_id = t.id
                ORDER BY RANDOM()
                LIMIT 1
            """)
        
        row = cursor.fetchone()
        if row:
            return {
                "id": row[0],
                "content": row[1],
                "date": row[2],
                "topic": row[3]
            }
        return None
    
    def add_activity_log(self, action: str, topic: str, content: str = ""):
        """
        Добавить запись в лог активности.
        
        Args:
            action: Действие (add, view, delete)
            topic: Тема
            content: Содержимое (первые 50 символов)
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO activity_log (action, topic, content, timestamp)
            VALUES (?, ?, ?, ?)
        """, (action, topic, content[:50], datetime.now().isoformat()))
        conn.commit()
    
    def get_activity_log(self, limit: int = 100) -> List[Dict]:
        """
        Получить лог активности.
        
        Args:
            limit: Максимальное количество записей
            
        Returns:
            Список записей активности
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT action, topic, content, timestamp
            FROM activity_log
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        
        logs = []
        for row in cursor.fetchall():
            logs.append({
                "action": row[0],
                "topic": row[1],
                "content": row[2],
                "timestamp": row[3]
            })
        return logs
    
    def get_activity_stats(self) -> Dict[str, int]:
        """
        Получить статистику активности по темам.
        
        Returns:
            Словарь с количеством действий по темам
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT topic, COUNT(*) as count
            FROM activity_log
            GROUP BY topic
            ORDER BY count DESC
        """)
        
        stats = {}
        for row in cursor.fetchall():
            stats[row[0]] = row[1]
        return stats
    
    def close(self):
        """Закрыть соединение с БД."""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def __del__(self):
        """Деструктор для закрытия соединения."""
        self.close()

