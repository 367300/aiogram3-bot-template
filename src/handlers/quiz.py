from aiogram import types, F
from aiogram.filters.command import Command
from src.quiz_data import quiz_data
from src.keyboards import generate_options_keyboard
from src.database import get_quiz_index, update_quiz_index, get_user_result, save_quiz_result
from aiogram import Router

router = Router()

def is_readable(name):
    return bool(name and name.strip() and name.lower() != 'none')

async def get_question(message, user_id):
    current_question_index = await get_quiz_index(user_id)
    opts = quiz_data[current_question_index]['options']
    kb = generate_options_keyboard(opts)
    await message.answer(f"{quiz_data[current_question_index]['question']}", reply_markup=kb)

async def new_quiz(message):
    user_id = message.from_user.id
    current_question_index = 0
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
    if is_readable(full_name):
        display_name = full_name
    else:
        display_name = 'Неизвестный'
    if is_readable(username):
        if len(username) > 3:
            masked = username[:3] + '*' * (len(username) - 3)
        else:
            masked = username
        display_name = f"{display_name} ({masked})"
    current_question_index = await get_quiz_index(user_id)
    correct_option = quiz_data[current_question_index]['correct_option']
    options = quiz_data[current_question_index]['options']
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
    if current_question_index < len(quiz_data):
        await save_quiz_result(user_id, display_name, correct_count)
        await get_question(callback.message, user_id)
    else:
        await save_quiz_result(user_id, display_name, correct_count)
        await callback.message.answer(f"Это был последний вопрос. Квиз завершен!\nВаш результат: {correct_count} из {len(quiz_data)}")