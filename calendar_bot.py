import telebot
from telebot import types
import threading
from datetime import datetime
import pytz

bot = telebot.TeleBot('')

reminder = {}

def Send_Reminder(chat_id, message):
    bot.send_message(chat_id, f"Напоминание: {message}")

@bot.message_handler(commands=['start'])
def Start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("🗓Поставить напоминание")
    markup.add(btn1)
    bot.send_message(message.from_user.id, "👋Привет, поставь напоминание", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == '🗓Поставить напоминание')
def Get_text_message(message):
    msg = bot.send_message(message.from_user.id, 'Введите напоминание')
    bot.register_next_step_handler(msg, Process_Reminder)

def Process_Reminder(message):
    text_reminder = message.text
    msg = bot.send_message(message.from_user.id, 'Введите дату напоминания в формате "ДД.ММ.ГГГГ":')
    bot.register_next_step_handler(msg, lambda msg: Set_Reminder_Date(msg, text_reminder))

def Set_Reminder_Date(message, reminder_text):
    date_str = message.text
    chat_id = message.from_user.id

    try:
        date_reminder = datetime.strptime(date_str, "%d.%m.%Y")
        msg = bot.send_message(chat_id, 'Введите время напоминания в формате "ЧЧ:ММ":')
        bot.register_next_step_handler(msg, lambda msg: Set_Reminder_Time(msg, reminder_text, date_reminder))

    except ValueError:
        bot.send_message(chat_id, "Неверный формат даты. Используйте формат ДД.ММ.ГГГГ.")
        return

def Set_Reminder_Time(message, reminder_text, reminder_date):
    time_str = message.text
    chat_id = message.from_user.id

    try:
        hour, minute = map(int, time_str.split(':'))
        time_reminder = reminder_date.replace(hour=hour, minute=minute)
        msg = bot.send_message(chat_id, 'Введите часовой пояс в формате: Europe/Moscow')
        bot.register_next_step_handler(msg, lambda msg: schedule_reminder(msg, chat_id, time_reminder, reminder_text))

    except ValueError:
        bot.send_message(chat_id, "Неверный формат времени. Используйте формат ЧЧ:ММ.")
        return 

def schedule_reminder(message, chat_id, reminder_datetime, reminder_text):
    timezone_str = message.text.strip()
    
    try:
        tz = pytz.timezone(timezone_str)
        localized_reminder_datetime = tz.localize(reminder_datetime)
        now = datetime.now(tz)

        if localized_reminder_datetime < now:
            bot.send_message(chat_id, "Нельзя установить напоминание на прошлое время.")
            return
        delay_seconds = (localized_reminder_datetime - now).total_seconds()
        threading.Timer(delay_seconds, Send_Reminder, args=(chat_id, reminder_text)).start()
        
        bot.send_message(chat_id, f"Напоминание установлено на {localized_reminder_datetime.strftime('%d.%m.%Y %H:%M')} в часовом поясе {timezone_str}.")

    except pytz.UnknownTimeZoneError:
        bot.send_message(chat_id, "Неверный часовой пояс. Используйте правильный формат.")

bot.polling(none_stop=True)
