import logging
import asyncio
from aiogram import Bot, Dispatcher
from src.config import API_TOKEN
from src.handlers import start, ai_handler
from src.database import create_table
from src.knowledge_base import initialize_knowledge_base

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

def setup_routers():
    dp.include_router(start.router)
    dp.include_router(ai_handler.router)

async def main():
    await create_table()
    await initialize_knowledge_base()
    setup_routers()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())