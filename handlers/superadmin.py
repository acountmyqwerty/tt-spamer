import logging
import json
import os
from aiogram import Dispatcher, types, F
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from config import ADMIN_IDS, SUPERADMIN_ID
from states import BotStates

logger = logging.getLogger(__name__)

ADMINS_FILE = "admins.json"


async def process_manage_admins(message: types.Message, state: FSMContext):
    """Обработчик для управления администраторами"""

    if message.from_user.id != SUPERADMIN_ID:
        await message.answer("🚫 Доступ запрещен. Управление администраторами доступно только главному админу.")
        return


    builder = ReplyKeyboardBuilder()
    buttons = [
        "➕ Добавить администратора",
        "➖ Удалить администратора",
        "📋 Список администраторов",
        "🔙 Вернуться в главное меню"
    ]

    for button in buttons:
        builder.add(types.KeyboardButton(text=button))


    builder.adjust(2)

    await message.answer(
        "👑 <b>Управление администраторами</b>\n\n"
        "Выберите действие из меню ниже:",
        reply_markup=builder.as_markup(resize_keyboard=True)
    )


async def process_add_admin(message: types.Message, state: FSMContext):
    """Обработчик для добавления нового администратора"""
    if message.from_user.id != SUPERADMIN_ID:
        return

    await message.answer(
        "👤 Введите ID пользователя Telegram, которого хотите добавить как администратора.\n\n"
        "ID должен быть числом, например: 1234567890\n"
        "Для отмены отправьте /cancel"
    )

    await state.set_state(BotStates.waiting_for_new_admin_id)


async def process_new_admin_input(message: types.Message, state: FSMContext):
    """Обработка ввода ID нового администратора"""
    if message.text == "/cancel":
        await state.clear()
        await message.answer("❌ Добавление администратора отменено")
        return

    try:
        admin_id = int(message.text.strip())


        if admin_id in ADMIN_IDS:
            await message.answer(f"⚠️ Пользователь с ID {admin_id} уже является администратором.")
            await state.clear()
            return


        ADMIN_IDS.append(admin_id)


        save_admins_to_file()

        await message.answer(f"✅ Администратор с ID {admin_id} успешно добавлен!")


        await state.clear()

    except ValueError:
        await message.answer("❌ Некорректный ID. Пожалуйста, введите числовой ID пользователя или отправьте /cancel.")


async def process_list_admins(message: types.Message):
    """Показать список всех администраторов"""
    if message.from_user.id != SUPERADMIN_ID:
        return

    admins_text = "👥 <b>Список администраторов:</b>\n\n"

    for i, admin_id in enumerate(ADMIN_IDS, 1):

        if admin_id == SUPERADMIN_ID:
            admins_text += f"{i}. {admin_id} (👑 Главный админ)\n"
        else:
            admins_text += f"{i}. {admin_id}\n"

    await message.answer(admins_text)


async def process_remove_admin(message: types.Message, state: FSMContext):
    """Обработчик для удаления администратора"""
    if message.from_user.id != SUPERADMIN_ID:
        return


    admins_to_remove = [admin_id for admin_id in ADMIN_IDS if admin_id != SUPERADMIN_ID]

    if not admins_to_remove:
        await message.answer("⚠️ В системе нет дополнительных администраторов для удаления.")
        return


    await state.update_data(admins_to_remove=admins_to_remove)

    admins_text = "❌ <b>Выберите ID администратора для удаления:</b>\n\n"

    for i, admin_id in enumerate(admins_to_remove, 1):
        admins_text += f"{i}. {admin_id}\n"

    admins_text += "\nВведите номер из списка или ID администратора.\nДля отмены отправьте /cancel"

    await message.answer(admins_text)

    await state.set_state(BotStates.waiting_for_admin_to_remove)


async def process_admin_to_remove(message: types.Message, state: FSMContext):
    """Обработка выбора администратора для удаления"""
    if message.text == "/cancel":
        await state.clear()
        await message.answer("❌ Удаление администратора отменено")
        return


    data = await state.get_data()
    admins_to_remove = data.get('admins_to_remove', [])

    try:
        input_text = message.text.strip()


        try:

            index = int(input_text) - 1
            if 0 <= index < len(admins_to_remove):
                admin_id_to_remove = admins_to_remove[index]
            else:
                # Если не порядковый номер, то возможно это сам ID
                admin_id_to_remove = int(input_text)
                if admin_id_to_remove not in admins_to_remove:
                    raise ValueError("ID not in list")
        except ValueError:
            await message.answer("❌ Некорректный ввод. Пожалуйста, введите номер из списка или ID администратора.")
            return


        if admin_id_to_remove in ADMIN_IDS:
            ADMIN_IDS.remove(admin_id_to_remove)


            save_admins_to_file()

            await message.answer(f"✅ Администратор с ID {admin_id_to_remove} успешно удален!")
        else:
            await message.answer(f"⚠️ Администратор с ID {admin_id_to_remove} не найден в списке.")


        await state.clear()

    except Exception as e:
        logger.error(f"Error removing admin: {e}")
        await message.answer(
            "❌ Произошла ошибка при удалении администратора. Попробуйте еще раз или отправьте /cancel.")


async def process_back_to_main_menu(message: types.Message, state: FSMContext):
    """Возврат в главное меню"""
    from handlers.commands import cmd_start
    await cmd_start(message)
    await state.clear()


def save_admins_to_file():
    """Сохранение списка администраторов в файл"""
    try:
        with open(ADMINS_FILE, 'w') as f:
            json.dump(list(ADMIN_IDS), f)
        logger.info(f"Admins list saved to {ADMINS_FILE}")
        return True
    except Exception as e:
        logger.error(f"Error saving admins list: {e}")
        return False


def load_admins_from_file():
    """Загрузка списка администраторов из файла"""
    try:
        if os.path.exists(ADMINS_FILE):
            with open(ADMINS_FILE, 'r') as f:
                admins = json.load(f)
                logger.info(f"Loaded {len(admins)} admin IDs from file")
                return admins
    except Exception as e:
        logger.error(f"Error loading admins list: {e}")
    return None


try:
    saved_admins = load_admins_from_file()
    if saved_admins:
        # Обновляем список, сохраняя SUPERADMIN_ID первым
        updated_admins = [SUPERADMIN_ID]
        for admin_id in saved_admins:
            # Предотвращаем дублирование SUPERADMIN_ID
            if admin_id != SUPERADMIN_ID and admin_id not in updated_admins:
                updated_admins.append(admin_id)

        ADMIN_IDS.clear()
        ADMIN_IDS.extend(updated_admins)
        logger.info(f"Updated ADMIN_IDS with {len(ADMIN_IDS)} admin IDs from file")
except Exception as e:
    logger.error(f"Error initializing admins from file: {e}")


def register_handlers(dp: Dispatcher):
    """Регистрация обработчиков управления администраторами"""

    dp.message.register(
        process_manage_admins,
        F.text == "👑 Управление админами"
    )

    dp.message.register(
        process_add_admin,
        F.text == "➕ Добавить администратора"
    )
    dp.message.register(
        process_new_admin_input,
        BotStates.waiting_for_new_admin_id
    )

    dp.message.register(
        process_list_admins,
        F.text == "📋 Список администраторов"
    )

    dp.message.register(
        process_remove_admin,
        F.text == "➖ Удалить администратора"
    )
    dp.message.register(
        process_admin_to_remove,
        BotStates.waiting_for_admin_to_remove
    )

    dp.message.register(
        process_back_to_main_menu,
        F.text == "🔙 Вернуться в главное меню"
    )