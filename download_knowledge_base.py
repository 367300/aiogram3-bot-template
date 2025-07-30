#!/usr/bin/env python3
"""
Скрипт для скачивания базы знаний из репозитория django-base-docker
"""

import os
import requests
import sys

def download_knowledge_base():
    """
    Скачивает базу знаний embeddings.sqlite3 из репозитория
    """
    # URL для скачивания файла из репозитория
    url = "https://raw.githubusercontent.com/367300/django-base-docker/ml_service/embeddings.sqlite3"
    
    # Путь для сохранения файла
    target_dir = "data/quiz_bot.db"
    target_file = os.path.join(target_dir, "embeddings.sqlite3")
    
    print("📥 Скачивание базы знаний...")
    
    try:
        # Создаем директорию, если её нет
        os.makedirs(target_dir, exist_ok=True)
        
        # Скачиваем файл
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Сохраняем файл
        with open(target_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # Проверяем размер файла
        file_size = os.path.getsize(target_file)
        print(f"✅ База знаний успешно скачана!")
        print(f"📁 Файл: {target_file}")
        print(f"📊 Размер: {file_size / 1024 / 1024:.1f} MB")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка при скачивании: {e}")
        print("💡 Убедитесь, что у вас есть доступ к интернету")
        return False
    except Exception as e:
        print(f"❌ Ошибка при сохранении файла: {e}")
        return False

def main():
    """
    Главная функция
    """
    print("🤖 Скачивание базы знаний для AI Telegram Bot")
    print("=" * 50)
    
    if download_knowledge_base():
        print("\n🎉 База знаний готова к использованию!")
        print("Теперь вы можете запустить бота командой: python main.py")
    else:
        print("\n❌ Не удалось скачать базу знаний")
        print("Попробуйте скачать файл вручную из репозитория:")
        print("https://github.com/367300/django-base-docker/tree/ml_service")
        sys.exit(1)

if __name__ == "__main__":
    main() 