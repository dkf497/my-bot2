import telebot
from config import BOT_TOKEN, DB_PATH
from db import init_db, add_ticket
from faq import get_faq_answer
import sqlite3


ADMIN_USERNAMES = ["@Maks"]

bot = telebot.TeleBot(BOT_TOKEN)
init_db()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(
        message.chat.id,
        f"Привет, {message.from_user.first_name}! 👋\n"
        "Я бот техподдержки магазина 'Продаём всё на свете'.\n"
        "Задай свой вопрос — попробую помочь."
    )

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(
        message.chat.id,
        "📌 Просто напиши свой вопрос. Если не найду ответ, передам его нужному отделу."
    )

@bot.message_handler(func=lambda msg: True, content_types=['text'])
def handle_message(message):
    
    if message.text.startswith("/reply"):
        return

    user_id = message.from_user.id
    user_name = message.from_user.username or message.from_user.first_name
    text = message.text.strip()

   
    print(f"Новый запрос от {user_name} (ID: {user_id}): {text}")

    answer = get_faq_answer(text)
    if answer:
        bot.send_message(message.chat.id, answer)
        return

    
    department = 'программисты' if any(k in text.lower() for k in ['сайт', 'оплата', 'ошибка']) else 'отдел продаж'
    ticket_id = add_ticket(user_id, user_name, department, text)

    bot.send_message(
        message.chat.id,
        f"✅ Ваш запрос передан в {department}. Номер тикета: #{ticket_id}. Наш специалист скоро ответит!"
    )


@bot.message_handler(commands=['reply'])
def reply_to_user(message):
    
    if message.from_user.username not in ADMIN_USERNAMES:
        bot.send_message(message.chat.id, "⛔ У вас нет доступа к этой команде.")
        return

    try:
        parts = message.text.split(maxsplit=2)
        ticket_id = int(parts[1])
        reply_text = parts[2]

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM tickets WHERE id = ?", (ticket_id,))
        row = cur.fetchone()
        conn.close()

        if not row:
            bot.send_message(message.chat.id, "❌ Тикет не найден.")
            return

        user_id = row[0]
        bot.send_message(user_id, f"💬 Ответ от отдела продаж:\n{reply_text}")
        bot.send_message(message.chat.id, f"✅ Сообщение отправлено пользователю (тикет #{ticket_id}).")

    except (IndexError, ValueError):
        bot.send_message(message.chat.id, "Использование: /reply <ticket_id> <сообщение>")

print("✅ Бот запущен...")
bot.polling(none_stop=True)
