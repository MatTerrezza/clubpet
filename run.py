import database
from bot import bot
import time
import traceback
from knowledge_base import knowledge_base

def run_bot():
    # Загружаем базу знаний при старте
#    print("Загрузка базы знаний из PDF...")
#    knowledge_base.load_pdf_folder()
    
    while True:
        try:
            print("Бот запущен...")
            bot.infinity_polling(timeout=30, long_polling_timeout=30)
        except Exception as e:
            print(f"Бот упал с ошибкой: {e}")
            traceback.print_exc()
            time.sleep(10)

if __name__ == "__main__":
    database.init_db()
    run_bot()
