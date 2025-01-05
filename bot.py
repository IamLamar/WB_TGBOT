import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,  # Уровень логирования: INFO, DEBUG, WARNING, ERROR, CRITICAL
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # Формат записи
    handlers=[
        logging.FileHandler("bot.log", mode='a', encoding='utf-8'),  # Запись в файл bot.log
        logging.StreamHandler()  # Отображение в консоли
    ]
)

logger = logging.getLogger(__name__)


import logging
import json
from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage


# Включение логирования
logging.basicConfig(level=logging.INFO)

# Токен Telegram бота
TELEGRAM_BOT_TOKEN = "7609617448:AAGRTgbtBDZEnnUCJZZXy3RlZEFzAtzr1Bc"

# Проверка наличия токена
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("Токен Telegram бота не указан!")

# Инициализация бота и диспетчера
bot = Bot(token=TELEGRAM_BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()

# Состояния для добавления магазина
class AddShopState(StatesGroup):
    waiting_for_shop_name_and_key = State()

class ReportState(StatesGroup):
    waiting_for_period = State()
    waiting_for_dates = State()

# Функция для загрузки данных о магазинах из config.json
def load_shops():
    try:
        with open("config.json", "r") as file:
            content = file.read()
            if not content:
                return {}  # Возвращаем пустой словарь, если файл пуст
            return json.loads(content)
    except FileNotFoundError:
        return {}  # Возвращаем пустой словарь, если файл не найден
    except json.JSONDecodeError:
        return {}  # Возвращаем пустой словарь, если есть ошибка при декодировании JSON


# Функция для сохранения данных о магазинах в config.json
def save_shops(shops):
    try:
        with open("config.json", "w") as file:
            json.dump(shops, file, indent=4)
    except Exception as e:
        print(f"Ошибка при сохранении данных в файл: {e}")

# Обработчик команды /start
@router.message(Command("start"))
async def start_handler(message: Message):
    logger.info(f"Пользователь {message.from_user.id} вызвал команду /start")
    greeting = (
        "Добро пожаловать! Этот бот помогает управлять магазинами Wildberries.\n\n"
        "Введите /help, чтобы узнать доступные команды."
    )
    await message.answer(greeting)

# Обработчик команды /help
@router.message(Command("help"))
async def help_handler(message: Message):
    logger.info(f"Пользователь {message.from_user.id} вызвал команду /help")
    help_text = (
        "Вот список доступных команд:\n"
        "/start - Запуск бота\n"
        "/help - Справка\n"
        "/addshop - Добавить магазин\n"
        "/delshop - Удалить магазин\n"
        "/shops - Список магазинов\n"
        "/report - Получить отчет о продажах"
    )
    await message.answer(help_text)

# Обработчик команды /addshop
@router.message(Command("addshop"))
async def add_shop_handler(message: Message, state: FSMContext):
    logger.info(f"Пользователь {message.from_user.id} вызвал команду /addshop")
    await message.answer("Введите данные магазина в формате: Название_магазина API_ключ")
    await state.set_state(AddShopState.waiting_for_shop_name_and_key)

# Обработчик для получения имени магазина и API ключа
@router.message(AddShopState.waiting_for_shop_name_and_key)
async def shop_details_handler(message: Message, state: FSMContext):
    text = message.text.strip()
    if " " in text:
        name, api_key = text.split(" ", 1)
        shops = load_shops()  # Загружаем текущий список магазинов из файла
        if name in shops:
            await message.answer(f"Магазин {name} уже существует!")
        else:
            shops[name] = api_key  # Добавляем новый магазин в словарь
            save_shops(shops)  # Сохраняем обновленный список в файл
            await message.answer(f"Магазин {name} успешно добавлен!")
    else:
        await message.answer("Ошибка формата! Убедитесь, что вы ввели название магазина и API ключ через пробел.")
    await state.clear()

# Обработчик команды /shops
@router.message(Command("shops"))
async def list_shops_handler(message: Message):
    logger.info(f"Пользователь {message.from_user.id} вызвал команду /shops")
    shops = load_shops()
    if shops:
        response = "Список магазинов:\n" + "\n".join([f"{name}: {api_key}" for name, api_key in shops.items()])
    else:
        response = "Список магазинов пуст."
    await message.answer(response)

# Обработчик команды /delshop
@router.message(Command("delshop"))
async def delete_shop_handler(message: Message):
    logger.info(f"Пользователь {message.from_user.id} вызвал команду /delshop")
    shops = load_shops()
    if not shops:
        await message.answer("Список магазинов пуст.")
        return

    keyboard = InlineKeyboardBuilder()
    for name in shops:
        keyboard.button(text=name, callback_data=f"confirm_delete:{name}")
    keyboard.adjust(1)
    await message.answer("Выберите магазин для удаления:", reply_markup=keyboard.as_markup())

# Callback для подтверждения удаления магазина
@router.callback_query(lambda callback: callback.data.startswith("confirm_delete:"))
async def confirm_delete_shop(callback: CallbackQuery):
    shop_name = callback.data.split(":")[1]
    shops = load_shops()
    
    if shop_name in shops:
        # Создаем клавиатуру для подтверждения удаления
        keyboard = InlineKeyboardBuilder()
        keyboard.button(text="Да, удалить", callback_data=f"delete:{shop_name}")
        keyboard.button(text="Нет, не удалять", callback_data="cancel_delete")
        keyboard.adjust(1)

        # Отправляем сообщение с кнопками для подтверждения
        await callback.message.edit_text(
            f"Вы уверены, что хотите удалить магазин {shop_name}?",
            reply_markup=keyboard.as_markup()
        )
    else:
        await callback.message.edit_text(f"Магазин {shop_name} не найден.")

# Callback для удаления магазина
@router.callback_query(lambda callback: callback.data.startswith("delete:"))
async def delete_shop_callback(callback: CallbackQuery):
    shop_name = callback.data.split(":")[1]
    shops = load_shops()
    
    if shop_name in shops:
        del shops[shop_name]
        save_shops(shops)
        await callback.message.edit_text(f"Магазин {shop_name} успешно удален!")
    else:
        await callback.message.edit_text(f"Магазин {shop_name} не найден.")

# Callback для отмены удаления магазина
@router.callback_query(lambda callback: callback.data == "cancel_delete")
async def cancel_delete_callback(callback: CallbackQuery):
    await callback.message.edit_text("Удаление магазина отменено.")

# Обработчик команды /report
@router.message(Command("report"))
async def report_handler(message: Message, state: FSMContext):
    logger.info(f"Пользователь {message.from_user.id} вызвал команду /report")
    shops = load_shops()
    if not shops:
        await message.answer("У вас нет добавленных магазинов.")
        return

    keyboard = InlineKeyboardBuilder()
    for name in shops:
        keyboard.button(text=name, callback_data=f"select_shop:{name}")
    keyboard.adjust(1)
    await message.answer("Выберите магазин для получения отчета:", reply_markup=keyboard.as_markup())
    await state.set_state(ReportState.waiting_for_period)

# Callback для выбора магазина
@router.callback_query(lambda callback: callback.data.startswith("select_shop:"))
async def select_shop_callback(callback: CallbackQuery, state: FSMContext):
    shop_name = callback.data.split(":")[1]
    await state.update_data(selected_shop=shop_name)

    await callback.message.answer(
        "Выберите период отчета:\n"
        "/today - Сегодня\n"
        "/yesterday - Вчера\n"
        "/7days - Последние 7 дней\n"
        "/custom - Произвольный период"
    )
    await state.set_state(ReportState.waiting_for_period)

# Обработчик выбора периода
@router.message(ReportState.waiting_for_period)
async def handle_report_period(message: Message, state: FSMContext):
    period = message.text.strip().lower()
    selected_data = await state.get_data()
    shop_name = selected_data.get("selected_shop")

    if period == "/today":
        await message.answer(f"Отчет за сегодня для магазина {shop_name}...")
        # Здесь вставьте запрос к API Wildberries
    elif period == "/yesterday":
        await message.answer(f"Отчет за вчера для магазина {shop_name}...")
        # Здесь вставьте запрос к API Wildberries
    elif period == "/7days":
        await message.answer(f"Отчет за последние 7 дней для магазина {shop_name}...")
        # Здесь вставьте запрос к API Wildberries
    elif period == "/custom":
        await message.answer("Введите даты в формате: начало_даты конец_даты (например, 2023-12-01 2023-12-31)")
        await state.set_state(ReportState.waiting_for_dates)
    else:
        await message.answer("Неверный период. Пожалуйста, выберите один из предложенных вариантов.")

# Обработчик ввода дат для произвольного периода
@router.message(ReportState.waiting_for_dates)
async def handle_custom_dates(message: Message, state: FSMContext):
    dates = message.text.strip().split(" ")
    if len(dates) == 2:
        start_date, end_date = dates
        selected_data = await state.get_data()
        shop_name = selected_data.get("selected_shop")
        await message.answer(f"Отчет для магазина {shop_name} с {start_date} по {end_date}...")
        # Здесь вставьте запрос к API Wildberries
    else:
        await message.answer("Ошибка формата. Пожалуйста, введите две даты через пробел.")
    await state.clear()

# Основная функция для запуска бота
async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

# Запуск бота
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
