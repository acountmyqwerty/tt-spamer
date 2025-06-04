from aiogram.fsm.state import State, StatesGroup

class BotStates(StatesGroup):
    """States for the TikTok comment bot"""
    waiting_for_cookies = State()
    waiting_for_search_query = State()
    waiting_for_comment = State()
    waiting_for_comments_count = State()
    waiting_for_new_admin_id = State()
    waiting_for_admin_to_remove = State()
