import asyncio
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from groq import AsyncGroq

# ==========================================
# 1. SOZLAMALAR
# ==========================================
# TOKEN va KEY ni o'zingizniki bilan almashtiring
BOT_TOKEN = " "
GROQ_API_KEY = ""

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
client = AsyncGroq(api_key=GROQ_API_KEY) 

class BotStates(StatesGroup):
    rus_tarjima = State()
    uzb_tarjima = State()
    kril_lotin = State()

asosiy_menyu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🇷🇺 Ruscha tarjima"), KeyboardButton(text="🇺🇿 O'zbekcha tarjima")],
        [KeyboardButton(text="🔄 Kril - Lotin")]
    ],
    resize_keyboard=True
)

orqaga_menyu = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🔙 Asosiy menyu")]],
    resize_keyboard=True
)

# ==========================================
# 2. AI FUNKSIYASI (SYSTEM PROMPT BILAN)
# ==========================================
async def get_ai_response(text: str, instruction: str) -> str:
    try:
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": instruction},
                {"role": "user", "content": text}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Xatolik yuz berdi: {e}"

# ==========================================
# 3. BOT MANTIG'I
# ==========================================
@dp.message(CommandStart())
async def start_cmd(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Assalomu alaykum! Kerakli bo'limni tanlang:", reply_markup=asosiy_menyu)

@dp.message(F.text == "🔙 Asosiy menyu")
async def back_to_main(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Asosiy menyuga qaytdingiz.", reply_markup=asosiy_menyu)

@dp.message(F.text.in_({"🇷🇺 Ruscha tarjima", "🇺🇿 O'zbekcha tarjima", "🔄 Kril - Lotin"}))
async def set_mode(message: types.Message, state: FSMContext):
    if message.text == "🇷🇺 Ruscha tarjima":
        await state.set_state(BotStates.rus_tarjima)
        await message.answer("Ruscha tarjima rejimidasiz. Matnni yuboring:", reply_markup=orqaga_menyu)
    elif message.text == "🇺🇿 O'zbekcha tarjima":
        await state.set_state(BotStates.uzb_tarjima)
        await message.answer("O'zbekcha tarjima rejimidasiz. Matnni yuboring:", reply_markup=orqaga_menyu)
    elif message.text == "🔄 Kril - Lotin":
        await state.set_state(BotStates.kril_lotin)
        await message.answer("Kril-Lotin rejimidasiz. Matnni yuboring:", reply_markup=orqaga_menyu)

# ==========================================
# 4. TARJIMA VA O'GIRISH JARAYONLARI
# ==========================================
@dp.message(BotStates.rus_tarjima)
async def process_rus(message: types.Message):
    ins = "Sen professional tarjimonsan. Matnni faqat rus tiliga tarjima qil. Hech qanday izoh yoki savol qo'shma."
    msg = await message.answer("⏳...")
    res = await get_ai_response(message.text, ins)
    await msg.edit_text(res)

@dp.message(BotStates.uzb_tarjima)
async def process_uzb(message: types.Message):
    ins = "Sen professional tarjimonsan. Matnni faqat o'zbek tiliga tarjima qil. Hech qanday izoh yoki savol qo'shma. 'Ipak Yo'li' nomini o'zgartirmasdan saqlab qol."
    msg = await message.answer("⏳...")
    res = await get_ai_response(message.text, ins)
    await msg.edit_text(res)

@dp.message(BotStates.kril_lotin)
async def process_kril(message: types.Message):
    ins = "Sen faqat matn o'giruvchi botsan. Matnni lotin yozuviga o'gir. Izoh yozma, savol berma, matndan tashqari hech narsa yozma."
    msg = await message.answer("⏳...")
    res = await get_ai_response(message.text, ins)
    await msg.edit_text(res)

async def main():
    print("Bot muvaffaqiyatli ishga tushdi!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())