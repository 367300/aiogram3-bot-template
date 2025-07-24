import os
from decouple import config

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(os.path.dirname(BASE_DIR), "data", "quiz_bot.db")
API_TOKEN = config('API_TOKEN_TG', default=False)