import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from config import BOT_TOKEN
import asyncio
from data_store import user_data

logger = logging.getLogger(__name__)

# Initialize bot and dispatcher
bot = Bot(token="BOT_TOKEN", default=DefaultBotProperties(parse_mode=HTML))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


def register_handlers(dispatcher):
    PythonProject.commands.register_handlers(dispatcher)
    PythonProject.admin.register_handlers(dispatcher)
    PythonProject.cookies.register_handlers(dispatcher)
    PythonProject.parameters.register_handlers(dispatcher)
    PythonProject.superadmin.register_handlers(dispatcher)


async def main():
    # Register all handlers
    register_handlers(dp)

    # Start the bot
    logger.info("Bot is starting...")
    await dp.start_polling(bot, skip_updates=True)


def start_bot():
    """Start the bot using asyncio"""
    asyncio.run(main())