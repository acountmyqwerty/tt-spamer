import os

# Bot configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "7951098936:AAGd99BRsf5IibjpmAYjhsZoBQogMdsFItY")
# Суперадмин ID (имеет особые права)
SUPERADMIN_ID = int(os.getenv("ADMIN_ID", "801253820"))
# Список ID администраторов
ADMIN_IDS = {
    SUPERADMIN_ID,
    801253820
}
ADMIN_ID = SUPERADMIN_ID

HEADLESS = True
BROWSER_LANGUAGE = "ru"

# Default parameters
DEFAULT_DELAY = 1.0
DEFAULT_DELAY_MODE = "fixed"  # 'fixed' or 'random'
DEFAULT_COMMENTS_COUNT = 5