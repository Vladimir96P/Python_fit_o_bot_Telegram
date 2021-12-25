import telebot
from telebot import types
import sqlite3
import datetime as dt
import os
import psycopg2
bot = telebot.TeleBot("5058162485:AAGSB2FehnhupFU5ViiEwRgypDMJmddcpmg")
bot.delete_webhook()
conn = sqlite3.connect('fit_o_bot.db')
cursor = conn.cursor()
try:
    query0 = '''CREATE TABLE \"bot_users_list\" (
    \"ID\" INTEGER UNIQUE,
    \"user_id\" INTEGER,
    \"name\" TEXT,
    \"age\" INTEGER,
    \"height\" REAL,
    \"sex\" TEXT,
    PRIMARY KEY (\"ID\")
    )'''
    cursor.execute(query0)
    conn.close()
except:
    pass
try:
    query = '''CREATE TABLE \"bot_users_weights_table\" (
    \"ID\" INTEGER UNIQUE,
    \"user_id\" INTEGER,
    \"date\" TEXT,
    \"weight\" REAL,
    PRIMARY KEY (\"ID\")
    )'''
    cursor.execute(query)
    conn.close()
except:
    pass
db_URL = "postgres://qmvydayqnuuxxz:40dc9792c9d15977ed989756198fbbba01983157173a98d5840e92c8c71928a8@ec2-54-74-102-48.eu-west-1.compute.amazonaws.com:5432/dcanatqglrancq"
db_con = psycopg2.connect(db_URL, sslmode = "require")
# db_obj = db_con.cursor()
# db_obj.execute('''INSERT INTO bot_users_list (user_id, name, age, height, sex) VALUES (%s, %s, %s, %s, %s);''', (12345, 'Alex', 32, 1.65, 'М'))
# # print('OK')
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
    bot.register_next_step_handler(msg, callback_worker)

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
            with sqlite3.connect('fit_o_bot.db') as con:
                cursor = con.cursor()
                cursor.execute('''
                       INSERT INTO bot_users_list (user_id, name, age, height, sex)
                       VALUES (?, ?, ?, ?, ?);''', (msg.from_user.id, name, age, height, sex))
                con.commit()
                cursor.close()
            with psycopg2.connect(db_URL, sslmode = "require") as postgre_con:
                db_obj = postgre_con.cursor()
                db_obj.execute(
                    '''INSERT INTO bot_users_list (user_id, name, age, height, sex) 
                    VALUES (%s, %s, %s, %s, %s);''', (msg.from_user.id, name, age, height, sex))
                postgre_con.commit()
                db_obj.close()
            message = bot.send_message(msg.from_user.id, f'''Привет! Приятно познакомиться, {name} 😜. Выбирай интересующую тебя тему:) И при первом использовании не забудь ввести свой текущий вес!)''')
            send_keyboard(msg)
    except Exception as e:
        bot.reply_to(msg, 'Что-то не так.. проверь корректность ввода и давай попробуем еще раз 🙏')
def activity_keyboard(message, text):
    activitykeyboard = types.ReplyKeyboardMarkup(row_width=1)
    but0 = types.KeyboardButton('Низкая активность 🐌')
    but1 = types.KeyboardButton('Средняя активность 🏄‍♀️🏄‍♂️')
    but2 = types.KeyboardButton('Высокая активность 🏋️ 🔥 🏋️')
    activitykeyboard.add(but0, but1, but2)
    msg = bot.send_message(message.from_user.id, '''
    В соответствии со своей активностью нажми на нужую кнопку 😉.
    \n- Низкая активность 🐌 (не тренируешься, но иногда получается гулять)
    \n- Средняя активность 🏄‍♀️🏄‍♂️ (1-2 тренировки в неделю, ежедневная ходьба по 1,5-2 часа в день)
    \n- Высокая активность 🏋️‍♂️ 🔥 🏋️‍♀️(> 3 силовых/кардио тренировки в неделю, ежедневная ходьба более 2 часов)
    ''', reply_markup = activitykeyboard)
    if text == "Хочу поднабрать массы 💪":
        bot.register_next_step_handler(msg, increase_weight)
    elif text == "Хочу согнать жирок 🥦":
        bot.register_next_step_handler(msg, decrease_weight)

def pretiffy(last_val):
    for val in last_val:
        last_v = val[0]
        return last_v

def increase_weight(msg):
    # try:
if msg.text == "Низкая активность 🐌":
    bot.send_message(msg.chat.id, '''
    Я даже боюсь представить, какая у тебя цель набора при малоактивном образе жизни 😱! Но это точно не в рамках моих компетенций 😂
    ''')
    send_keyboard(msg)
elif msg.text == "Средняя активность 🏄‍♀️🏄‍♂️":
    # with sqlite3.connect('fit_o_bot.db') as con:
            #     con.isolation_level = None
            #     cursor = con.cursor()
            #     cursor.execute(f'SELECT weight FROM bot_users_weights_table WHERE user_id=={msg.from_user.id} ORDER BY ID DESC LIMIT 1')
            #     last_weight = float(pretiffy(cursor.fetchall()))
            #     print(last_weight)
            #     cursor.execute(f'SELECT sex FROM bot_users_list WHERE user_id=={msg.from_user.id} ORDER BY ID DESC LIMIT 1')
            #     sex = pretiffy(cursor.fetchall())
            #     cursor.execute(f'SELECT age FROM bot_users_list WHERE user_id=={msg.from_user.id} ORDER BY ID DESC LIMIT 1')
            #     age = int(pretiffy(cursor.fetchall()))
            #     cursor.execute(f'SELECT height FROM bot_users_list WHERE user_id=={msg.from_user.id} ORDER BY ID DESC LIMIT 1')
            #     height = float(pretiffy(cursor.fetchall()))
    with psycopg2.connect(db_URL, sslmode="require") as postgre_con:
        db_obj = postgre_con.cursor()
        db_obj.execute(f'SELECT weight FROM bot_users_weights_table WHERE user_id=={msg.from_user.id} ORDER BY ID DESC LIMIT 1')
        last_weight = float(pretiffy(db_obj.fetchall()))
        db_obj.execute(f'SELECT age FROM bot_users_list WHERE user_id=={msg.from_user.id} ORDER BY ID DESC LIMIT 1')
        age = int(pretiffy(db_obj.fetchall()))
        db_obj.execute(f'SELECT height FROM bot_users_list WHERE user_id=={msg.from_user.id} ORDER BY ID DESC LIMIT 1')
        height = float(pretiffy(db_obj.fetchall()))
        postgre_con.commit()
        db_obj.close()
        if sex == 'М':
            target_calories = round(1.2 * (13.397 * last_weight + 88.362 + 4.799 * height * 100 - 5.677 * age))
            water_quantity = round(((target_calories/ 1000) * 1),2)
            fat_nutrient = round((0.35 * target_calories) / 9)
            protein_nutrient = round((0.25 * target_calories) / 4)
            carbs_nutrient = round((0.4 * target_calories) / 4)
            bot.send_message(msg.chat.id, f'''
            Такс 🤔, судя по имеющимся у меня данным твой текущий и последний записанный вес составляет {last_weight} кг. Рост = {height} м; Возраст = {age}; Пол: {sex}.
            \nЕсли это не так - тебе нужно обновить информацию, в соответствующих командах, иначе расчет будет некорректным 😔.
            \nДля достижения цели тебе следует придерживаться следующих ежесуточных пропорций в питании:
            \n- {fat_nutrient} г жиров;
            \n- {protein_nutrient} г белков;
            \n- {carbs_nutrient} г углеводов.
            \n- А также выпивать не меньше, чем {water_quantity} л чистой воды!
            \nИтого твой суммарный рацион за день составит {target_calories} ккал.
            \nДля подсчета и записи будут очень полезны соответствующие приложения, а также кухонные весы. Не забывай, что зачастую каллорийность продукта указана на сухой (не готовый) продукт. Поэтому взвешивать все проще до готовки. Углеводы постарайся использовать медленные, а жиры - полезные.
            \nПо достижении целевого веса, можешь обновить данные и я произведу перерасчет под новую цель.
            \nУдачи! Все получится ☺️
            ''')
            send_keyboard(msg)
        # elif sex == 'Ж':
        #             target_calories = round(1.2 * (9.247 * last_weight + 447.593 + 3.098 * height * 100 - 4.33 * age))
        #             water_quantity = round(((target_calories / 1000) * 1), 2)
        #             fat_nutrient = round((0.35 * target_calories) / 9)
        #             protein_nutrient = round((0.25 * target_calories) / 4)
        #             carbs_nutrient = round((0.4 * target_calories) / 4)
        #             bot.send_message(msg.chat.id, f'''
        #             Такс 🤔, судя по имеющимся у меня данным твой текущий и последний записанный вес составляет {last_weight} кг. Рост = {height} м; Возраст = {age}; Пол: {sex}.
        #             \nЕсли это не так - тебе нужно обновить информацию, в соответствующих командах, иначе расчет будет некорректным 😔.
        #             \nДля достижения цели тебе следует придерживаться следующих ежесуточных пропорций в питании:
        #             \n- {fat_nutrient} г жиров;
        #             \n- {protein_nutrient} г белков;
        #             \n- {carbs_nutrient} г углеводов.
        #             \n- А также выпивать не меньше, чем {water_quantity} л чистой воды!
        #             \nИтого твой суммарный рацион за день составит {target_calories} ккал.
        #             \nДля подсчета и записи будут очень полезны соответствующие приложения, а также кухонные весы. Не забывай, что зачастую каллорийность продукта указана на сухой (не готовый) продукт. Поэтому взвешивать все проще до готовки. Углеводы постарайся использовать медленные, а жиры - полезные.
        #             \nПо достижении целевого веса, можешь обновить данные и я произведу перерасчет под новую цель.
        #             \nУдачи! Все получится ☺️
        #             ''')
        #             send_keyboard(msg)
        # elif msg.text == "Высокая активность 🏋️ 🔥 🏋️":
        #     with sqlite3.connect('fit_o_bot.db') as con:
        #         con.isolation_level = None
        #         cursor = con.cursor()
        #         cursor.execute(f'SELECT weight FROM bot_users_weights_table WHERE user_id=={msg.from_user.id} ORDER BY ID DESC LIMIT 1')
        #         last_weight = float(pretiffy(cursor.fetchall()))
        #         cursor.execute(f'SELECT sex FROM bot_users_list WHERE user_id=={msg.from_user.id} ORDER BY ID DESC LIMIT 1')
        #         sex = pretiffy(cursor.fetchall())
        #         cursor.execute(f'SELECT age FROM bot_users_list WHERE user_id=={msg.from_user.id} ORDER BY ID DESC LIMIT 1')
        #         age = int(pretiffy(cursor.fetchall()))
        #         cursor.execute(f'SELECT height FROM bot_users_list WHERE user_id=={msg.from_user.id} ORDER BY ID DESC LIMIT 1')
        #         height = float(pretiffy(cursor.fetchall()))
        #         if sex == 'М':
        #             target_calories = round(1.4 * (13.397 * last_weight + 88.362 + 4.799 * height * 100 - 5.677 * age))
        #             water_quantity = round(((target_calories/ 1000) * 1),2)
        #             fat_nutrient = round((0.3 * target_calories) / 9)
        #             protein_nutrient = round((0.3 * target_calories) / 4)
        #             carbs_nutrient = round((0.4 * target_calories) / 4)
        #             bot.send_message(msg.chat.id, f'''
        #             Такс 🤔, судя по имеющимся у меня данным твой текущий и последний записанный вес составляет {last_weight} кг. Рост = {height} м; Возраст = {age}; Пол: {sex}.
        #             \nЕсли это не так - тебе нужно обновить информацию, в соответствующих командах, иначе расчет будет некорректным 😔.
        #             \nДля достижения цели тебе следует придерживаться следующих ежесуточных пропорций в питании:
        #             \n- {fat_nutrient} г жиров;
        #             \n- {protein_nutrient} г белков;
        #             \n- {carbs_nutrient} г углеводов.
        #             \n- А также выпивать не меньше, чем {water_quantity} л чистой воды!
        #             \nИтого твой суммарный рацион за день составит {target_calories} ккал.
        #             \nДля подсчета и записи будут очень полезны соответствующие приложения, а также кухонные весы. Не забывай, что зачастую каллорийность продукта указана на сухой (не готовый) продукт. Поэтому взвешивать все проще до готовки. Углеводы постарайся использовать медленные, а жиры - полезные.
        #             \nПо достижении целевого веса, можешь обновить данные и я произведу перерасчет под новую цель.
        #             \nУдачи! Все получится ☺️
        #             ''')
        #             cursor.close()
        #             send_keyboard(msg)
        #         elif sex == 'Ж':
        #             target_calories = round(1.4 * (9.247 * last_weight + 447.593 + 3.098 * height * 100 - 4.33 * age))
        #             water_quantity = round(((target_calories / 1000) * 1), 2)
        #             fat_nutrient = round((0.3 * target_calories) / 9)
        #             protein_nutrient = round((0.3 * target_calories) / 4)
        #             carbs_nutrient = round((0.4 * target_calories) / 4)
        #             bot.send_message(msg.chat.id, f'''
        #             Такс 🤔, судя по имеющимся у меня данным твой текущий и последний записанный вес составляет {last_weight} кг. Рост = {height} м; Возраст = {age}; Пол: {sex}.
        #             \nЕсли это не так - тебе нужно обновить информацию, в соответствующих командах, иначе расчет будет некорректным 😔.
        #             \nДля достижения цели тебе следует придерживаться следующих ежесуточных пропорций в питании:
        #             \n- {fat_nutrient} г жиров;
        #             \n- {protein_nutrient} г белков;
        #             \n- {carbs_nutrient} г углеводов.
        #             \n- А также выпивать не меньше, чем {water_quantity} л чистой воды!
        #             \nИтого твой суммарный рацион за день составит {target_calories} ккал.
        #             \nДля подсчета и записи будут очень полезны соответствующие приложения, а также кухонные весы. Не забывай, что зачастую каллорийность продукта указана на сухой (не готовый) продукт. Поэтому взвешивать все проще до готовки. Углеводы постарайся использовать медленные, а жиры - полезные.
        #             \nПо достижении целевого веса, можешь обновить данные и я произведу перерасчет под новую цель.
        #             \nУдачи! Все получится ☺️
        #             ''')
        #             cursor.close()
        #             send_keyboard(msg)
    # except:
    #     bot.send_message(msg.chat.id, '''
    #     Кажется, мне не достает данных, проверь был ли введен вес и первичные данные, которые вводились на старте 😉
    #     ''')
    #     send_keyboard(msg)

def decrease_weight(msg):
    try:
        if msg.text == "Низкая активность 🐌":
            with sqlite3.connect('fit_o_bot.db') as con:
                con.isolation_level = None
                cursor = con.cursor()
                cursor.execute(f'SELECT weight FROM bot_users_weights_table WHERE user_id=={msg.from_user.id} ORDER BY ID DESC LIMIT 1')
                last_weight = float(pretiffy(cursor.fetchall()))
                cursor.execute(f'SELECT sex FROM bot_users_list WHERE user_id=={msg.from_user.id} ORDER BY ID DESC LIMIT 1')
                sex = pretiffy(cursor.fetchall())
                cursor.execute(f'SELECT age FROM bot_users_list WHERE user_id=={msg.from_user.id} ORDER BY ID DESC LIMIT 1')
                age = int(pretiffy(cursor.fetchall()))
                cursor.execute(f'SELECT height FROM bot_users_list WHERE user_id=={msg.from_user.id} ORDER BY ID DESC LIMIT 1')
                height = float(pretiffy(cursor.fetchall()))
                if sex == 'М':
                    target_calories = round(0.8 * (13.397 * last_weight + 88.362 + 4.799 * height * 100 - 5.677 * age))
                    water_quantity = round(((target_calories/ 1000) * 1),2)
                    fat_nutrient = round((0.35 * target_calories) / 9)
                    protein_nutrient = round((0.25 * target_calories) / 4)
                    carbs_nutrient = round((0.4 * target_calories) / 4)
                    bot.send_message(msg.chat.id, f'''
                    Такс 🤔, судя по имеющимся у меня данным твой текущий и последний записанный вес составляет {last_weight} кг. Рост = {height} м; Возраст = {age}; Пол: {sex}.
                    \nЕсли это не так - тебе нужно обновить информацию, в соответствующих командах, иначе расчет будет некорректным 😔.
                    \nДля достижения цели тебе следует придерживаться следующих ежесуточных пропорций в питании:
                    \n- {fat_nutrient} г жиров;
                    \n- {protein_nutrient} г белков;
                    \n- {carbs_nutrient} г углеводов.
                    \n- А также выпивать не меньше, чем {water_quantity} л чистой воды!
                    \nИтого твой суммарный рацион за день составит {target_calories} ккал.
                    \nДля подсчета и записи будут очень полезны соответствующие приложения, а также кухонные весы. Не забывай, что зачастую каллорийность продукта указана на сухой (не готовый) продукт. Поэтому взвешивать все проще до готовки. Углеводы постарайся использовать медленные, а жиры - полезные.
                    \nПо достижении целевого веса, можешь обновить данные и я произведу перерасчет под новую цель.
                    \nУдачи! Все получится ☺️
                    ''')
                    cursor.close()
                    send_keyboard(msg)
                elif sex == 'Ж':
                    target_calories = round(0.8 * (9.247 * last_weight + 447.593 + 3.098 * height * 100 - 4.33 * age))
                    water_quantity = round(((target_calories / 1000) * 1), 2)
                    fat_nutrient = round((0.35 * target_calories) / 9)
                    protein_nutrient = round((0.25 * target_calories) / 4)
                    carbs_nutrient = round((0.4 * target_calories) / 4)
                    bot.send_message(msg.chat.id, f'''
                    Такс 🤔, судя по имеющимся у меня данным твой текущий и последний записанный вес составляет {last_weight} кг. Рост = {height} м; Возраст = {age}; Пол: {sex}.
                    \nЕсли это не так - тебе нужно обновить информацию, в соответствующих командах, иначе расчет будет некорректным 😔.
                    \nДля достижения цели тебе следует придерживаться следующих ежесуточных пропорций в питании:
                    \n- {fat_nutrient} г жиров;
                    \n- {protein_nutrient} г белков;
                    \n- {carbs_nutrient} г углеводов.
                    \n- А также выпивать не меньше, чем {water_quantity} л чистой воды!
                    \nИтого твой суммарный рацион за день составит {target_calories} ккал.
                    \nДля подсчета и записи будут очень полезны соответствующие приложения, а также кухонные весы. Не забывай, что зачастую каллорийность продукта указана на сухой (не готовый) продукт. Поэтому взвешивать все проще до готовки. Углеводы постарайся использовать медленные, а жиры - полезные.
                    \nПо достижении целевого веса, можешь обновить данные и я произведу перерасчет под новую цель.
                    \nУдачи! Все получится ☺️
                    ''')
                    cursor.close()
                    send_keyboard(msg)
        elif msg.text == "Средняя активность 🏄‍♀️🏄‍♂️":
            with sqlite3.connect('fit_o_bot.db') as con:
                con.isolation_level = None
                cursor = con.cursor()
                cursor.execute(f'SELECT weight FROM bot_users_weights_table WHERE user_id=={msg.from_user.id} ORDER BY ID DESC LIMIT 1')
                last_weight = float(pretiffy(cursor.fetchall()))
                cursor.execute(f'SELECT sex FROM bot_users_list WHERE user_id=={msg.from_user.id} ORDER BY ID DESC LIMIT 1')
                sex = pretiffy(cursor.fetchall())
                cursor.execute(f'SELECT age FROM bot_users_list WHERE user_id=={msg.from_user.id} ORDER BY ID DESC LIMIT 1')
                age = int(pretiffy(cursor.fetchall()))
                cursor.execute(f'SELECT height FROM bot_users_list WHERE user_id=={msg.from_user.id} ORDER BY ID DESC LIMIT 1')
                height = float(pretiffy(cursor.fetchall()))
                if sex == 'М':
                    target_calories = round(0.85 * (13.397 * last_weight + 88.362 + 4.799 * height * 100 - 5.677 * age))
                    water_quantity = round(((target_calories/ 1000) * 1),2)
                    fat_nutrient = round((0.35 * target_calories) / 9)
                    protein_nutrient = round((0.25 * target_calories) / 4)
                    carbs_nutrient = round((0.4 * target_calories) / 4)
                    bot.send_message(msg.chat.id, f'''
                    Такс 🤔, судя по имеющимся у меня данным твой текущий и последний записанный вес составляет {last_weight} кг. Рост = {height} м; Возраст = {age}; Пол: {sex}.
                    \nЕсли это не так - тебе нужно обновить информацию, в соответствующих командах, иначе расчет будет некорректным 😔.
                    \nДля достижения цели тебе следует придерживаться следующих ежесуточных пропорций в питании:
                    \n- {fat_nutrient} г жиров;
                    \n- {protein_nutrient} г белков;
                    \n- {carbs_nutrient} г углеводов.
                    \n- А также выпивать не меньше, чем {water_quantity} л чистой воды!
                    \nИтого твой суммарный рацион за день составит {target_calories} ккал.
                    \nДля подсчета и записи будут очень полезны соответствующие приложения, а также кухонные весы. Не забывай, что зачастую каллорийность продукта указана на сухой (не готовый) продукт. Поэтому взвешивать все проще до готовки. Углеводы постарайся использовать медленные, а жиры - полезные.
                    \nПо достижении целевого веса, можешь обновить данные и я произведу перерасчет под новую цель.
                    \nУдачи! Все получится ☺️
                    ''')
                    cursor.close()
                    send_keyboard(msg)
                elif sex == 'Ж':
                    target_calories = round(0.85 * (9.247 * last_weight + 447.593 + 3.098 * height * 100 - 4.33 * age))
                    water_quantity = round(((target_calories / 1000) * 1), 2)
                    fat_nutrient = round((0.35 * target_calories) / 9)
                    protein_nutrient = round((0.25 * target_calories) / 4)
                    carbs_nutrient = round((0.4 * target_calories) / 4)
                    bot.send_message(msg.chat.id, f'''
                    Такс 🤔, судя по имеющимся у меня данным твой текущий и последний записанный вес составляет {last_weight} кг. Рост = {height} м; Возраст = {age}; Пол: {sex}.
                    \nЕсли это не так - тебе нужно обновить информацию, в соответствующих командах, иначе расчет будет некорректным 😔.
                    \nДля достижения цели тебе следует придерживаться следующих ежесуточных пропорций в питании:
                    \n- {fat_nutrient} г жиров;
                    \n- {protein_nutrient} г белков;
                    \n- {carbs_nutrient} г углеводов.
                    \n- А также выпивать не меньше, чем {water_quantity} л чистой воды!
                    \nИтого твой суммарный рацион за день составит {target_calories} ккал.
                    \nДля подсчета и записи будут очень полезны соответствующие приложения, а также кухонные весы. Не забывай, что зачастую каллорийность продукта указана на сухой (не готовый) продукт. Поэтому взвешивать все проще до готовки. Углеводы постарайся использовать медленные, а жиры - полезные.
                    \nПо достижении целевого веса, можешь обновить данные и я произведу перерасчет под новую цель.
                    \nУдачи! Все получится ☺️
                    ''')
                    cursor.close()
                    send_keyboard(msg)
        elif msg.text == "Высокая активность 🏋️ 🔥 🏋️":
            with sqlite3.connect('fit_o_bot.db') as con:
                con.isolation_level = None
                cursor = con.cursor()
                cursor.execute(f'SELECT weight FROM bot_users_weights_table WHERE user_id=={msg.from_user.id} ORDER BY ID DESC LIMIT 1')
                last_weight = float(pretiffy(cursor.fetchall()))
                cursor.execute(f'SELECT sex FROM bot_users_list WHERE user_id=={msg.from_user.id} ORDER BY ID DESC LIMIT 1')
                sex = pretiffy(cursor.fetchall())
                cursor.execute(f'SELECT age FROM bot_users_list WHERE user_id=={msg.from_user.id} ORDER BY ID DESC LIMIT 1')
                age = int(pretiffy(cursor.fetchall()))
                cursor.execute(f'SELECT height FROM bot_users_list WHERE user_id=={msg.from_user.id} ORDER BY ID DESC LIMIT 1')
                height = float(pretiffy(cursor.fetchall()))
                if sex == 'М':
                    target_calories = round(0.9 * (13.397 * last_weight + 88.362 + 4.799 * height * 100 - 5.677 * age))
                    water_quantity = round(((target_calories/ 1000) * 1),2)
                    fat_nutrient = round((0.35 * target_calories) / 9)
                    protein_nutrient = round((0.4 * target_calories) / 4)
                    carbs_nutrient = round((0.25 * target_calories) / 4)
                    bot.send_message(msg.chat.id, f'''
                    Такс 🤔, судя по имеющимся у меня данным твой текущий и последний записанный вес составляет {last_weight} кг. Рост = {height} м; Возраст = {age}; Пол: {sex}.
                    \nЕсли это не так - тебе нужно обновить информацию, в соответствующих командах, иначе расчет будет некорректным 😔.
                    \nДля достижения цели тебе следует придерживаться следующих ежесуточных пропорций в питании:
                    \n- {fat_nutrient} г жиров;
                    \n- {protein_nutrient} г белков;
                    \n- {carbs_nutrient} г углеводов.
                    \n- А также выпивать не меньше, чем {water_quantity} л чистой воды!
                    \nИтого твой суммарный рацион за день составит {target_calories} ккал.
                    \nДля подсчета и записи будут очень полезны соответствующие приложения, а также кухонные весы. Не забывай, что зачастую каллорийность продукта указана на сухой (не готовый) продукт. Поэтому взвешивать все проще до готовки. Углеводы постарайся использовать медленные, а жиры - полезные.
                    \nПо достижении целевого веса, можешь обновить данные и я произведу перерасчет под новую цель.
                    \nУдачи! Все получится ☺️
                    ''')
                    cursor.close()
                    send_keyboard(msg)
                elif sex == 'Ж':
                    target_calories = round(0.9 * (9.247 * last_weight + 447.593 + 3.098 * height * 100 - 4.33 * age))
                    water_quantity = round(((target_calories / 1000) * 1), 2)
                    fat_nutrient = round((0.35 * target_calories) / 9)
                    protein_nutrient = round((0.4 * target_calories) / 4)
                    carbs_nutrient = round((0.25 * target_calories) / 4)
                    bot.send_message(msg.chat.id, f'''
                    Такс 🤔, судя по имеющимся у меня данным твой текущий и последний записанный вес составляет {last_weight} кг. Рост = {height} м; Возраст = {age}; Пол: {sex}.
                    \nЕсли это не так - тебе нужно обновить информацию, в соответствующих командах, иначе расчет будет некорректным 😔.
                    \nДля достижения цели тебе следует придерживаться следующих ежесуточных пропорций в питании:
                    \n- {fat_nutrient} г жиров;
                    \n- {protein_nutrient} г белков;
                    \n- {carbs_nutrient} г углеводов.
                    \n- А также выпивать не меньше, чем {water_quantity} л чистой воды!
                    \nИтого твой суммарный рацион за день составит {target_calories} ккал.
                    \nДля подсчета и записи будут очень полезны соответствующие приложения, а также кухонные весы. Не забывай, что зачастую каллорийность продукта указана на сухой (не готовый) продукт. Поэтому взвешивать все проще до готовки. Углеводы постарайся использовать медленные, а жиры - полезные.
                    \nПо достижении целевого веса, можешь обновить данные и я произведу перерасчет под новую цель.
                    \nУдачи! Все получится ☺️
                    ''')
                    cursor.close()
                    send_keyboard(msg)
    except:
        bot.send_message(msg.chat.id, '''
        Кажется, мне не достает данных, проверь был ли введен вес и первичные данные, которые вводились на старте 😉
        ''')
        send_keyboard(msg)

def callback_worker(call):
    if call.text == "Хочу сообщить свой текущий вес 😱":
        print(call.text)
        print('ohhh')
        msg = bot.send_message(call.chat.id, f'''
        \nНе бойся, отправляй свой текущий вес, на своем веку я видал многое..
        \nПрисылай в формате текущей даты и веса разделенных пробелом, мне нужно записать это в свой журнал:)
        \nНужен следующий формат: dd-mm-yyyy 85.4 где первая часть - дата (например: 16-04-1996), а вторая - вес.''')
        bot.register_next_step_handler(msg, add_weight)
    elif call.text == "Хочу согнать жирок 🥦":
        try:
            activity_keyboard(call, text = "Хочу согнать жирок 🥦")
        except:
            bot.send_message(call.chat.id, 'Кажется, нет данных о твоем весе, необходимо сначала их ввести 😛')
            send_keyboard(call, "Чем еще могу помочь?")
    elif call.text == "Хочу поднабрать массы 💪":
        activity_keyboard(call, text = "Хочу поднабрать массы 💪")
    elif call.text == "Хочу посмотреть статистику своего веса 😈":
        try:
            weight_statistic(call)
        except:
            bot.send_message(call.chat.id, 'Кажется, нет данных о твоем весе, необходимо сначала их ввести 😛')
            send_keyboard(call, "Чем еще могу помочь?")
    elif call.text == "Удалить последнюю запись веса":
        try:
            delete_last(call)
        except:
            bot.send_message(call.chat.id, 'Кажется, нет данных о твоем весе, необходимо сначала их ввести 😛')
            send_keyboard(call, "Чем еще могу помочь?")
    elif call.text == "Удалить все записи веса":
        try:
            delete_all(call)
        except:
            bot.send_message(call.chat.id, 'Кажется, нет данных, необходимо сначала их ввести 😛')
            send_keyboard(call, "Чем еще могу помочь?")
    elif call.text == "Очистить данные из базы (имя, возраст, пол, рост)":
        try:
            delete_user_info(call)
        except:
            bot.send_message(call.chat.id, 'Кажется, нет данных, необходимо сначала их ввести 😛')
            send_keyboard(call, "Чем еще могу помочь?")

def add_weight(msg):
    current_date = msg.text.split()[0]
    current_weight = msg.text.split()[1]
    try:
        float(current_weight)
        current_weight = float(current_weight)
        dt_obj = dt.datetime.strptime(f"{current_date}", "%d-%m-%Y").date()
        # with sqlite3.connect('fit_o_bot.db') as con:
        #     con.isolation_level = None
        #     cursor = con.cursor()
        #     cursor.execute('''
        #     INSERT INTO bot_users_weights_table (user_id, date, weight)
        #     VALUES (?, ?, ?);''', (msg.from_user.id, current_date, current_weight))
        #     cursor.close()
        with psycopg2.connect(db_URL, sslmode = "require") as postgre_con:
            db_obj = postgre_con.cursor()
            db_obj.execute(
                '''INSERT INTO bot_users_weights_table (user_id, date, weight) 
                VALUES (%s, %s, %s);''', (msg.from_user.id, current_date, current_weight))
            postgre_con.commit()
            db_obj.close()
            bot.send_message(msg.chat.id, 'Зафиксировал!😨 Как когда-то сказал Аристотель: \"Познание всегда начинается с удивления\"..')
            send_keyboard(msg)

    except:
        bot.send_message(msg.chat.id, 'Введен некорректный формат 😟. Попробуй еще раз 😉')
        send_keyboard(msg)

def get_nice(data_list):
    data_str = []
    print(data_str)
    for val in list(data_list):
        data_str.append(f'{val[0]} = {val[1]} кг\n')
    return ''.join(data_str)

def weight_statistic(msg):
    with sqlite3.connect('fit_o_bot.db') as con:
        con.isolation_level = None
        cursor = con.cursor()
        cursor.execute(f'SELECT date, weight FROM bot_users_weights_table WHERE user_id=={msg.from_user.id}')
        c = cursor.fetchall()
        data_list = get_nice(c)
        bot.send_message(msg.chat.id, data_list)
        send_keyboard(msg, "Ох! Сначала подумал, что это пример геометрической прогрессии, а оказалось..")

def delete_last(msg):
    with sqlite3.connect('fit_o_bot.db') as con:
        con.isolation_level = None
        cursor = con.cursor()
        cursor.execute(f'DELETE FROM bot_users_weights_table WHERE user_id=={msg.from_user.id} ORDER BY ID DESC LIMIT 1')
        cursor.close()
        bot.send_message(msg.chat.id, 'Прошло успешно!')
        send_keyboard(msg, "Чем еще могу помочь?")

def delete_all(msg):
    with sqlite3.connect('fit_o_bot.db') as con:
        con.isolation_level = None
        cursor = con.cursor()
        cursor.execute(f'DELETE FROM bot_users_weights_table WHERE user_id=={msg.from_user.id}')
        cursor.close()
        bot.send_message(msg.chat.id, 'И начнем все с чистого листа! 🥂')
        send_keyboard(msg, "Чем еще могу помочь?")

def delete_user_info(msg):
    with sqlite3.connect('fit_o_bot.db') as con:
        con.isolation_level = None
        cursor = con.cursor()
        cursor.execute(f'DELETE FROM bot_users_list WHERE user_id=={msg.from_user.id}')
        cursor.close()
        bot.send_message(msg.chat.id, 'Все данные удалены 🥳')
        send_keyboard(msg, "Чем еще могу помочь?")

@bot.message_handler(content_types=['text'])

def sorry(message):
    send_keyboard(message, text="Я не понимаю!🌚 Выбери один из пунктов меню:")

bot.infinity_polling()