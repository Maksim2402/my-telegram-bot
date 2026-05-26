import sqlite3
import asyncio
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiohttp import web

# --- НАЛАШТУВАННЯ ---
API_TOKEN = "8849714599:AAE2rn3RM5HLof9LAoSsimwosoifW7NbXx4"
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- БАЗА ДАНИХ ---
conn = sqlite3.connect("dating_bot.db")
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (tg_id INTEGER PRIMARY KEY, name TEXT, age INTEGER, gender TEXT, photo_id TEXT)")
conn.commit()

# --- КЛАВІАТУРА ---
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Компанія для туси"), KeyboardButton(text="Прогулянки")],
        [KeyboardButton(text="Шукаю пару")],
        [KeyboardButton(text="🚗 Шукаю поїздку"), KeyboardButton(text="🎮 Пошук напарників")],
        [KeyboardButton(text="🔍 Дивитися анкети")]
    ],
    resize_keyboard=True
)

# --- СТАН РОЗДІЛ ---
class Registration(StatesGroup):
    name = State()
    age = State()
    gender = State()
    photo = State()

# --- ОБРОБНИКИ ---
@dp.message(Command("start"))
async def start_handler(message: types.Message, state: FSMContext):
    cursor.execute("SELECT * FROM users WHERE tg_id = ?", (message.from_user.id,))
    if cursor.fetchone():
        await message.answer("Привіт! Ти вже зареєстрований. Обери дію в меню:", reply_markup=main_kb)
    else:
        await message.answer("Привіт! Давай створимо анкету. Як тебе звати?")
        await state.set_state(Registration.name)

@dp.message(F.text == "🔍 Дивитися анкети")
async def show_profiles(message: types.Message):
    cursor.execute("SELECT * FROM users WHERE tg_id != ?", (message.from_user.id,))
    profiles = cursor.fetchall()
    if not profiles:
        await message.answer("На жаль, нових анкет поки немає.")
    else:
        for p in profiles:
            await message.answer_photo(photo=p[4], caption=f"Ім'я: {p[1]}, Вік: {p[2]}, Стать: {p[3]}")

@dp.message(lambda message: message.text == "Компанія для туси")
async def find_party(message: types.Message):
    await message.answer("Ви обрали: Компанія для туси. Розкажіть, який формат зустрічі ви шукаєте?")

@dp.message(lambda message: message.text == "Прогулянки")
async def find_walk(message: types.Message):
    await message.answer("Ви обрали: Прогулянки. Куди плануєте йти?")

@dp.message(lambda message: message.text == "Шукаю пару")
async def find_partner(message: types.Message):
    await message.answer("Ви обрали: Шукаю пару. Напишіть коротко про себе.")

@dp.message(F.text == "🚗 Шукаю поїздку")
async def show_trips(message: types.Message):
    await message.answer("Розділ пошуку поїздок у розробці!")

@dp.message(F.text == "🎮 Пошук напарників")
async def show_games(message: types.Message):
    await message.answer("Розділ пошуку напарників у розробці!")

@dp.message()
async def all_other_messages(message: types.Message):
    await message.answer("Я не розумію. Обери пункт у меню:", reply_markup=main_kb)

# --- ЗАПУСК З ВЕБ-СЕРВЕРОМ ---
async def web_handler(request):
    return web.Response(text="Bot is running!")

async def start_bot():
    app = web.Application()
    app.router.add_get('/', web_handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 10000)
    await site.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(start_bot())
