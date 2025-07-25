from aiogram import types, F
from aiogram.filters.command import Command
from src.keyboards import generate_options_keyboard
from src.database import get_quiz_index, update_quiz_index, get_user_result, save_quiz_result, get_question_by_id, get_questions_count
from aiogram import Router
from aiogram.exceptions import TelegramBadRequest, TelegramNetworkError

router = Router()

def is_readable(name):
    return bool(name and name.strip() and name.lower() != 'none')

async def get_question(message, user_id):
    current_question_index = await get_quiz_index(user_id)
    question_data = await get_question_by_id(current_question_index)
    if not question_data:
        await message.answer("Вопрос не найден.")
        return
    opts = question_data['options']
    kb = generate_options_keyboard(opts)
    await message.answer(f"{question_data['question']}", reply_markup=kb)

async def new_quiz(message):
    user_id = message.from_user.id
    current_question_index = 0

    # Сначала пробуем отправить картинку по ссылке
    image_url = "https://storage.yandexcloud.net/telegram-bot-aiogram/3704bcfd-fb30-4627-8641-66cf48ce8f23.jpg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=YCAJEnX8GFFhSnCMaZw1xWQ76%2F20250725%2Fru-central1%2Fs3%2Faws4_request&X-Amz-Date=20250725T192649Z&X-Amz-Expires=2592000&X-Amz-Signature=d5ea496464f4f744f68baa1f4a45eec65ac42bb1f023dfd44713dc51ba820733&X-Amz-SignedHeaders=host"
    local_path = "img/3704bcfd-fb30-4627-8641-66cf48ce8f23.jpg"

    try:
        await message.answer_photo(image_url, caption="Добро пожаловать в квиз!")
    except (TelegramBadRequest, TelegramNetworkError):
        # Если не удалось — отправляем локальный файл
        with open(local_path, "rb") as photo:
            await message.answer_photo(photo, caption="Добро пожаловать в квиз!")

    await update_quiz_index(user_id, current_question_index)
    await get_question(message, user_id)

@router.message(F.text == "Начать игру")
@router.message(Command("quiz"))
async def cmd_quiz(message: types.Message):
    await message.answer(f"Давайте начнем квиз!")
    await new_quiz(message)

@router.callback_query(F.data.startswith("answer_"))
async def answer_handler(callback: types.CallbackQuery):
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )
    user_id = callback.from_user.id
    username = callback.from_user.username
    full_name = callback.from_user.full_name
    display_name = full_name if is_readable(full_name) else 'Неизвестный'
    if is_readable(username):
        masked = username[:3] + '*' * (len(username) - 3) if len(username) > 3 else username
        display_name = f"{display_name} ({masked})"
    current_question_index = await get_quiz_index(user_id)
    question_data = await get_question_by_id(current_question_index)
    if not question_data:
        await callback.message.answer("Вопрос не найден.")
        return
    correct_option = question_data['correct_option']
    options = question_data['options']
    selected_idx = int(callback.data.split('_')[1])
    selected_text = options[selected_idx]
    correct_count = await get_user_result(user_id) or 0
    if current_question_index == 0:
        correct_count = 0
    await callback.message.answer(f"Вы выбрали: {selected_text}")
    if selected_idx == correct_option:
        await callback.message.answer("Верно!")
        correct_count += 1
    else:
        await callback.message.answer(f"Неправильно. Правильный ответ: {options[correct_option]}")
    current_question_index += 1
    await update_quiz_index(user_id, current_question_index)
    total_questions = await get_questions_count()
    if current_question_index < total_questions:
        await save_quiz_result(user_id, display_name, correct_count)
        await get_question(callback.message, user_id)
    else:
        await save_quiz_result(user_id, display_name, correct_count)
        await callback.message.answer(f"Это был последний вопрос. Квиз завершен!\nВаш результат: {correct_count} из {total_questions}")