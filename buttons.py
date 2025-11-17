from telebot import types
import os
from dotenv import load_dotenv

load_dotenv()

def is_admin(user_id):
    ADMIN_IDS_STR = os.getenv('ADMIN_IDS', '')
    ADMIN_IDS = []
    
    if ADMIN_IDS_STR:
        ADMIN_IDS = list(map(int, ADMIN_IDS_STR.split(',')))
    
    return user_id in ADMIN_IDS

def get_admin_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_view_stats = types.KeyboardButton("Просмотреть статистику")
    keyboard.add(btn_view_stats)
    return keyboard

def get_client_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    
    btn_ai = types.KeyboardButton("AI Кинолог")
    btn_order = types.KeyboardButton("Записаться на консультацию")
    btn_about = types.KeyboardButton("О нас")
    
    keyboard.add(btn_ai, btn_order)
    keyboard.add(btn_about)
    return keyboard

def get_privacy_keyboard():
    """Инлайн-клавиатура для согласия с политикой"""
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✅ Согласен", callback_data="privacy_agree"),
        types.InlineKeyboardButton("❌ Не согласен", callback_data="privacy_disagree")
    )
    return markup
