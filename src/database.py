import aiosqlite
from src.config import DB_NAME

async def create_table():
    """
    Создает базовую таблицу для хранения информации о пользователях
    """
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        await db.commit()

async def save_user_info(user_id: int, username: str = None, first_name: str = None, last_name: str = None):
    """
    Сохраняет информацию о пользователе
    """
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''INSERT OR REPLACE INTO users (user_id, username, first_name, last_name) 
                           VALUES (?, ?, ?, ?)''', (user_id, username, first_name, last_name))
        await db.commit()

async def get_user_info(user_id: int):
    """
    Получает информацию о пользователе
    """
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT * FROM users WHERE user_id = ?', (user_id,)) as cursor:
            return await cursor.fetchone()