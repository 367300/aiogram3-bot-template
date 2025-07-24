#@title Полный код бота для самоконтроля
import aiosqlite
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram import F

from decouple import config

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

# Замените "YOUR_BOT_TOKEN" на токен, который вы получили от BotFather
API_TOKEN = config('API_TOKEN_TG', default=False)

if (not API_TOKEN):
    logging.error("Необходимо указать токен для бота!")
    exit()

# Объект бота
bot = Bot(token=API_TOKEN)
# Диспетчер
dp = Dispatcher()

# Зададим имя базы данных
DB_NAME = 'quiz_bot.db'


# Структура квиза
quiz_data = [
    {
        'question': 'Что такое Python?',
        'options': ['Язык программирования', 'Тип данных', 'Музыкальный инструмент', 'Змея на английском'],
        'correct_option': 0
    },
    {
        'question': 'Какой тип данных используется для хранения целых чисел?',
        'options': ['int', 'float', 'str', 'natural'],
        'correct_option': 0
    },
    {
        'question': 'Какой метод используется для добавления элемента в список?',
        'options': ['append()', 'add()', 'insert()', 'push()'],
        'correct_option': 0
    },
    {
        'question': 'Какой символ используется для комментария в Python?',
        'options': ['#', '//', '--', '/*'],
        'correct_option': 0
    },
    {
        'question': 'Какой результат выражения 2 ** 3?',
        'options': ['6', '8', '9', '5'],
        'correct_option': 1
    },
    {
        'question': 'Какой модуль используется для работы со случайными числами?',
        'options': ['random', 'math', 'os', 'sys'],
        'correct_option': 0
    },
    {
        'question': 'Какой метод строки делает все буквы заглавными?',
        'options': ['upper()', 'capitalize()', 'title()', 'big()'],
        'correct_option': 0
    },
    {
        'question': 'Какой оператор используется для проверки равенства?',
        'options': ['=', '==', '!=', 'equals'],
        'correct_option': 1
    },
    {
        'question': 'Какой тип данных предназначен для хранения True/False?',
        'options': ['bool', 'int', 'str', 'float'],
        'correct_option': 0
    },
    {
        'question': 'Какой цикл используется для перебора элементов списка?',
        'options': ['for', 'while', 'loop', 'repeat'],
        'correct_option': 0
    },
]



def generate_options_keyboard(answer_options):
    builder = InlineKeyboardBuilder()

    for idx, option in enumerate(answer_options):
        builder.add(types.InlineKeyboardButton(
            text=option,
            callback_data=f"answer_{idx}")
        )

    builder.adjust(1)
    return builder.as_markup()


@dp.callback_query(F.data.startswith("answer_"))
async def answer_handler(callback: types.CallbackQuery):
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    current_question_index = await get_quiz_index(callback.from_user.id)
    correct_option = quiz_data[current_question_index]['correct_option']
    options = quiz_data[current_question_index]['options']
    selected_idx = int(callback.data.split('_')[1])
    selected_text = options[selected_idx]

    # Сообщаем пользователю, что он выбрал
    await callback.message.answer(f"Вы выбрали: {selected_text}")

    if selected_idx == correct_option:
        await callback.message.answer("Верно!")
    else:
        await callback.message.answer(f"Неправильно. Правильный ответ: {quiz_data[current_question_index]['options'][correct_option]}")

    # Обновление номера текущего вопроса в базе данных
    current_question_index += 1
    await update_quiz_index(callback.from_user.id, current_question_index)

    if current_question_index < len(quiz_data):
        await get_question(callback.message, callback.from_user.id)
    else:
        await callback.message.answer("Это был последний вопрос. Квиз завершен!")


# Хэндлер на команду /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Начать игру"))
    await message.answer("Добро пожаловать в квиз!", reply_markup=builder.as_markup(resize_keyboard=True))


async def get_question(message, user_id):
    current_question_index = await get_quiz_index(user_id)
    correct_index = quiz_data[current_question_index]['correct_option']
    opts = quiz_data[current_question_index]['options']
    kb = generate_options_keyboard(opts)
    await message.answer(f"{quiz_data[current_question_index]['question']}", reply_markup=kb)


async def new_quiz(message):
    user_id = message.from_user.id
    current_question_index = 0
    await update_quiz_index(user_id, current_question_index)
    await get_question(message, user_id)


async def get_quiz_index(user_id):
     # Подключаемся к базе данных
     async with aiosqlite.connect(DB_NAME) as db:
        # Получаем запись для заданного пользователя
        async with db.execute('SELECT question_index FROM quiz_state WHERE user_id = (?)', (user_id, )) as cursor:
            # Возвращаем результат
            results = await cursor.fetchone()
            if results is not None:
                return results[0]
            else:
                return 0


async def update_quiz_index(user_id, index):
    # Создаем соединение с базой данных (если она не существует, она будет создана)
    async with aiosqlite.connect(DB_NAME) as db:
        # Вставляем новую запись или заменяем ее, если с данным user_id уже существует
        await db.execute('INSERT OR REPLACE INTO quiz_state (user_id, question_index) VALUES (?, ?)', (user_id, index))
        # Сохраняем изменения
        await db.commit()


# Хэндлер на команду /quiz
@dp.message(F.text=="Начать игру")
@dp.message(Command("quiz"))
async def cmd_quiz(message: types.Message):

    await message.answer(f"Давайте начнем квиз!")
    await new_quiz(message)



async def create_table():
    # Создаем соединение с базой данных (если она не существует, она будет создана)
    async with aiosqlite.connect(DB_NAME) as db:
        # Создаем таблицу
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_state (user_id INTEGER PRIMARY KEY, question_index INTEGER)''')
        # Сохраняем изменения
        await db.commit()



# Запуск процесса поллинга новых апдейтов
async def main():

    # Запускаем создание таблицы базы данных
    await create_table()

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())