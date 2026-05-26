import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiohttp import web

async def handle(request):
    return web.Response(text="Bot is running!")

app = web.Application()
app.router.add_get('/', handle)

# Замініть ваш рядок запуску (dp.start_polling) на цей блок:
if __name__ == "__main__":
    import asyncio
    runner = web.AppRunner(app)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(runner.setup())
    site = web.TCPSite(runner, '0.0.0.0', 10000)
    loop.run_until_complete(site.start())
    loop.run_until_complete(dp.start_polling(bot))
# --- НАЛАШТУВАННЯ ТОКЕНА ---
API_TOKEN = "8849714599:AAE2rn3RM5HLof9LAoSsimwosoifW7NbXx4"
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- БАЗА ДАНИХ ---
conn = sqlite3.connect("dating_bot.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    tg_id INTEGER PRIMARY KEY,
    name TEXT,
    age INTEGER,
    gender TEXT,
    photo_id TEXT
)
""")
conn.commit()

class Registration(StatesGroup):
    name = State()
    age = State()
    gender = State()
    photo = State()

main_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="🔍 Дивитися анкети")]
], resize_keyboard=True)
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🔎 Дивитися анкети"),
            KeyboardButton(text="🚗 Шукаю поїздку")
        ],
        [
            KeyboardButton(text="🎮 Пошук напарників"),
            KeyboardButton(text="🥂 Компанія для туси")
        ],
        [
            KeyboardButton(text="🚶 Прогулянки"),
            KeyboardButton(text="❤️ Шукаю пару")
        ]
    ],
    resize_keyboard=True
)
def get_gender_kb():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Хлопець")],
        [KeyboardButton(text="Дівчина")]
    ], resize_keyboard=True)

def get_like_dislike_kb(current_profile_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👎 Дизлайк", callback_data=f"dislike_{current_profile_id}"),
            InlineKeyboardButton(text="👍 Лайк", callback_data=f"like_{current_profile_id}")
        ]
    ])
@dp.message(lambda message: message.text == "Компанія для туси")
async def find_party(message: types.Message):
    await message.answer("Ви обрали: Компанія для туси. Розкажіть, який формат зустрічі ви шукаєте?")
@dp.message(lambda message: message.text == "Компанія для туси")
async def find_party(message: types.Message):
    await message.answer("Ви обрали: Компанія для туси. Розкажіть, який формат зустрічі ви шукаєте?")
@dp.message(lambda message: message.text == "Прогулянки")
async def find_walk(message: types.Message):
    await message.answer("Ви обрали: Прогулянки. Куди плануєте йти?")

@dp.message(lambda message: message.text == "Шукаю пару")
async def find_partner(message: types.Message):
    await message.answer("Ви обрали: Шукаю пару. Напишіть коротко про себе.")
@dp.message(Command("start"))
async def start_cmd(message: types.Message, state: FSMContext):
    cursor.execute("SELECT * FROM users WHERE tg_id = ?", (message.from_user.id,))
    user = cursor.fetchone()
    if user:
        await message.answer(f"Привіт, {user[1]}! Натисни кнопку нижче, щоб шукати пару.", reply_markup=main_kb)
    else:
        await message.answer("Привіт! Давай створимо твою анкету для знайомств. Як тебе звати?")
        await state.set_state(Registration.name)

@dp.message(Registration.name)
async def reg_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Скільки тобі років?")
    await state.set_state(Registration.age)

@dp.message(Registration.age)
async def reg_age(message: types.Message, state: FSMContext):
    if not message.text.isdigit() or int(message.text) < 14:
        return await message.answer("Введи свій вік цифрами (мінімум 14 років).")
    await state.update_data(age=int(message.text))
    await message.answer("Яка твоя стать?", reply_markup=get_gender_kb())
    await state.set_state(Registration.gender)

@dp.message(Registration.gender)
async def reg_gender(message: types.Message, state: FSMContext):
    gender_text = message.text.capitalize()
    if gender_text not in ["Хлопець", "Дівчина"]:
        return await message.answer("Обери стать за допомогою кнопки.")
    await state.update_data(gender=gender_text)
    await message.answer("Надішли своє фото для анкети.", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(Registration.photo)

@dp.message(Registration.photo, F.photo)
async def reg_photo(message: types.Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    data = await state.get_data()
    cursor.execute("INSERT OR REPLACE INTO users VALUES (?, ?, ?, ?, ?)",
                   (message.from_user.id, data['name'], data['age'], data['gender'], photo_id))
    conn.commit()
    await state.clear()
    await message.answer("Чудово! Анкету створено.", reply_markup=main_kb)

@dp.message(F.text == "🔍 Дивитися анкети")
async def show_profiles(message: types.Message):
    cursor.execute("SELECT gender FROM users WHERE tg_id = ?", (message.from_user.id,))
    my_data = cursor.fetchone()
    if not my_data:
        return await message.answer("Спочатку зареєструйся! Напиши /start")
    
    my_gender = my_data[0]
    opposite_gender = "Дівчина" if my_gender == "Хлопець" else "Хлопець"
    cursor.execute("SELECT tg_id, name, age, photo_id FROM users WHERE gender = ? AND tg_id != ? ORDER BY RANDOM() LIMIT 1", 
                   (opposite_gender, message.from_user.id))
    profile = cursor.fetchone()
    if not profile:
        return await message.answer("На жаль, нові анкети закінчилися.")
    
    tg_id, name, age, photo_id = profile
    await message.answer_photo(photo=photo_id, caption=f"🔥 {name}, {age}", reply_markup=get_like_dislike_kb(tg_id))

@dp.callback_query(F.data.startswith("like_"))
async def handle_like(callback: types.CallbackQuery):
    liked_user_id = int(callback.data.split("_")[1])
    try:
        cursor.execute("SELECT name FROM users WHERE tg_id = ?", (callback.from_user.id,))
        me_data = cursor.fetchone()
        link = f"[профіль](tg://user?id={callback.from_user.id})"
        await bot.send_message(chat_id=liked_user_id, text=f"❤️ Ти сподобався користувачу {me_data[0]}! Ось посилання: {link}", parse_mode="Markdown")
    except:
        pass
    await callback.answer("Лайк надіслано! ❤️")
    await show_profiles(callback.message)

@dp.callback_query(F.data.startswith("dislike_"))
async def handle_dislike(callback: types.CallbackQuery):
    await callback.answer("Пропущено ↩️")
    await show_profiles(callback.message)

async def main():
    print("Бот успішно запустився!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
