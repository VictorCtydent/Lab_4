from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import Message
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor
import logging
import os

bot_token = os.getenv('TELEGRAM_BOT_TOKEN')

# Объект бота
bot = Bot(token=bot_token)
# Диспетчер для бота
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

saved_data = {}

# Форма, которая хранит информацию о пользователе
class Form(StatesGroup):
    currency = State()
    number = State()
    other_currency = State()
    sum = State()


#Обработчик команды старт
@dp.message_handler(commands=['start'])
async def process_command1(message: Message):
    await message.reply("Привет! Я бот для подсчёта валюты. Введи /save_currency, чтобы сохранить валюту")

#Сохрание данных значения
@dp.message_handler(commands=['save_currency'])
async def process_command1(message: Message):
    await Form.currency.set()
    await message.reply("Введите название валюты")

@dp.message_handler(state=Form.currency)
async def process_currency1(message: types.Message, state: FSMContext):
    print(message.text)
    await state.update_data(currency=message.text)
    await Form.number.set()
    await message.reply("Введите курс валюты к рублю")

@dp.message_handler(state=Form.number)
async def process_currency2(message: types.Message, state: FSMContext):
    rate = message.text
    print(rate)
    data = await state.get_data()
    currency = data['currency']
    saved_data[currency] = rate
    await state.finish()
    await message.reply("Курс валюты сохранен")

@dp.message_handler(commands=['convert'])
async def procces_command2(message: types.Message):
    await Form.other_currency.set()
    await message.reply("Введите название валюты")

@dp.message_handler(state=Form.other_currency)
async def process_other_currency(message: types.Message, state: FSMContext):
    await state.update_data(other_currency=message.text)
    await Form.sum.set()
    await message.reply("Сумма")

@dp.message_handler(state=Form.sum)
async def process_sum(message: types.Message, state: FSMContext):
    data = await state.get_data()
    currency = data['other_currency']
    saved_rate = saved_data[currency]
    sum = message.text
    rate1 = int(sum) * int(saved_rate)
    print(data)
    print(saved_data)
    await message.reply(f"Сконвертированная по курсу сумма = {rate1}")
    await state.finish()

#Точка входа в приложение
if __name__ == "__main__":
    #Инициализация системы логирования
    logging.basicConfig(level=logging.INFO)
    #Подключение системы логирования к боту
    dp.middleware.setup(LoggingMiddleware())
    #Запуск бота
    executor.start_polling(dp, skip_updates= True)
