import numpy as np
import pandas as pd
import aiosqlite
import json
import requests
from gigachat import GigaChat
from src.config import GIGACHAT_CREDENTIALS
import os

# Глобальная переменная для хранения токена доступа GigaChat
giga_access_token = None

# URL для получения эмбеддингов GigaChat
GIGACHAT_EMBEDDINGS_URL = "https://gigachat.devices.sberbank.ru/api/v1/embeddings"

# Инициализация клиента GigaChat
giga_client = GigaChat(
    credentials=GIGACHAT_CREDENTIALS
)

# Получаем токен доступа при инициализации
def get_gigachat_token():
    """Получить токен доступа для GigaChat API."""
    try:
        response = giga_client.get_token()
        return response.access_token
    except Exception as e:
        print(f'[red]Ошибка получения токена GigaChat: {e}[/red]')
        return None

# Путь к существующей базе данных
EMBEDDINGS_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "quiz_bot.db", "embeddings_gigachat.sqlite3")

def get_embedding(text: str) -> list:
    """
    Получает эмбеддинг для текста через GigaChat API с автоматическим обновлением токена
    """
    global giga_access_token
    
    if not giga_access_token:
        print("❌ Токен доступа GigaChat не получен. Выполните инициализацию базы знаний.")
        return None
    
    max_retries = 3  # Максимальное количество попыток обновления токена
    
    for attempt in range(max_retries):
        try:
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': f'Bearer {giga_access_token}'
            }
            
            data = {
                "model": "EmbeddingsGigaR",
                "input": [text]
            }
            
            response = requests.post(GIGACHAT_EMBEDDINGS_URL, headers=headers, json=data)
            response.raise_for_status()
            
            response_data = response.json()
            return response_data['data'][0]['embedding']
            
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                print(f"🔄 Токен истек (попытка {attempt + 1}/{max_retries}). Получение нового токена...")
                
                # Получаем новый токен
                new_token = get_gigachat_token()
                if new_token:
                    giga_access_token = new_token
                    print("✅ Новый токен получен, повторяем запрос...")
                    continue
                else:
                    print("❌ Не удалось получить новый токен")
                    return None
            else:
                print(f"HTTP ошибка при получении эмбеддинга: {e}")
                return None
        except Exception as e:
            print(f"Ошибка при получении эмбеддинга: {e}")
            return None
    
    print(f"❌ Превышено максимальное количество попыток ({max_retries})")
    return None

async def load_embeddings_from_db():
    """
    Загружает эмбеддинги из существующей базы данных
    """
    try:
        async with aiosqlite.connect(EMBEDDINGS_DB_PATH) as db:
            # Получаем все записи из таблицы embeddings
            async with db.execute('''
                SELECT id, embedding, raw_text, embedding_text, class_name, method_name, 
                       file_path, block_type, start_line, end_line
                FROM embeddings
            ''') as cursor:
                rows = await cursor.fetchall()
                
                embeddings_data = []
                for row in rows:
                    embedding_json = row[1]  # embedding поле
                    if embedding_json:
                        try:
                            embedding_vector = json.loads(embedding_json)
                            embeddings_data.append({
                                'id': row[0],
                                'embedding': embedding_vector,
                                'raw_text': row[2],
                                'embedding_text': row[3],
                                'class_name': row[4],
                                'method_name': row[5],
                                'file_path': row[6],
                                'block_type': row[7],
                                'start_line': row[8],
                                'end_line': row[9]
                            })
                        except json.JSONDecodeError:
                            print(f"Ошибка парсинга JSON для записи {row[0]}")
                            continue
                
                print(f"Загружено {len(embeddings_data)} записей из базы знаний")
                return embeddings_data
                
    except Exception as e:
        print(f"Ошибка при загрузке базы знаний: {e}")
        return []

# Глобальная переменная для хранения данных
embeddings_data = []

async def initialize_knowledge_base():
    """
    Инициализирует базу знаний из существующей БД и получает токен доступа GigaChat
    """
    global embeddings_data, giga_access_token
    
    # Получение токена доступа GigaChat
    print("🔑 Получение токена доступа GigaChat...")
    giga_access_token = get_gigachat_token()
    if not giga_access_token:
        print("❌ Не удалось получить токен доступа GigaChat")
        return
    
    print("✅ Токен доступа GigaChat получен")
    
    # Загрузка базы знаний
    print("📚 Загрузка базы знаний из embeddings.sqlite3...")
    embeddings_data = await load_embeddings_from_db()
    print(f"✅ База знаний инициализирована. Записей: {len(embeddings_data)}")

def get_relevant_contexts(user_query, top_k=5):
    """
    Находит наиболее релевантные контексты для запроса пользователя
    """
    if len(embeddings_data) == 0:
        print("⚠️ База знаний не инициализирована")
        return []
    
    user_embedding = get_embedding(user_query)
    if not user_embedding:
        return []
    
    # Расчет косинусного сходства
    knowledge_embeddings = np.array([item['embedding'] for item in embeddings_data])
    user_embedding_np = np.array(user_embedding).reshape(1, -1)
    
    from sklearn.metrics.pairwise import cosine_similarity
    similarities = cosine_similarity(user_embedding_np, knowledge_embeddings)[0]
    
    # Получение индексов наиболее похожих записей
    top_indices = np.argsort(similarities)[-top_k:][::-1]
    
    # Извлечение релевантных текстовых фрагментов
    relevant_contexts = []
    for idx in top_indices:
        item = embeddings_data[idx]
        context = {
            'text': item['raw_text'],
            'file_path': item['file_path'],
            'class_name': item['class_name'],
            'method_name': item['method_name'],
            'block_type': item['block_type'],
            'similarity': similarities[idx]
        }
        relevant_contexts.append(context)
    
    return relevant_contexts

def get_knowledge_base_info():
    """
    Возвращает информацию о базе знаний
    """
    if len(embeddings_data) == 0:
        return "База знаний не загружена"
    
    # Статистика по типам блоков
    block_types = {}
    class_names = set()
    method_names = set()
    
    for item in embeddings_data:
        block_type = item['block_type']
        block_types[block_type] = block_types.get(block_type, 0) + 1
        
        if item['class_name']:
            class_names.add(item['class_name'])
        if item['method_name']:
            method_names.add(item['method_name'])
    
    info = f"📊 База знаний содержит {len(embeddings_data)} записей\n"
    info += f"📁 Типы блоков: {', '.join([f'{k}: {v}' for k, v in block_types.items()])}\n"
    info += f"🏗️ Классов: {len(class_names)}\n"
    info += f"⚙️ Методов/функций: {len(method_names)}"
    
    return info 