import os
from decouple import config

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(os.path.dirname(BASE_DIR), "data", "ai_bot.db")

# Telegram Bot Token
TELEGRAM_BOT_TOKEN = config('TELEGRAM_BOT_TOKEN', default=False)

# OpenAI Configuration
OPENAI_API_KEY = config('OPENAI_API_KEY', default=False)
OPENAI_MODEL_NAME = config('OPENAI_MODEL_NAME', default=False)

# GigaChat Configuration
GIGACHAT_CREDENTIALS = config('GIGACHAT_CREDENTIALS', default=False)

# Проверка наличия токенов
if not TELEGRAM_BOT_TOKEN:
    print("Ошибка: Токен Telegram бота не установлен в переменных окружения.")
if not OPENAI_API_KEY:
    print("Ошибка: Ключ OpenAI API не установлен в переменных окружения.")
if not GIGACHAT_CREDENTIALS:
    print("Ошибка: Ключ авторизации GigaChat не установлен в переменных окружения.")
if not OPENAI_MODEL_NAME:
    print("Ошибка: Модель OpenAI не установлена в переменных окружения.")