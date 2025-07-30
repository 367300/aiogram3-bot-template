#!/usr/bin/env python3
"""
Скрипт для инициализации базы знаний из существующей БД
"""

import asyncio
from src.knowledge_base import initialize_knowledge_base

async def main():
    """
    Инициализирует базу знаний из существующей БД
    """
    print("🚀 Инициализация базы знаний из embeddings.sqlite3...")
    
    try:
        # Инициализация базы знаний
        await initialize_knowledge_base()
        print("✅ База знаний успешно инициализирована!")
        
    except Exception as e:
        print(f"❌ Ошибка при инициализации базы знаний: {e}")
        print("Убедитесь, что:")
        print("1. Установлены все зависимости: pip install -r requirements.txt")
        print("2. Настроены переменные окружения в файле .env")
        print("3. Указан правильный OPENAI_API_KEY")
        print("4. Файл data/quiz_bot.db/embeddings.sqlite3 существует")

if __name__ == "__main__":
    asyncio.run(main()) 