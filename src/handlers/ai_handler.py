from aiogram import types, F
from aiogram import Router
from openai import OpenAI
from src.config import OPENAI_API_KEY, OPENAI_MODEL_NAME
from src.knowledge_base import get_relevant_contexts
import re

router = Router()

# Инициализация клиента OpenAI
client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

print("🌐 OpenAI клиент инициализирован")

def escape_markdown_v2(text: str) -> str:
    """
    Экранирует специальные символы для MarkdownV2
    """
    escape_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in escape_chars:
        text = text.replace(char, f'\\{char}')
    return text

def convert_headers_to_bold(text: str) -> str:
    """
    Заменяет markdown заголовки (# ## ### ####) на жирный текст
    """
    # Регулярное выражение для поиска заголовков в начале строки
    # Поддерживает от 1 до 4 символов # в начале строки
    header_pattern = r'^(#{1,4})\s+(.+)$'
    
    def replace_header(match):
        level = len(match.group(1))  # количество символов #
        content = match.group(2).strip()  # содержимое заголовка
        return f"**{content}**"
    
    # Разбиваем текст на строки, обрабатываем каждую и собираем обратно
    lines = text.split('\n')
    processed_lines = []
    
    for line in lines:
        if re.match(header_pattern, line):
            # Заменяем заголовок на жирный текст
            processed_line = re.sub(header_pattern, replace_header, line)
            processed_lines.append(processed_line)
        else:
            processed_lines.append(line)
    
    return '\n'.join(processed_lines)

async def send_markdown_message(message: types.Message, text: str):
    """
    Безопасно отправляет сообщение с markdown разметкой
    """
    # Сначала конвертируем заголовки в жирный текст
    processed_text = convert_headers_to_bold(text)
    
    try:
        # Сначала пробуем отправить с MarkdownV2
        await message.answer(processed_text, parse_mode="MarkdownV2")
    except Exception as e:
        try:
            # Если не получилось, пробуем с обычным Markdown
            await message.answer(processed_text, parse_mode="Markdown")
        except Exception as e2:
            # Если и это не работает, отправляем как обычный текст
            # Убираем markdown разметку
            clean_text = re.sub(r'\*\*(.*?)\*\*', r'\1', processed_text)  # Убираем **жирный**
            clean_text = re.sub(r'\*(.*?)\*', r'\1', clean_text)  # Убираем *курсив*
            clean_text = re.sub(r'`(.*?)`', r'\1', clean_text)  # Убираем `код`
            clean_text = re.sub(r'```(.*?)```', r'\1', clean_text, flags=re.DOTALL)  # Убираем блоки кода
            await message.answer(clean_text)

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
    prompt += "Если информации недостаточно, укажи это. Включи в ответ информацию о файлах и методах, если это релевантно. "

    # Отправка промпта в OpenAI API
    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL_NAME,
            messages=[
                {
                    "role": "system", 
                    "content": "Ты полезный ассистент, отвечающий на вопросы о коде и функциональности на основе предоставленной информации. Отвечай на русском языке. Используй markdown разметку для форматирования: **жирный текст**, *курсив*, `код`, ```блоки кода```"
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.7
        )
        generated_response = response.choices[0].message.content
        
        # Добавляем информацию об источниках
        sources_info = "\n\n📚 *Источники информации:*\n"
        for i, context in enumerate(relevant_contexts[:3], 1):
            similarity_percent = context['similarity'] * 100
            sources_info += f"{i}\\. 📁 `{context['file_path']}`"
            if context['class_name']:
                sources_info += f" \\(класс: `{context['class_name']}`\\)"
            if context['method_name']:
                sources_info += f" \\(метод: `{context['method_name']}`\\)"
            sources_info += f" \\- релевантность: *{similarity_percent:.1f}%*\n"
        
        full_response = generated_response + sources_info
        
    except Exception as e:
        full_response = f"❌ Произошла ошибка при обращении к API LLM: {str(e)}\n\nПопробуйте позже или обратитесь к команде /help."
    
    # Отправка сгенерированного ответа пользователю с поддержкой markdown
    await send_markdown_message(message, full_response) 