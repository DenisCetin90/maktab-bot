import os
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
import telebot
from telebot import types
from flask import Flask

# 🔹 Flask web-server (Render uni tirik saqlaydi)
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Maktab bot is running on Render!"

# 🔹 Tokenni o‘qish
load_dotenv("botuchuntn.env")
TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

# 🔹 Ma'lumotlar bazasi ulanishi
conn = sqlite3.connect("results.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS results (
    user_id INTEGER,
    subject TEXT,
    score INTEGER,
    total INTEGER,
    date TEXT
)
""")
conn.commit()

# 📚 Fanlar va savollar
subjects = {
    "Matematika": [
        {"q": "2 + 3 =", "a": "4", "b": "5", "c": "6", "correct": "B"},
        {"q": "7 - 2 =", "a": "4", "b": "5", "c": "6", "correct": "B"},
        {"q": "9 × 3 =", "a": "27", "b": "26", "c": "28", "correct": "A"},
        {"q": "15 ÷ 3 =", "a": "6", "b": "5", "c": "4", "correct": "B"},
        {"q": "4² =", "a": "8", "b": "16", "c": "12", "correct": "B"},
    ],

    "Tarix": [
        {"q": "O‘zbekiston mustaqilligi qachon e’lon qilingan?", "a": "1990-yil", "b": "1991-yil", "c": "1992-yil", "correct": "B"},
        {"q": "Birinchi Prezidentimiz kim?", "a": "I. Karimov", "b": "Sh. Mirziyoyev", "c": "A. Qodiriy", "correct": "A"},
    ],

    "Ingliz tili": [
        {"q": "Translate: 'apple'", "a": "nok", "b": "olma", "c": "banan", "correct": "B"},
        {"q": "Which is a color?", "a": "red", "b": "cat", "c": "table", "correct": "A"},
    ],
}

# 🧠 Foydalanuvchi holati
user_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for subject in subjects.keys():
        markup.add(subject)
    bot.send_message(message.chat.id, "Assalomu alaykum! Fanni tanlang 👇", reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text in subjects.keys())
def select_subject(message):
    user_data[message.chat.id] = {"subject": message.text, "index": 0, "score": 0}
    send_question(message.chat.id)

def send_question(chat_id):
    data = user_data[chat_id]
    subject = data["subject"]
    index = data["index"]

    if index >= len(subjects[subject]):
        foiz = round(data['score'] / len(subjects[subject]) * 100)
        baho = (
            "🌟 A’lo!" if foiz >= 90 else
            "😊 Yaxshi!" if foiz >= 70 else
            "🤔 Yana urinib ko‘ring!"
        )
        bot.send_message(chat_id, f"✅ Test tugadi!\n📊 Natija: {data['score']} / {len(subjects[subject])}\nFoiz: {foiz}%\n{baho}")

        cursor.execute("INSERT INTO results VALUES (?, ?, ?, ?, ?)",
                       (chat_id, subject, data['score'], len(subjects[subject]), datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        return

    question = subjects[subject][index]
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("A", callback_data="A"),
        types.InlineKeyboardButton("B", callback_data="B"),
        types.InlineKeyboardButton("C", callback_data="C")
    )
    text = f"📘 {subject} fani\n\n{index + 1}-savol:\n{question['q']}\nA) {question['a']}\nB) {question['b']}\nC) {question['c']}"
    bot.send_message(chat_id, text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def check_answer(call):
    chat_id = call.message.chat.id
    data = user_data[chat_id]
    subject = data["subject"]
    index = data["index"]
    question = subjects[subject][index]

    if call.data == question["correct"]:
        data["score"] += 1
        bot.answer_callback_query(call.id, "✅ To‘g‘ri!")
    else:
        bot.answer_callback_query(call.id, f"❌ Noto‘g‘ri! To‘g‘ri javob: {question['correct']}")

    data["index"] += 1
    send_question(chat_id)

# 🔹 Admin uchun statistika
@bot.message_handler(commands=['stat'])
def show_stats(message):
    ADMIN_ID = "123456789"  # O‘zingizning Telegram ID’ingizni yozing
    if str(message.chat.id) != ADMIN_ID:
        bot.send_message(message.chat.id, "⛔ Sizda ruxsat yo‘q.")
        return

    cursor.execute("SELECT subject, COUNT(*), AVG(score*1.0/total)*100 FROM results GROUP BY subject")
    rows = cursor.fetchall()
    if not rows:
        bot.send_message(message.chat.id, "📭 Hozircha hech kim test yechmagan.")
        return

    text = "📊 Test natijalari:\n\n"
    for row in rows:
        subject, count, avg_percent = row
        text += f"📘 {subject}\n🧍‍♂️ Ishtirokchilar: {count}\n💯 O‘rtacha foiz: {avg_percent:.1f}%\n\n"
    bot.send_message(message.chat.id, text)

# 🔹 Botni ishga tushirish
print("🤖 Bot ishga tushdi...")

import threading
t = threading.Thread(target=lambda: bot.infinity_polling(), daemon=True)
t.start()

# 🔹 Flask serverni ishga tushirish
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
