from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

# from app.database.requests import get_users

main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text= 'Аккаунт')],
    [KeyboardButton(text= 'Персональные задачи')],
    [KeyboardButton(text= 'Создать персональную задачу')]
], resize_keyboard=True)

async def hello_buttons():
    hello_kb = InlineKeyboardBuilder()
    
    hello_kb.add(InlineKeyboardButton(text='Начать работу', callback_data='start'))
    
    return hello_kb.adjust(2).as_markup()

async def options_task(task_id):
    option_kb = InlineKeyboardBuilder()
    
    option_kb.add(InlineKeyboardButton(text="Выполнено", callback_data=f'done_{task_id}'))
    option_kb.add(InlineKeyboardButton(text="В работе", callback_data=f'inwork_{task_id}'))
    option_kb.add(InlineKeyboardButton(text="Удалить", callback_data=f'delete_{task_id}'))
    
    return option_kb.adjust(1).as_markup()
# async def hello():
#     users_kb = InlineKeyboardBuilder()
    
#     users = await get_users()
#     for user in users:
#         users_kb.add(InlineKeyboardButton(text=user.name, callback_data=f'user_{user.user_id}'))
#     return users_kb.adjust(2).as_markup()