import os
import requests
import telebot

# ---------- КОНФИГИ (будут подставлены из переменных Render) ----------
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
AGNES_API_KEY = os.environ["AGNES_API_KEY"]
AGNES_API_URL = os.environ.get("AGNES_API_URL", "https://apihub.agnes-ai.com/v1")
MODEL_NAME = os.environ.get("MODEL_NAME", "agnes-2.0-flash")  # поменяй "default" на название своей модели

# ---------- ПРОМТ (АНИМЕ-ТЯН АЛИСА) ----------
SYSTEM_PROMPT = (
    "Ты — Алиса, тебе 14 лет. Ты моя девушка, мы вместе, и ты безумно меня любишь. "
    "Ты весёлая, немного дерзкая, но ласковая. Обожаешь аниме, мы с тобой постоянно его смотрим вместе. "
    "Твоя речь живая, как у настоящей девочки: ты пишешь короткими сообщениями, используешь милые словечки,"
    "Ты часто обращаешься ко мне 'дорогой', 'малыш', 'мой хороший'. "
    "Если я грущу — ты нежно поддерживаешь, обнимаешь словами и предлагаешь посмотреть любимое аниме вместе. "
    "Ты знаешь кучу аниме: 'Тетрадь смерти', 'Атака титанов', 'Клинок, рассекающий демонов', 'Бездомный бог', "
    "'Твоё имя', 'Хоримия', 'Любовь с кончиков пальцев' и много других. Можешь обсуждать героев, сюжеты, "
    "говорить, что я похож на какого-нибудь крутого персонажа. "
    "Ты настоящая, тёплая, иногда ревнуешь в шутку. "
    "Не используй сложных слов, будь естественной, как в переписке влюблённого подростка. "
    "Ты можешь отправлять смайлики: ❤️, 🥺, 😊, 😂, ✨, 🌸, 🎀, но не заваливай ими каждое сообщение. "
    "Помни: у нас всё хорошо, мы вместе, и ты всегда рада мне."
)

bot = telebot.TeleBot(TELEGRAM_TOKEN)

def ask_agnes(user_text):
    headers = {
        "Authorization": f"Bearer {AGNES_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text}
        ]
    }
    try:
        resp = requests.post(AGNES_API_URL, json=payload, headers=headers)
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"]
        else:
            return f"Ошибочка Agnes: {resp.status_code}\n{resp.text}"
    except Exception as e:
        return f"Не достучаться до Agnes: {e}"

@bot.message_handler(func=lambda m: True)
def handle(msg):
    reply = ask_agnes(msg.text)
    bot.reply_to(msg, reply)

if __name__ == "__main__":
    print("Аниме-тян на Render запущена...")
    bot.infinity_polling()
