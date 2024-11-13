from config import BOT_TOKEN
import telebot
from telebot import types
import time
import threading

bot = telebot.TeleBot(BOT_TOKEN)

# Хранение последних координат пользователя
user_locations = {}


# Функция для преобразования координат в формат DMS
def convert_to_dms(degrees, is_latitude=True):
    direction = "N" if is_latitude and degrees >= 0 else "S" if is_latitude else "E" if degrees >= 0 else "W"
    degrees = abs(degrees)
    d = int(degrees)
    m = int((degrees - d) * 60)
    s = round((degrees - d - m / 60) * 3600, 1)
    return f"{d}°{m}'{s}\"{direction}"


# Функция для отправки обновленной локации каждые 5 секунд
def send_location_updates(chat_id):
    while chat_id in user_locations:
        location = user_locations[chat_id]
        lat_dms = convert_to_dms(location['latitude'], is_latitude=True)
        lon_dms = convert_to_dms(location['longitude'], is_latitude=False)
        bot.send_message(chat_id, f"Текущие координаты:\n{lat_dms} {lon_dms}")
        time.sleep(5)


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start_message(message):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    location_button = types.KeyboardButton("📍 Поделиться живой локацией", request_location=True)
    markup.add(location_button)

    bot.send_message(message.chat.id, "Привет! Нажмите кнопку ниже, чтобы начать трансляцию своей локации.",
                     reply_markup=markup)


# Обработчик для получения локации
@bot.message_handler(content_types=['location'])
def handle_location(message):
    if message.location is not None:
        # Сохраняем локацию пользователя
        user_locations[message.chat.id] = {
            'latitude': message.location.latitude,
            'longitude': message.location.longitude
        }
        bot.send_message(message.chat.id,
                         "Я начал отслеживать вашу локацию и буду отправлять обновления каждые 5 секунд.")

        # Запускаем поток для регулярной отправки локации
        threading.Thread(target=send_location_updates, args=(message.chat.id,), daemon=True).start()
    else:
        bot.send_message(message.chat.id, "Не удалось получить координаты.")


bot.polling()
