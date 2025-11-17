import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

DB_NAME = os.getenv("DB_NAME", "telegram_bot.db")

def get_db_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Основная таблица пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица для согласия с политикой конфиденциальности
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS privacy_agreements (
                user_id INTEGER PRIMARY KEY,
                agreed BOOLEAN,
                agreed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Таблица для AI сессий
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_sessions (
                user_id INTEGER PRIMARY KEY,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Таблица для истории диалогов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                role TEXT,
                content TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        conn.commit()

def add_user_if_not_exists(user_id, username):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO users (user_id, username) 
            VALUES (?, ?)
        ''', (user_id, username))
        conn.commit()

def save_privacy_agreement(user_id, agreed):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO privacy_agreements (user_id, agreed)
            VALUES (?, ?)
        ''', (user_id, agreed))
        conn.commit()

def get_user_privacy_status(user_id):
    """Проверяет, давал ли пользователь согласие"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT agreed FROM privacy_agreements WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        return result[0] if result else None

# Функции для AI сессий
def start_ai_session(user_id):
    """Начинает AI сессию"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO ai_sessions (user_id) VALUES (?)', (user_id,))
        conn.commit()

def end_ai_session(user_id):
    """Завершает AI сессию"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM ai_sessions WHERE user_id = ?', (user_id,))
        conn.commit()

def is_ai_session_active(user_id):
    """Проверяет активна ли AI сессия"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM ai_sessions WHERE user_id = ?', (user_id,))
        return cursor.fetchone() is not None

# Функции для истории диалогов
def add_message_to_history(user_id, role, content):
    """Добавляет сообщение в историю диалога"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO conversation_history (user_id, role, content)
            VALUES (?, ?, ?)
        ''', (user_id, role, content))
        conn.commit()

def get_conversation_history(user_id, limit=10):
    """Получает историю диалога пользователя"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT role, content FROM conversation_history 
            WHERE user_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (user_id, limit))
        rows = cursor.fetchall()
        # Возвращаем в правильном порядке (от старых к новым)
        return [{"role": role, "content": content} for role, content in reversed(rows)]

def clear_conversation_history(user_id):
    """Очищает историю диалога пользователя"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM conversation_history WHERE user_id = ?', (user_id,))
        conn.commit()
