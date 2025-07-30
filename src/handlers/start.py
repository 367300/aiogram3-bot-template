from aiogram import types
from aiogram.filters.command import Command
from aiogram import F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from src.knowledge_base import get_knowledge_base_info
from aiogram import Router

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    """
    Обработчик команд /start и /help
    """
    knowledge_base_info = (
        "🤖 Добро пожаловать в AI-бот с базой знаний!\n\n"
        "Тематика базы знаний: Код и документация проектов.\n"
        f"📊 {get_knowledge_base_info()}\n\n"
        "💡 Пример запроса к базе: Как работает аутентификация?\n\n"
        "Просто напишите ваш вопрос, и я найду релевантную информацию в базе знаний!"
    )

    # Создание инлайн-клавиатуры с кнопкой
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💡 Пример запроса", callback_data="example_query")]
    ])

    await message.answer(knowledge_base_info, reply_markup=keyboard)

@router.message(Command("help"))
async def cmd_help(message: types.Message):
    """
    Обработчик команды /help
    """
    help_text = (
        "🔍 **Как использовать бота:**\n\n"
        "1. Просто напишите ваш вопрос о коде или функциональности\n"
        "2. Я найду релевантную информацию в базе знаний\n"
        "3. Сгенерирую ответ на основе найденной информации\n\n"
        "📝 **Примеры вопросов:**\n"
        "• Как работает аутентификация?\n"
        "• Где находится функция валидации?\n"
        "• Как обрабатываются ошибки?\n"
        "• Какие есть методы в классе UserView?\n\n"
        "💡 Нажмите кнопку 'Пример запроса' для демонстрации!"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💡 Пример запроса", callback_data="example_query")]
    ])
    
    await message.answer(help_text, reply_markup=keyboard)

@router.callback_query(F.data == "example_query")
async def process_example_query(callback_query: types.CallbackQuery):
    """
    Обработчик нажатия на инлайн-кнопку "Пример запроса"
    """
    await callback_query.answer()
    await callback_query.message.answer("Как работает аутентификация?")