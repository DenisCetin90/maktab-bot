import os
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
import telebot
from telebot import types

# 🔹 .env fayldan TOKEN ni yuklaymiz
load_dotenv("botuchuntn.env")
TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

# 🔹 Ma'lumotlar bazasi ulanishi
conn = sqlite3.connect("results.db", check_same_thread=False)
cursor = conn.cursor()

# 🔹 Jadval yaratish (agar mavjud bo‘lmasa)
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
        {"q": "10 + 12 =", "a": "22", "b": "23", "c": "21", "correct": "A"},
        {"q": "100 ÷ 10 =", "a": "5", "b": "10", "c": "15", "correct": "B"},
        {"q": "3 × 8 =", "a": "24", "b": "21", "c": "18", "correct": "A"},
        {"q": "5 × 5 =", "a": "10", "b": "20", "c": "25", "correct": "C"},
        {"q": "12 – 7 =", "a": "4", "b": "5", "c": "6", "correct": "B"},
    ],

    "Tarix": [
        {"q": "O‘zbekiston mustaqilligi qachon e’lon qilingan?", "a": "1990-yil", "b": "1991-yil", "c": "1992-yil", "correct": "B"},
        {"q": "Birinchi Prezidentimiz kim?", "a": "I. Karimov", "b": "Sh. Mirziyoyev", "c": "A. Qodiriy", "correct": "A"},
        {"q": "Amir Temur qaysi yillarda yashagan?", "a": "1336–1405", "b": "1405–1465", "c": "1200–1260", "correct": "A"},
        {"q": "O‘zbekiston BMTga qachon a’zo bo‘lgan?", "a": "1991-yil", "b": "1992-yil", "c": "1993-yil", "correct": "B"},
        {"q": "Qadimgi Xorazm qayerda joylashgan?", "a": "Janubiy O‘zbekiston", "b": "Shimoliy O‘zbekiston", "c": "G‘arbiy O‘zbekiston", "correct": "B"},
        {"q": "Temuriylar davlati poytaxti qayer?", "a": "Samarqand", "b": "Buxoro", "c": "Toshkent", "correct": "A"},
        {"q": "O‘zbekiston Respublikasi Konstitutsiyasi qachon qabul qilingan?", "a": "1991-yil", "b": "1992-yil", "c": "1993-yil", "correct": "B"},
        {"q": "Qo‘qon xonligini kim boshqargan?", "a": "Amir Temur", "b": "Muhammad Alixon", "c": "Shahrux", "correct": "B"},
        {"q": "1991-yilda qanday voqea bo‘lgan?", "a": "Mustaqillik e’lon qilingan", "b": "BMT tashkil topgan", "c": "Konstitutsiya qabul qilingan", "correct": "A"},
        {"q": "Samarqand necha ming yillik tarixga ega?", "a": "2000", "b": "2500", "c": "3000", "correct": "C"},
    ],

    "Ingliz tili": [
        {"q": "Translate: 'apple'", "a": "nok", "b": "olma", "c": "banan", "correct": "B"},
        {"q": "Which is a color?", "a": "red", "b": "cat", "c": "table", "correct": "A"},
        {"q": "I ___ a student.", "a": "am", "b": "is", "c": "are", "correct": "A"},
        {"q": "She ___ from London.", "a": "am", "b": "is", "c": "are", "correct": "B"},
        {"q": "We ___ happy.", "a": "is", "b": "am", "c": "are", "correct": "C"},
        {"q": "He has a ___ car.", "a": "red", "b": "book", "c": "run", "correct": "A"},
        {"q": "‘Dog’ means ___ in Uzbek.", "a": "it", "b": "mushuk", "c": "it", "correct": "B"},
        {"q": "How many letters are in 'cat'?", "a": "2", "b": "3", "c": "4", "correct": "B"},
        {"q": "What is opposite of 'cold'?", "a": "hot", "b": "wet", "c": "dry", "correct": "A"},
        {"q": "Choose the correct article: ___ apple", "a": "a", "b": "an", "c": "the", "correct": "B"},
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
        bot.send_message(chat_id, f"✅ Test tugadi!\n📊 Natija: {data['score']} / {len(subjects[subject])}\nFoiz: {foiz}%")

        # 🔹 Natijani bazaga yozamiz
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

# 🔹 Admin statistikasi (o‘zingizning Telegram ID’ingizni kiriting)
@bot.message_handler(commands=['stat'])
def show_stats(message):
    ADMIN_ID = "7386950903"  # 🧑‍💻 O‘zingizning Telegram ID’ingizni shu yerga yozing!
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

print("🤖 Bot ishga tushdi...")
bot.infinity_polling()
