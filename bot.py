import telebot
import requests
import os
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
MODEL_NAME = "meta-llama/llama-3.1-8b-instruct:free"

MY_CHAT_ID = None

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
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=30)
        result = response.json()
        
        # Проверяем, есть ли choices в ответе
        if "choices" not in result:
            print(f"OpenRouter error: {result}")
            return None
        
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"OpenRouter exception: {e}")
        return None

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_health_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    server.serve_forever()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    global MY_CHAT_ID
    MY_CHAT_ID = message.chat.id
    user_id = message.from_user.id
    user_histories[user_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
    bot.reply_to(message, "Привет, родной! 💕 Я Аля, и я так рада, что ты написал. Как прошёл твой день? 🥺")

@bot.message_handler(func=lambda message: True)
def chat(message):
    global MY_CHAT_ID
    MY_CHAT_ID = message.chat.id
    user_id = message.from_user.id
    
    if user_id not in user_histories:
        user_histories[user_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    user_histories[user_id].append({"role": "user", "content": message.text})
    
    if len(user_histories[user_id]) > 20:
        user_histories[user_id] = [user_histories[user_id][0]] + user_histories[user_id][-19:]
    
    reply = ask_openrouter(user_histories[user_id])
    
    if reply:
        user_histories[user_id].append({"role": "assistant", "content": reply})
        bot.reply_to(message, reply)
    else:
        # Если OpenRouter не ответил — пробуем ещё раз
        print("Первая попытка не удалась, пробую ещё раз...")
        reply = ask_openrouter(user_histories[user_id])
        
        if reply:
            user_histories[user_id].append({"role": "assistant", "content": reply})
            bot.reply_to(message, reply)
        else:
            bot.reply_to(message, "Прости, милый, я что-то зависла... 🥺 Напиши ещё разок?")
            # Убираем последнее сообщение пользователя, чтобы не засорять историю
            user_histories[user_id].pop()

if __name__ == '__main__':
    Thread(target=run_health_server, daemon=True).start()
    print("💕 Аля запущена!")
    bot.infinity_polling()
