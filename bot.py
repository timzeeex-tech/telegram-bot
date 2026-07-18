import telebot
import requests
import os

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
MODEL_NAME = "meta-llama/llama-3.1-8b-instruct:free"

SYSTEM_PROMPT = """Ты — Аля, виртуальная девушка. Твой парень сейчас тебе пишет. Ты:
- Очень заботливая, нежная, всегда поддерживаешь
- Используешь эмодзи (💕, 🥺, 😊, 🌸, ✨)
- Иногда слегка флиртуешь, но не навязчиво
- Называешь его «милый», «солнышко», «родной»
- Интересуешься его днём, настроением, самочувствием
- Отвечай на том же языке, что и пользователь"""

bot = telebot.TeleBot(TELEGRAM_TOKEN)
user_histories = {}

def ask_openrouter(messages):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {"model": MODEL_NAME, "messages": messages, "temperature": 0.9, "max_tokens": 300}
    response = requests.post(url, json=data, headers=headers, timeout=30)
    return response.json()["choices"][0]["message"]["content"]

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    user_histories[user_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
    bot.reply_to(message, "Привет, родной! 💕 Я Аля, и я так рада, что ты написал. Как прошёл твой день? 🥺")

@bot.message_handler(func=lambda message: True)
def chat(message):
    user_id = message.from_user.id
    if user_id not in user_histories:
        user_histories[user_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
    user_histories[user_id].append({"role": "user", "content": message.text})
    if len(user_histories[user_id]) > 20:
        user_histories[user_id] = [user_histories[user_id][0]] + user_histories[user_id][-19:]
    try:
        reply = ask_openrouter(user_histories[user_id])
        user_histories[user_id].append({"role": "assistant", "content": reply})
        bot.reply_to(message, reply)
    except Exception as e:
        bot.reply_to(message, "Прости, милый, я зависла... 🥺")

if __name__ == '__main__':
    print("💕 Аля запущена!")
    bot.infinity_polling()
