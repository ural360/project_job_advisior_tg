import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from logic import CareerAdvisor
from config import BOT_TOKEN

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Инициализация помощников
career_advisor = CareerAdvisor("career_advisor.db")

# Состояния FSM
class Form(StatesGroup):
    waiting_skills = State()
    waiting_interests = State()
    waiting_experience = State()
    waiting_profession = State()

# Клавиатуры
def get_main_menu() -> ReplyKeyboardMarkup:
    """Главное меню"""
    buttons = [
        [KeyboardButton(text="🎯 Получить рекомендации")],
        [KeyboardButton(text="📊 Оценить профессию")],
        [KeyboardButton(text="📋 Список профессий")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_experience_levels() -> ReplyKeyboardMarkup:
    """Выбор уровня опыта"""
    buttons = [
        [KeyboardButton(text="🚀 Нет опыта")],
        [KeyboardButton(text="🛠 Менее 1 года")],
        [KeyboardButton(text="⚙️ 1-3 года")],
        [KeyboardButton(text="🏆 Более 3 лет")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_back_button() -> ReplyKeyboardMarkup:
    """Кнопка возврата"""
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🔙 Назад")]], resize_keyboard=True)

# Обработчики команд
@dp.message(Command("start"))
async def start_command(message: Message):
    await message.answer(
        "👋 Добро пожаловать в карьерного помощника!\n"
        "Я помогу вам найти подходящие профессии на основе ваших навыков и интересов.",
        reply_markup=get_main_menu()
    )

@dp.message(F.text == "🔙 Назад")
async def back_to_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Главное меню:", reply_markup=get_main_menu())

# Рекомендации
@dp.message(F.text == "🎯 Получить рекомендации")
async def start_recommendations(message: Message, state: FSMContext):
    await message.answer(
        "Введите ваши навыки через запятую:\n"
        "Пример: Python, работа в команде, аналитическое мышление",
        reply_markup=get_back_button()
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
        reply_markup=get_back_button()
    )
    await state.set_state(Form.waiting_interests)

@dp.message(Form.waiting_interests)
async def process_interests(message: Message, state: FSMContext):
    if message.text == "🔙 Назад":
        await message.answer("Введите навыки заново:", reply_markup=get_back_button())
        await state.set_state(Form.waiting_skills)
        return
    
    interests = [i.strip() for i in message.text.split(",") if i.strip()]
    if not interests:
        await message.answer("Пожалуйста, введите хотя бы один интерес")
        return
    
    await state.update_data(interests=interests)
    await message.answer(
        "Выберите ваш уровень опыта:",
        reply_markup=get_experience_levels()
    )
    await state.set_state(Form.waiting_experience)

@dp.message(Form.waiting_experience)
async def process_experience(message: Message, state: FSMContext):
    valid_experience = ["🚀 Нет опыта", "🛠 Менее 1 года", "⚙️ 1-3 года", "🏆 Более 3 лет"]
    
    if message.text not in valid_experience:
        await message.answer("Пожалуйста, выберите вариант из клавиатуры ниже")
        return
    
    user_data = await state.get_data()
    experience_map = {
        "🚀 Нет опыта": "Нет опыта",
        "🛠 Менее 1 года": "Менее 1 года",
        "⚙️ 1-3 года": "1-3 года",
        "🏆 Более 3 лет": "Более 3 лет"
    }
    
    try:
        response = await career_advisor.get_ai_recommendations(
            skills=user_data['skills'],
            interests=user_data['interests'],
            experience=experience_map[message.text]
        )
        await message.answer(response[:4000], reply_markup=get_main_menu())
    except Exception as e:
        logger.error(f"Ошибка получения рекомендаций: {e}")
        await message.answer("Произошла ошибка. Попробуйте позже.", reply_markup=get_main_menu())
    finally:
        await state.clear()

# Список профессий
@dp.message(F.text == "📋 Список профессий")
async def show_professions(message: Message):
    professions = career_advisor.get_all_professions()
    response = "📚 Доступные профессии:\n\n" + "\n".join(
        f"• {p['name']}: {p['description']}" for p in professions[:15]
    )
    await message.answer(response, reply_markup=get_main_menu())

# Оценка профессии
@dp.message(F.text == "📊 Оценить профессию")
async def start_evaluation(message: Message, state: FSMContext):
    await message.answer(
        "Введите название профессии для оценки:",
        reply_markup=get_back_button()
    )
    await state.set_state(Form.waiting_profession)

@dp.message(Form.waiting_profession)
async def evaluate_profession_step1(message: Message, state: FSMContext):
    if message.text == "🔙 Назад":
        await state.clear()
        await message.answer("Главное меню:", reply_markup=get_main_menu())
        return
    
    await state.update_data(profession=message.text)
    await message.answer(
        "Введите ваши навыки через запятую:",
        reply_markup=get_back_button()
    )
    await state.set_state(Form.waiting_skills)

# Запуск бота
async def main():
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.critical(f"Ошибка в основном цикле: {e}")
    finally:
        await career_advisor.close()

if __name__ == "__main__":
    asyncio.run(main())