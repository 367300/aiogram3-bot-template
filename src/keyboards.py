from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram import types

def main_menu_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Начать игру"))
    builder.add(types.KeyboardButton(text="Статистика"))
    return builder.as_markup(resize_keyboard=True)

def generate_options_keyboard(answer_options):
    builder = InlineKeyboardBuilder()
    for idx, option in enumerate(answer_options):
        builder.add(types.InlineKeyboardButton(
            text=option,
            callback_data=f"answer_{idx}")
        )
    builder.adjust(1)
    return builder.as_markup()