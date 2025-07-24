from decouple import config

API_TOKEN = config('API_TOKEN_TG', default=False)
DB_NAME = 'quiz_bot.db'