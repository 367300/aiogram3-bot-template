from aiogram import types, F
from aiogram import Router
from openai import OpenAI
from src.config import OPENAI_API_KEY, OPENAI_MODEL_NAME
from src.knowledge_base import get_relevant_contexts
import os
import httpx
import sys
import atexit

# Добавляем путь к корневой директории для импорта vpn_manager
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from vpn_manager import init_vpn_manager, ensure_vpn_for_openai, cleanup_vpn

router = Router()

# Настройки прокси (опционально)
PROXY_URL = os.environ.get("PROXY_URL")
PROXY_USERNAME = os.environ.get("PROXY_USERNAME")
PROXY_PASSWORD = os.environ.get("PROXY_PASSWORD")

# Настройки VPN (опционально)
OVPN_CONFIG_PATH = os.environ.get("OVPN_CONFIG_PATH")

# Инициализация VPN менеджера
vpn_manager = None
if OVPN_CONFIG_PATH:
    try:
        vpn_manager = init_vpn_manager(OVPN_CONFIG_PATH)
        print(f"🔒 VPN менеджер инициализирован: {OVPN_CONFIG_PATH}")
        # Регистрируем функцию очистки при завершении
        atexit.register(cleanup_vpn)
    except Exception as e:
        print(f"⚠️ Ошибка инициализации VPN: {e}")

# Инициализация клиента OpenAI с прокси (если настроен)
if PROXY_URL:
    # Создаем HTTP клиент с прокси
    proxy_auth = None
    if PROXY_USERNAME and PROXY_PASSWORD:
        proxy_auth = httpx.BasicAuth(PROXY_USERNAME, PROXY_PASSWORD)
    
    http_client = httpx.Client(
        proxies=PROXY_URL,
        auth=proxy_auth,
        timeout=30.0
    )
    client = OpenAI(api_key=OPENAI_API_KEY, http_client=http_client)
    print(f"🔒 OpenAI клиент настроен с прокси: {PROXY_URL}")
else:
    client = OpenAI(api_key=OPENAI_API_KEY)
    print("🌐 OpenAI клиент настроен без прокси")

@router.message(F.text)
async def handle_message(message: types.Message):
    """
    Обработчик текстовых сообщений для AI-бота
    """
    user_message = message.text
    
    # Показываем индикатор набора текста
    await message.answer("🤔 Ищу информацию в базе знаний...")
    
    # Получение релевантных контекстов
    relevant_contexts = get_relevant_contexts(user_message, top_k=5)
    
    if not relevant_contexts:
        await message.answer(
            "❌ Извините, не удалось найти релевантную информацию в базе знаний. "
            "Попробуйте переформулировать ваш вопрос или обратитесь к команде /help для примеров."
        )
        return
    
    # Формирование промпта для GPT-3.5-turbo
    prompt = f"Используя следующую информацию из базы знаний:\n\n"
    for i, context in enumerate(relevant_contexts, 1):
        prompt += f"{i}. Файл: {context['file_path']}\n"
        if context['class_name']:
            prompt += f"   Класс: {context['class_name']}\n"
        if context['method_name']:
            prompt += f"   Метод: {context['method_name']}\n"
        prompt += f"   Тип: {context['block_type']}\n"
        prompt += f"   Код:\n{context['text']}\n\n"
    
    prompt += f"Ответь на вопрос пользователя: {user_message}\n\n"
    prompt += "Ответ должен быть на русском языке, информативным и основываться только на предоставленной информации. "
    prompt += "Если информации недостаточно, укажи это. Включи в ответ информацию о файлах и методах, если это релевантно."

    # Обеспечиваем VPN подключение (если настроено)
    vpn_used = False
    if vpn_manager and not PROXY_URL:
        try:
            print("🔒 Проверка VPN подключения...")
            vpn_used = ensure_vpn_for_openai()
            
            # Если VPN не работает, пробуем принудительно перезапустить
            if not vpn_used:
                print("🔄 Попытка принудительного перезапуска VPN...")
                vpn_used = vpn_manager.force_restart_vpn()
                
            # Проверяем IP после VPN
            if vpn_used:
                ip = vpn_manager.get_vpn_ip()
                if ip:
                    print(f"🌍 IP через VPN: {ip}")
                else:
                    print("⚠️ Не удалось получить IP через VPN")
                
        except Exception as e:
            print(f"⚠️ Ошибка VPN: {e}")
            vpn_used = False

    # Отправка промпта в OpenAI API
    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL_NAME,
            messages=[
                {
                    "role": "system", 
                    "content": "Ты полезный ассистент, отвечающий на вопросы о коде и функциональности на основе предоставленной информации. Отвечай на русском языке."
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.7
        )
        generated_response = response.choices[0].message.content
        
        # Добавляем информацию об источниках
        sources_info = "\n\n📚 **Источники информации:**\n"
        for i, context in enumerate(relevant_contexts[:3], 1):
            similarity_percent = context['similarity'] * 100
            sources_info += f"{i}. 📁 {context['file_path']}"
            if context['class_name']:
                sources_info += f" (класс: {context['class_name']})"
            if context['method_name']:
                sources_info += f" (метод: {context['method_name']})"
            sources_info += f" - релевантность: {similarity_percent:.1f}%\n"
        
        # Добавляем информацию о VPN, если использовался
        if vpn_used:
            sources_info += "\n🔒 *Запрос выполнен через VPN*"
        
        full_response = generated_response + sources_info
        
    except Exception as e:
        full_response = f"❌ Произошла ошибка при обращении к OpenAI API: {str(e)}\n\nПопробуйте позже или обратитесь к команде /help."
    
    # Отправка сгенерированного ответа пользователю
    await message.answer(full_response) 