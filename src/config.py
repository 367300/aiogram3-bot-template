import os
from decouple import config

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(os.path.dirname(BASE_DIR), "data", "ai_bot.db")

# Telegram Bot Token
TELEGRAM_BOT_TOKEN = config('TELEGRAM_BOT_TOKEN', default=False)

# OpenAI Configuration
OPENAI_API_KEY = config('OPENAI_API_KEY', default=False)
OPENAI_MODEL_NAME = "gpt-3.5-turbo"

# GigaChat Configuration
GIGACHAT_CREDENTIALS = config('GIGACHAT_CREDENTIALS', default=False)

# OpenAI Proxy Configuration (опционально)
PROXY_URL = config('PROXY_URL', default=False)
PROXY_USERNAME = config('PROXY_USERNAME', default=False)
PROXY_PASSWORD = config('PROXY_PASSWORD', default=False)

# OpenVPN Configuration (опционально)
OVPN_CONFIG_PATH = config('OVPN_CONFIG_PATH', default=False)

# Проверка наличия токенов
if not TELEGRAM_BOT_TOKEN:
    print("Ошибка: Токен Telegram бота не установлен в переменных окружения.")
if not OPENAI_API_KEY:
    print("Ошибка: Ключ OpenAI API не установлен в переменных окружения.")
if not GIGACHAT_CREDENTIALS:
    print("Ошибка: Ключ авторизации GigaChat не установлен в переменных окружения.")

# Информация о прокси и VPN
if PROXY_URL:
    print(f"🔒 Настроен прокси для OpenAI: {PROXY_URL}")
elif OVPN_CONFIG_PATH:
    print(f"🔒 Настроен VPN для OpenAI: {OVPN_CONFIG_PATH}")
else:
    print("🌐 Прокси/VPN для OpenAI не настроен")