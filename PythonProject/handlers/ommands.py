import logging
from aiogram import Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from config import ADMIN_IDS, SUPERADMIN_ID

logger = logging.getLogger(__name__)


async def cmd_start(message: types.Message):
    """Start command handler - entry point to the bot"""
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("🚫 Доступ запрещен. Этот бот только для администраторов.")
        return

    builder = ReplyKeyboardBuilder()
    buttons = [
        "📌 Добавить cookies",
        "🔍 Изменить запрос",
        "💬 Изменить комментарий",
        "🔢 Изменить количество",
        "⏱ Изменить задержку",
        "▶️ Начать комментирование",
        "🛑 Остановить бота"
    ]

    if message.from_user.id == SUPERADMIN_ID:
        buttons.append("👑 Управление админами")

    for button in buttons:
        builder.add(types.KeyboardButton(text=button))

    builder.adjust(2)

    await message.answer(
        "🤖 <b>TikTok Комментирующий Бот</b>\n\n"
        "Добро пожаловать в бота, который помогает автоматизировать комментирование видео в TikTok.\n\n"
        "Выберите действие из меню ниже:",
        reply_markup=builder.as_markup(resize_keyboard=True)
    )


async def cmd_help(message: types.Message):
    """Help command handler"""
    if message.from_user.id not in ADMIN_IDS:
        return

    help_text = (
        "🤖 <b>TikTok Комментирующий Бот - Помощь</b>\n\n"
        "<b>Команды:</b>\n"
        "/start - Открыть главное меню\n"
        "/help - Показать это сообщение\n"
        "/status - Показать текущий статус и настройки\n\n"
        "<b>Как использовать:</b>\n"
        "1. Добавьте cookies от TikTok\n"
        "2. Установите поисковый запрос для поиска видео\n"
        "3. Настройте текст комментария\n"
        "4. Настройте количество видео и задержку\n"
        "5. Запустите процесс комментирования\n\n"
        "<b>Примечание:</b> Вам понадобятся действующие cookies TikTok для работы."
    )

    await message.answer(help_text)


async def cmd_status(message: types.Message, state: FSMContext):
    """Status command handler - shows current bot settings"""
    if message.from_user.id not in ADMIN_IDS:
        return

    data = await state.get_data()

    cookies_status = "✅ Установлены" if data.get('cookies') else "❌ Не установлены"
    search_query = data.get('search_query', "Не установлен")
    comment_text = data.get('comment_text', "Не установлен")
    comments_count = data.get('comments_count', 5)
    delay = data.get('delay', 1.0)
    delay_mode = data.get('delay_mode', 'fixed')
    delay_info = f"{delay}с (фикс.)" if delay_mode == 'fixed' else f"{delay}с (случайно ±50%)"
    is_running = "Запущен" if data.get('is_running', False) else "Остановлен"

    status_text = (
        "🤖 <b>TikTok Комментирующий Бот - Статус</b>\n\n"
        f"<b>Статус бота:</b> {is_running}\n\n"
        f"<b>Cookies:</b> {cookies_status}\n"
        f"<b>Поисковый запрос:</b> {search_query}\n"
        f"<b>Текст комментария:</b> {comment_text}\n"
        f"<b>Количество видео:</b> {comments_count}\n"
        f"<b>Задержка:</b> {delay_info}\n"
    )

    await message.answer(status_text)


def register_handlers(dp: Dispatcher):
    """Register all command handlers"""
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(cmd_help, Command("help"))
    dp.message.register(cmd_status, Command("status"))
