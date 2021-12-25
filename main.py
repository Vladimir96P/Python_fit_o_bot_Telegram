import telebot
from telebot import types
import statistics
import sqlite3
import os
import time
import datetime as dt
import psycopg2
bot = telebot.TeleBot("5058162485:AAHGx9-XieFGAaHLb3cVumTcokI1RkwGJbg")
DB_URI = "postgres://qmvydayqnuuxxz:40dc9792c9d15977ed989756198fbbba01983157173a98d5840e92c8c71928a8@ec2-54-74-102-48.eu-west-1.compute.amazonaws.com:5432/dcanatqglrancq"
db_con = psycopg2.connect(DB_URI, sslmode = "require")
db_obj = db_con.cursor()

@bot.message_handler(commands=['start'])

def send_welcome(message):
    msg = bot.reply_to(message, "Хэй! Меня зовут Фитобот😊 А тебя как? Напиши, пожалуйста, свое имя, возраст, рост в метрах и пол (русскоязычной раскладкой) на моем примере: Фитобот 25 1.75 М")
    bot.register_next_step_handler(msg, user_name)

def send_keyboard(message, text = "Выбери интересующий раздел 😉"):
    keyboard = types.ReplyKeyboardMarkup(row_width=2)
    itembtn0 = types.KeyboardButton('Хочу сообщить свой текущий вес 😱')
    itembtn1 = types.KeyboardButton('Хочу посмотреть статистику своего веса 😈')
    itembtn2 = types.KeyboardButton('Хочу согнать жирок 🥦')
    itembtn3 = types.KeyboardButton('Хочу поднабрать массы 💪')
    itembtn4 = types.KeyboardButton('Удалить последнюю запись веса')
    itembtn5 = types.KeyboardButton("Удалить все записи веса")
    itembtn6 = types.KeyboardButton("Очистить данные из базы (имя, возраст, пол, рост)")
    keyboard.add(itembtn0, itembtn1, itembtn2, itembtn3, itembtn4, itembtn5, itembtn6)
    msg = bot.send_message(message.from_user.id,text=text, reply_markup=keyboard)
    # bot.register_next_step_handler(msg, callback_worker)

def user_name(msg):
    print(msg)
    try:
        name = msg.text.split()[0].title()
        age = msg.text.split()[1]
        age = int(age)
        height = msg.text.split()[2]
        height = float(height)
        sex = msg.text.split()[3].title()
        if sex == 'М' or sex == 'Ж':
            # with sqlite3.connect('fit_o_bot.db') as con:
            #     cursor = con.cursor()
            #     cursor.execute('''
            #            INSERT INTO bot_users_list (user_id, name, age, height, sex)
            #            VALUES (?, ?, ?, ?, ?);''', (msg.from_user.id, name, age, height, sex))
            #     con.commit()
            #     cursor.close()
            db_obj.execute("INSERT INTO bot_users_list (user_id, name, age, height, sex) VALUES (%s, %s, %s, %s, %s);", (msg.from_user.id, name, age, height, sex))
            print('OK')
            db_con.commit()
            message = bot.send_message(msg.from_user.id, f'''Привет! Приятно познакомиться, {name} 😜. Выбирай интересующую тебя тему:) И при первом использовании не забудь ввести свой текущий вес!)''')
            send_keyboard(msg)

@bot.message_handler(content_types=['text'])

def sorry(message):
    send_keyboard(message, text="Я не понимаю 🌚 Выбери один из пунктов меню:")

bot.infinity_polling()