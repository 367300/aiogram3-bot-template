from aiogram import types
from aiogram.filters.command import Command
from src.database import get_all_results
from aiogram import Router

router = Router()

@router.message(Command("stats"))
async def cmd_stats(message: types.Message):
    results = await get_all_results()
    if not results:
        await message.answer("Статистика пока пуста.")
        return
    text = "Статистика игроков (последний результат):\n"
    for idx, (username, correct) in enumerate(results, 1):
        text += f"{idx}. {username}: {correct}\n"
    await message.answer(text)