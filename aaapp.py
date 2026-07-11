import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from groq import AsyncGroq
from aiohttp import web
from dotenv import load_dotenv

# .env fayldan kalitlarni yuklash
load_dotenv()

# TOKENLARNI .env fayldan o'qiydi
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
AI_MODEL = "llama-3.3-70b-versatile"

# Bot va Groq sozlamalari
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
client = AsyncGroq(api_key=GROQ_API_KEY)

# Suhbat tarixi
user_histories = {}
MAX_HISTORY_LEN = 10

logging.basicConfig(level=logging.INFO)

# Buyruqlar
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    user_histories[message.from_user.id] = [
        {"role": "system", "content": "Sen yordamchisan. O'zbek tilida muloqot qil."}
    ]
    await message.answer("Salom! Men tayyorman. Savolingizni bering.")

@dp.message(Command("clear"))
async def clear_history(message: types.Message):
    user_histories[message.from_user.id] = [{"role": "system", "content": "Sen yordamchisan."}]
    await message.answer("Suhbat tarixi tozalandi.")

# Xabarlarni qayta ishlash
@dp.message()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_histories:
        user_histories[user_id] = [{"role": "system", "content": "Sen yordamchisan."}]
    
    user_histories[user_id].append({"role": "user", "content": message.text})
    
    if len(user_histories[user_id]) > MAX_HISTORY_LEN:
        user_histories[user_id] = [user_histories[user_id][0]] + user_histories[user_id][-MAX_HISTORY_LEN:]

    try:
        chat_completion = await client.chat.completions.create(
            messages=user_histories[user_id],
            model=AI_MODEL,
            temperature=0.7
        )
        response_text = chat_completion.choices[0].message.content
        user_histories[user_id].append({"role": "assistant", "content": response_text})
        await message.answer(response_text)
    except Exception as e:
        await message.answer("Kechirasiz, AI bilan bog'lanishda xatolik yuz berdi.")
        logging.error(f"Groq xatosi: {e}")

# UptimeRobot uchun HTTP server
async def handle_ping(request):
    return web.Response(text="Bot is running!")

async def main():
    # Render yoki boshqa platformalar uchun port
    port = int(os.environ.get("PORT", 8080))
    app = web.Application()
    app.router.add_get("/", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    # Botni ishga tushirish
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())