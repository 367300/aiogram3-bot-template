import logging
import asyncio
from aiogram import Bot, Dispatcher
from src.config import API_TOKEN
from src.handlers import start, quiz, stats
from src.database import create_table, create_results_table

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

def setup_routers():
    dp.include_router(start.router)
    dp.include_router(quiz.router)
    dp.include_router(stats.router)

async def main():
    await create_table()
    await create_results_table()
    setup_routers()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())