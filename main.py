import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.client.default import DefaultBotProperties
from database import Database
from ai_helper import AIHelper
from config import BOT_TOKEN

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
dp = Dispatcher()
db = Database()
ai_helper = AIHelper()

class Form(StatesGroup):
    waiting_skills = State()
    waiting_interests = State()
    waiting_experience = State()

def get_main_menu() -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text="🎯 Рекомендации по профессиям")],
        [KeyboardButton(text="📋 Список категорий")],
        
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_experience_keyboard() -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text="🚀 Нет опыта")],
        [KeyboardButton(text="🛠 1-3 года опыта")],
        [KeyboardButton(text="⚡ 3+ года опыта")],
        [KeyboardButton(text="🔙 Назад")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_back_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🔙 Назад")]], resize_keyboard=True)

@dp.message(Command("start"))
async def start_command(message: Message):
    db.add_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )
    await message.answer(
        "👋 Добро пожаловать в карьерного помощника!\n"
        "Я помогу вам найти подходящие профессии на основе ваших навыков и интересов.",
        reply_markup=get_main_menu()
    )

@dp.message(F.text == "🔙 Назад")
async def back_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Главное меню:", reply_markup=get_main_menu())

@dp.message(F.text == "🎯 Рекомендации по профессиям")
async def start_recommendations(message: Message, state: FSMContext):
    await message.answer(
        "Введите ваши ключевые навыки через запятую:\n"
        "Пример: Python, работа в команде, аналитическое мышление",
        reply_markup=get_back_keyboard()
    )
    await state.set_state(Form.waiting_skills)

@dp.message(Form.waiting_skills)
async def process_skills(message: Message, state: FSMContext):
    if message.text == "🔙 Назад":
        await state.clear()
        await message.answer("Главное меню:", reply_markup=get_main_menu())
        return
    
    skills = [s.strip() for s in message.text.split(",") if s.strip()]
    if not skills:
        await message.answer("Пожалуйста, введите хотя бы один навык")
        return
    
    await state.update_data(skills=skills)
    await message.answer(
        "Теперь введите ваши интересы через запятую:\n"
        "Пример: программирование, дизайн, маркетинг",
        reply_markup=get_back_keyboard()
    )
    await state.set_state(Form.waiting_interests)

@dp.message(Form.waiting_interests)
async def process_interests(message: Message, state: FSMContext):
    if message.text == "🔙 Назад":
        await state.set_state(Form.waiting_skills)
        await message.answer("Введите навыки заново:", reply_markup=get_back_keyboard())
        return
    
    interests = [i.strip() for i in message.text.split(",") if i.strip()]
    if not interests:
        await message.answer("Пожалуйста, введите хотя бы один интерес")
        return
    
    await state.update_data(interests=interests)
    await message.answer(
        "Выберите ваш уровень опыта:",
        reply_markup=get_experience_keyboard()
    )
    await state.set_state(Form.waiting_experience)

@dp.message(Form.waiting_experience)
async def process_experience(message: Message, state: FSMContext):
    if message.text == "🔙 Назад":
        await state.set_state(Form.waiting_interests)
        await message.answer("Введите интересы заново:", reply_markup=get_back_keyboard())
        return
    
    experience_map = {
        "🚀 Нет опыта": "Нет опыта",
        "🛠 1-3 года опыта": "1-3 года",
        "⚡ 3+ года опыта": "3+ года"
    }
    experience = experience_map.get(message.text, message.text)
    
    user_data = await state.get_data()
    try:
        response = await ai_helper.get_recommendations(
            skills=user_data['skills'],
            interests=user_data['interests'],
            experience=experience
        )
        await message.answer(response, reply_markup=get_main_menu())
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        await message.answer(
            "⚠ Произошла ошибка. Попробуйте другие навыки/интересы.",
            reply_markup=get_main_menu()
        )
    finally:
        await state.clear()

@dp.message(F.text == "📋 Список категорий")
async def show_categories(message: Message):
    categories = await ai_helper.get_categories()
    response = "📚 Категории профессий:\n\n" + "\n".join(f"• {cat}" for cat in categories)
    await message.answer(response)

async def main():
    try:
        await dp.start_polling(bot)
    finally:
        db.close()
        await ai_helper.close()

if __name__ == "__main__":
    asyncio.run(main())