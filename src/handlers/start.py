from aiogram import types
from aiogram.filters.command import Command
from aiogram import F
from src.keyboards import main_menu_keyboard
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import Router

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Добро пожаловать в квиз!", reply_markup=main_menu_keyboard())

@router.message(F.text == "Статистика")
async def stats_button_handler(message: types.Message):
    from src.handlers.stats import cmd_stats
    await cmd_stats(message)