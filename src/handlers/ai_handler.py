from aiogram import types, F
from aiogram import Router
from openai import OpenAI
from src.config import OPENAI_API_KEY, OPENAI_MODEL_NAME
from src.knowledge_base import get_relevant_contexts

router = Router()

# Инициализация клиента OpenAI
client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

print("🌐 OpenAI клиент инициализирован")

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
        
        full_response = generated_response + sources_info
        
    except Exception as e:
        full_response = f"❌ Произошла ошибка при обращении к OpenAI API: {str(e)}\n\nПопробуйте позже или обратитесь к команде /help."
    
    # Отправка сгенерированного ответа пользователю
    await message.answer(full_response) 