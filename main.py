import telebot
from telebot import types
import datetime as dt
import psycopg2
bot = telebot.TeleBot("5058162485:AAGSB2FehnhupFU5ViiEwRgypDMJmddcpmg")
bot.delete_webhook()
db_URL = "postgres://qmvydayqnuuxxz:40dc9792c9d15977ed989756198fbbba01983157173a98d5840e92c8c71928a8@ec2-54-74-102-48.eu-west-1.compute.amazonaws.com:5432/dcanatqglrancq"
db_con = psycopg2.connect(db_URL, sslmode = "require")
backslash = "\\"
warning = "Рекомендация носит исключительно ознакомительный характер\\. Перед применением проконсультируйтесь со специалистом\\."

@bot.message_handler(commands=['start'])
def send_welcome(message):
    msg = bot.reply_to(message, '''Хэй\! Меня зовут Фитобот😊 А тебя как? Напиши, пожалуйста: свое *имя*, *возраст*, *рост* \(в сантиметрах\) и *пол* \(русскоязычной раскладкой м/ж\) на моем примере \(обязательно следуй формату, если с первого раза не получится \- вызови повторно команду start и повтори попытку, данные пишем через пробел\):
    \n*Фитобот 25 175 М*''', parse_mode="MarkdownV2")
    bot.register_next_step_handler(msg, user_name)

def send_keyboard(message, text = "Выбери интересующий раздел 😉"):
    keyboard = types.ReplyKeyboardMarkup(row_width=2)
    itembtn0 = types.KeyboardButton('Хочу сообщить свой вес 😱')
    itembtn1 = types.KeyboardButton('Хочу посмотреть статистику своего веса 😈')
    itembtn2 = types.KeyboardButton('Хочу согнать жирок 🥦')
    itembtn3 = types.KeyboardButton('Хочу поднабрать массы 💪')
    itembtn4 = types.KeyboardButton('Удалить последнюю запись веса')
    itembtn5 = types.KeyboardButton("Удалить все записи веса")
    itembtn6 = types.KeyboardButton("Не худею/не набираю 👿")
    itembtn7 = types.KeyboardButton("Очистить данные из базы (имя, возраст, пол, рост)")
    keyboard.add(itembtn0, itembtn1, itembtn2, itembtn3, itembtn4, itembtn5, itembtn6, itembtn7)
    msg = bot.send_message(message.from_user.id,text=text, reply_markup=keyboard)
    bot.register_next_step_handler(msg, callback_worker)

def user_name(msg):
    try:
        name = msg.text.split()[0].title()
        age = msg.text.split()[1]
        age = int(age)
        height = msg.text.split()[2]
        height = int(height)
        sex = msg.text.split()[3].title()
        if sex == 'М' or sex == 'Ж':
            try:
                with psycopg2.connect(db_URL, sslmode="require") as postgre_con:
                    db_obj = postgre_con.cursor()
                    db_obj.execute(f'DELETE FROM bot_users_list WHERE "user_id"={msg.from_user.id}')
                    postgre_con.commit()
                    db_obj.execute(
                        '''INSERT INTO bot_users_list (user_id, name, age, height, sex) 
                        VALUES (%s, %s, %s, %s, %s);''', (msg.from_user.id, name, age, height, sex))
                    postgre_con.commit()
                    db_obj.close()
                    message = bot.send_message(msg.from_user.id, f'''Привет! Приятно познакомиться, {name} 😜. Выбирай интересующую тебя тему:) И при первом использовании не забудь ввести свой текущий вес!)''')
                    send_keyboard(msg)
            except:
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
        bot.register_next_step_handler(msg, diet_type())

def diet_type(message, text):
    activitykeyboard = types.ReplyKeyboardMarkup(row_width=2)
    b0 = types.KeyboardButton('Низкоуглеводка 🍤🥜🥩')
    b1 = types.KeyboardButton('Классика 🍝🍗🥙')
    activitykeyboard.add(b0, b1)
    msg = bot.send_message(message.from_user.id, f'''
    Что выбираешь?
    \n◌ *Низкоуглеводка* {backslash}- даст более быстрый результат жиросжигания{backslash}. Имеет ряд противопоказаний{backslash}. Но также имеет и ряд положительных свойств 😉
    \n◌ *Классика* {backslash}- общепринятые пропорции белков, жиров и углеводов{backslash}.
    ''', reply_markup = activitykeyboard, parse_mode="MarkdownV2")
    if text == "Низкая активность 🐌":
        bot.register_next_step_handler(msg, low_activity_decrease)
    elif text == "Средняя активность 🏄‍♀️🏄‍♂️":
        bot.register_next_step_handler(msg, middle_activity_decrease)
    elif text == "Высокая активность 🏋️ 🔥 🏋️️":
        bot.register_next_step_handler(msg, high_activity_decrease)

def low_activity_decrease(msg):
    try:
        if msg.text == "Низкоуглеводка 🍤🥜🥩":
            with psycopg2.connect(db_URL, sslmode="require") as postgre_con:
                db_obj = postgre_con.cursor()
                db_obj.execute(f'''
                SELECT weight
                FROM
                    (
                    SELECT weight, to_date(date, 'DD/MM/YYYY') as date_form
                    FROM bot_users_weights_table
                    WHERE "user_id"={msg.from_user.id}
                    ORDER BY date_form
                    DESC LIMIT 1) 
                    AS last_weight''')
                last_weight = float(pretiffy(db_obj.fetchall()))
                db_obj.execute(f'SELECT sex FROM bot_users_list WHERE "user_id"={msg.from_user.id} ORDER BY ID DESC LIMIT 1')
                sex = pretiffy(db_obj.fetchall())
                db_obj.execute(f'SELECT age FROM bot_users_list WHERE "user_id"={msg.from_user.id} ORDER BY ID DESC LIMIT 1')
                age = int(pretiffy(db_obj.fetchall()))
                db_obj.execute(f'SELECT height FROM bot_users_list WHERE "user_id"={msg.from_user.id} ORDER BY ID DESC LIMIT 1')
                height = int(pretiffy(db_obj.fetchall()))
                postgre_con.commit()
                db_obj.close()
                if sex == 'М':
                    target_calories = round((1.2 * (10 * last_weight) + (6.25 * height) - (5 * age) + 5) - 200)
                    water_quantity = round((target_calories / 1000), 2)
                    fat_nutrient = round((0.45 * target_calories) / 9)
                    protein_nutrient = round((0.45 * target_calories) / 4)
                    carbs_nutrient = round((0.1 * target_calories) / 4)
                    last_weight_str = str(last_weight).replace('.', '\.')
                    water_quantity_str = str(water_quantity).replace('.', '\.')
                    bot.send_message(msg.chat.id, f'''
                    🤔 По моим данным твой текущий вес составляет *{last_weight_str}* кг{backslash}. Рост {backslash}= *{height}* cм{backslash}. Возраст {backslash}= *{age}*{backslash}. Пол {backslash}= *мужской*{backslash}.
                    \nЕсли это не так {backslash}- тебе нужно обновить информацию, в соответствующих командах, иначе расчет будет некорректным 😔{backslash}.
                    \nДля достижения цели тебе следует придерживаться следующих ежесуточных пропорций в питании:
                    \n★ *{fat_nutrient}* г жиров;
                    \n★ *{protein_nutrient}* г белков;
                    \n★ *{carbs_nutrient}* г углеводов{backslash}.
                    \n★ А также выпивать не меньше, чем *{water_quantity_str}* л чистой воды{backslash}!
                    \nИтого твой суммарный рацион за день составит *{target_calories}* калорий{backslash}.
                    \n{warning}
                    \nДля подсчета рациона тебе пригодятся соответствующие приложения и необходимо приобрести кухонные весы{backslash}. Подробнее про питание и тренировки узнаешь в *@fit{backslash}_o{backslash}_blog* 😎
                    \nУдачи{backslash}! Все получится ☺️
                    ''', parse_mode="MarkdownV2")
                    send_keyboard(msg)
                elif sex == 'Ж':
                    target_calories = round((1.2 * (10 * last_weight) + (6.25 * height) - (5 * age) + 5) - 350)
                    water_quantity = round((target_calories / 1000), 2)
                    fat_nutrient = round((0.45 * target_calories) / 9)
                    protein_nutrient = round((0.45 * target_calories) / 4)
                    carbs_nutrient = round((0.1 * target_calories) / 4)
                    last_weight_str = str(last_weight).replace('.', '\.')
                    water_quantity_str = str(water_quantity).replace('.', '\.')
                    bot.send_message(msg.chat.id, f'''
                    🤔 По моим данным твой текущий и последний записанный вес составляет *{last_weight_str}* кг{backslash}. Рост {backslash}= *{height}* cм{backslash}. Возраст {backslash}= *{age}*{backslash}. Пол {backslash}= *женский*{backslash}.
                    \nЕсли это не так {backslash}- тебе нужно обновить информацию, в соответствующих командах, иначе расчет будет некорректным 😔{backslash}.
                    \nДля достижения цели тебе следует придерживаться следующих ежесуточных пропорций в питании:
                    \n★ *{fat_nutrient}* г жиров;
                    \n★ *{protein_nutrient}* г белков;
                    \n★ *{carbs_nutrient}* г углеводов{backslash}.
                    \n★ А также выпивать не меньше, чем *{water_quantity_str}* л чистой воды{backslash}!
                    \nИтого твой суммарный рацион за день составит *{target_calories}* калорий{backslash}.
                    \n{warning}
                    \nДля подсчета рациона тебе пригодятся соответствующие приложения и необходимо приобрести кухонные весы{backslash}. Подробнее про питание и тренировки узнаешь в *@fit{backslash}_o{backslash}_blog* 😎
                    \nУдачи{backslash}! Все получится ☺️
                    ''', parse_mode="MarkdownV2")
                    send_keyboard(msg)
        elif msg.text == "Классика 🍝🍗🥙":
            with psycopg2.connect(db_URL, sslmode="require") as postgre_con:
                db_obj = postgre_con.cursor()
                db_obj.execute(f'''
                SELECT weight
                FROM
                    (
                    SELECT weight, to_date(date, 'DD/MM/YYYY') as date_form
                    FROM bot_users_weights_table
                    WHERE "user_id"={msg.from_user.id}
                    ORDER BY date_form
                    DESC LIMIT 1) 
                    AS last_weight''')
                last_weight = float(pretiffy(db_obj.fetchall()))
                db_obj.execute(f'SELECT sex FROM bot_users_list WHERE "user_id"={msg.from_user.id} ORDER BY ID DESC LIMIT 1')
                sex = pretiffy(db_obj.fetchall())
                db_obj.execute(f'SELECT age FROM bot_users_list WHERE "user_id"={msg.from_user.id} ORDER BY ID DESC LIMIT 1')
                age = int(pretiffy(db_obj.fetchall()))
                db_obj.execute(f'SELECT height FROM bot_users_list WHERE "user_id"={msg.from_user.id} ORDER BY ID DESC LIMIT 1')
                height = int(pretiffy(db_obj.fetchall()))
                postgre_con.commit()
                db_obj.close()
                if sex == 'М':
                    target_calories = round(0.8 * (13.397 * last_weight + 88.362 + 4.799 * height - 5.677 * age))
                    water_quantity = round(((target_calories / 1000) * 1), 2)
                    fat_nutrient = round((0.35 * target_calories) / 9)
                    protein_nutrient = round((0.25 * target_calories) / 4)
                    carbs_nutrient = round((0.4 * target_calories) / 4)
                    last_weight_str = str(last_weight).replace('.', '\.')
                    water_quantity_str = str(water_quantity).replace('.', '\.')
                    bot.send_message(msg.chat.id, f'''
                    🤔 По моим данным твой текущий и последний записанный вес составляет *{last_weight_str}* кг{backslash}. Рост {backslash}= *{height}* cм{backslash}. Возраст {backslash}= *{age}*{backslash}. Пол {backslash}= *мужской*{backslash}.
                    \nЕсли это не так {backslash}- тебе нужно обновить информацию, в соответствующих командах, иначе расчет будет некорректным 😔{backslash}.
                    \nДля достижения цели тебе следует придерживаться следующих ежесуточных пропорций в питании:
                    \n★ *{fat_nutrient}* г жиров;
                    \n★ *{protein_nutrient}* г белков;
                    \n★ *{carbs_nutrient}* г углеводов{backslash}.
                    \n★ А также выпивать не меньше, чем *{water_quantity_str}* л чистой воды{backslash}!
                    \nИтого твой суммарный рацион за день составит *{target_calories}* калорий{backslash}.
                    \n{warning}
                    \nДля подсчета рациона тебе пригодятся соответствующие приложения и необходимо приобрести кухонные весы{backslash}. Подробнее про питание и тренировки узнаешь в *@fit{backslash}_o{backslash}_blog* 😎
                    \nУдачи{backslash}! Все получится ☺️
                    ''', parse_mode="MarkdownV2")
                    send_keyboard(msg)
                elif sex == 'Ж':
                    target_calories = round(0.8 * (9.247 * last_weight + 447.593 + 3.098 * height - 4.33 * age))
                    water_quantity = round(((target_calories / 1000) * 1), 2)
                    fat_nutrient = round((0.35 * target_calories) / 9)
                    protein_nutrient = round((0.25 * target_calories) / 4)
                    carbs_nutrient = round((0.4 * target_calories) / 4)
                    last_weight_str = str(last_weight).replace('.', '\.')
                    water_quantity_str = str(water_quantity).replace('.', '\.')
                    bot.send_message(msg.chat.id, f'''
                    🤔 По моим данным твой текущий и последний записанный вес составляет *{last_weight_str}* кг{backslash}. Рост {backslash}= *{height}* cм{backslash}. Возраст {backslash}= *{age}*{backslash}. Пол {backslash}= *женский*{backslash}.
                    \nЕсли это не так {backslash}- тебе нужно обновить информацию, в соответствующих командах, иначе расчет будет некорректным 😔{backslash}.
                    \nДля достижения цели тебе следует придерживаться следующих ежесуточных пропорций в питании:
                    \n★ *{fat_nutrient}* г жиров;
                    \n★ *{protein_nutrient}* г белков;
                    \n★ *{carbs_nutrient}* г углеводов{backslash}.
                    \n★ А также выпивать не меньше, чем *{water_quantity_str}* л чистой воды{backslash}!
                    \nИтого твой суммарный рацион за день составит *{target_calories}* калорий{backslash}.
                    \n{warning}
                    \nДля подсчета рациона тебе пригодятся соответствующие приложения и необходимо приобрести кухонные весы{backslash}. Подробнее про питание и тренировки узнаешь в *@fit{backslash}_o{backslash}_blog* 😎
                    \nУдачи{backslash}! Все получится ☺️
                    ''', parse_mode="MarkdownV2")
                    send_keyboard(msg)
    except Exception as e:
        bot.send_message(msg.chat.id, '''
        Кажется, мне не достает данных, проверь был ли введен вес и первичные данные, которые вводились на старте 😉
        ''')
        send_keyboard(msg)

def middle_activity_decrease(msg):
    try:
        if msg.text == "Низкоуглеводка 🍤🥜🥩":
            with psycopg2.connect(db_URL, sslmode="require") as postgre_con:
                db_obj = postgre_con.cursor()
                db_obj.execute(f'''
                SELECT weight
                FROM
                    (
                    SELECT weight, to_date(date, 'DD/MM/YYYY') as date_form
                    FROM bot_users_weights_table
                    WHERE "user_id"={msg.from_user.id}
                    ORDER BY date_form
                    DESC LIMIT 1) 
                    AS last_weight''')
                last_weight = float(pretiffy(db_obj.fetchall()))
                db_obj.execute(f'SELECT sex FROM bot_users_list WHERE "user_id"={msg.from_user.id} ORDER BY ID DESC LIMIT 1')
                sex = pretiffy(db_obj.fetchall())
                db_obj.execute(f'SELECT age FROM bot_users_list WHERE "user_id"={msg.from_user.id} ORDER BY ID DESC LIMIT 1')
                age = int(pretiffy(db_obj.fetchall()))
                db_obj.execute(f'SELECT height FROM bot_users_list WHERE "user_id"={msg.from_user.id} ORDER BY ID DESC LIMIT 1')
                height = int(pretiffy(db_obj.fetchall()))
                postgre_con.commit()
                db_obj.close()
                if sex == 'М':
                    target_calories = round((1.375 * (10 * last_weight) + (6.25 * height) - (5 * age) + 5) - 200)
                    water_quantity = round((target_calories / 1000), 2)
                    fat_nutrient = round((0.45 * target_calories) / 9)
                    protein_nutrient = round((0.45 * target_calories) / 4)
                    carbs_nutrient = round((0.1 * target_calories) / 4)
                    last_weight_str = str(last_weight).replace('.', '\.')
                    water_quantity_str = str(water_quantity).replace('.', '\.')
                    bot.send_message(msg.chat.id, f'''
                    🤔 По моим данным твой текущий вес составляет *{last_weight_str}* кг{backslash}. Рост {backslash}= *{height}* cм{backslash}. Возраст {backslash}= *{age}*{backslash}. Пол {backslash}= *мужской*{backslash}.
                    \nЕсли это не так {backslash}- тебе нужно обновить информацию, в соответствующих командах, иначе расчет будет некорректным 😔{backslash}.
                    \nДля достижения цели тебе следует придерживаться следующих ежесуточных пропорций в питании:
                    \n★ *{fat_nutrient}* г жиров;
                    \n★ *{protein_nutrient}* г белков;
                    \n★ *{carbs_nutrient}* г углеводов{backslash}.
                    \n★ А также выпивать не меньше, чем *{water_quantity_str}* л чистой воды{backslash}!
                    \nИтого твой суммарный рацион за день составит *{target_calories}* калорий{backslash}.
                    \n{warning}
                    \nДля подсчета рациона тебе пригодятся соответствующие приложения и необходимо приобрести кухонные весы{backslash}. Подробнее про питание и тренировки узнаешь в *@fit{backslash}_o{backslash}_blog* 😎
                    \nУдачи{backslash}! Все получится ☺️
                    ''', parse_mode="MarkdownV2")
                    send_keyboard(msg)
                elif sex == 'Ж':
                    target_calories = round((1.375 * (10 * last_weight) + (6.25 * height) - (5 * age) + 5) - 350)
                    water_quantity = round((target_calories / 1000), 2)
                    fat_nutrient = round((0.45 * target_calories) / 9)
                    protein_nutrient = round((0.45 * target_calories) / 4)
                    carbs_nutrient = round((0.1 * target_calories) / 4)
                    last_weight_str = str(last_weight).replace('.', '\.')
                    water_quantity_str = str(water_quantity).replace('.', '\.')
                    bot.send_message(msg.chat.id, f'''
                    🤔 По моим данным твой текущий и последний записанный вес составляет *{last_weight_str}* кг{backslash}. Рост {backslash}= *{height}* cм{backslash}. Возраст {backslash}= *{age}*{backslash}. Пол {backslash}= *женский*{backslash}.
                    \nЕсли это не так {backslash}- тебе нужно обновить информацию, в соответствующих командах, иначе расчет будет некорректным 😔{backslash}.
                    \nДля достижения цели тебе следует придерживаться следующих ежесуточных пропорций в питании:
                    \n★ *{fat_nutrient}* г жиров;
                    \n★ *{protein_nutrient}* г белков;
                    \n★ *{carbs_nutrient}* г углеводов{backslash}.
                    \n★ А также выпивать не меньше, чем *{water_quantity_str}* л чистой воды{backslash}!
                    \nИтого твой суммарный рацион за день составит *{target_calories}* калорий{backslash}.
                    \n{warning}
                    \nДля подсчета рациона тебе пригодятся соответствующие приложения и необходимо приобрести кухонные весы{backslash}. Подробнее про питание и тренировки узнаешь в *@fit{backslash}_o{backslash}_blog* 😎
                    \nУдачи{backslash}! Все получится ☺️
                    ''', parse_mode="MarkdownV2")
                    send_keyboard(msg)
        elif msg.text == "Классика 🍝🍗🥙":
            if sex == 'М':
                target_calories = round(0.85 * (13.397 * last_weight + 88.362 + 4.799 * height - 5.677 * age))
                water_quantity = round(((target_calories / 1000) * 1), 2)
                fat_nutrient = round((0.35 * target_calories) / 9)
                protein_nutrient = round((0.25 * target_calories) / 4)
                carbs_nutrient = round((0.4 * target_calories) / 4)
                last_weight_str = str(last_weight).replace('.', '\.')
                water_quantity_str = str(water_quantity).replace('.', '\.')
                bot.send_message(msg.chat.id, f'''
                🤔 По моим данным твой текущий и последний записанный вес составляет *{last_weight_str}* кг{backslash}. Рост {backslash}= *{height}* cм{backslash}. Возраст {backslash}= *{age}*{backslash}. Пол {backslash}= *мужской*{backslash}.
                \nЕсли это не так {backslash}- тебе нужно обновить информацию, в соответствующих командах, иначе расчет будет некорректным 😔{backslash}.
                \nДля достижения цели тебе следует придерживаться следующих ежесуточных пропорций в питании:
                \n★ *{fat_nutrient}* г жиров;
                \n★ *{protein_nutrient}* г белков;
                \n★ *{carbs_nutrient}* г углеводов{backslash}.
                \n★ А также выпивать не меньше, чем *{water_quantity_str}* л чистой воды{backslash}!
                \nИтого твой суммарный рацион за день составит *{target_calories}* калорий{backslash}.
                \n{warning}
                \nДля подсчета рациона тебе пригодятся соответствующие приложения и необходимо приобрести кухонные весы{backslash}. Подробнее про питание и тренировки узнаешь в *@fit{backslash}_o{backslash}_blog* 😎
                \nУдачи{backslash}! Все получится ☺️
                ''', parse_mode="MarkdownV2")
                send_keyboard(msg)
            elif sex == 'Ж':
                target_calories = round(0.85 * (9.247 * last_weight + 447.593 + 3.098 * height - 4.33 * age))
                water_quantity = round(((target_calories / 1000) * 1), 2)
                fat_nutrient = round((0.35 * target_calories) / 9)
                protein_nutrient = round((0.25 * target_calories) / 4)
                carbs_nutrient = round((0.4 * target_calories) / 4)
                last_weight_str = str(last_weight).replace('.', '\.')
                water_quantity_str = str(water_quantity).replace('.', '\.')
                bot.send_message(msg.chat.id, f'''
                🤔 По моим данным твой текущий и последний записанный вес составляет *{last_weight_str}* кг{backslash}. Рост {backslash}= *{height}* cм{backslash}. Возраст {backslash}= *{age}*{backslash}. Пол {backslash}= *женский*{backslash}.
                \nЕсли это не так {backslash}- тебе нужно обновить информацию, в соответствующих командах, иначе расчет будет некорректным 😔{backslash}.
                \nДля достижения цели тебе следует придерживаться следующих ежесуточных пропорций в питании:
                \n★ *{fat_nutrient}* г жиров;
                \n★ *{protein_nutrient}* г белков;
                \n★ *{carbs_nutrient}* г углеводов{backslash}.
                \n★ А также выпивать не меньше, чем *{water_quantity_str}* л чистой воды{backslash}!
                \nИтого твой суммарный рацион за день составит *{target_calories}* калорий{backslash}.
                \n{warning}
                \nДля подсчета рациона тебе пригодятся соответствующие приложения и необходимо приобрести кухонные весы{backslash}. Подробнее про питание и тренировки узнаешь в *@fit{backslash}_o{backslash}_blog* 😎
                \nУдачи{backslash}! Все получится ☺️
                ''', parse_mode="MarkdownV2")
                send_keyboard(msg)
    except Exception as e:
        bot.send_message(msg.chat.id, '''
        Кажется, мне не достает данных, проверь был ли введен вес и первичные данные, которые вводились на старте 😉
        ''')
        send_keyboard(msg)

def high_activity_decrease(msg):
    try:
        if msg.text == "Низкоуглеводка 🍤🥜🥩":
            with psycopg2.connect(db_URL, sslmode="require") as postgre_con:
                db_obj = postgre_con.cursor()
                db_obj.execute(f'''
                SELECT weight
                FROM
                    (
                    SELECT weight, to_date(date, 'DD/MM/YYYY') as date_form
                    FROM bot_users_weights_table
                    WHERE "user_id"={msg.from_user.id}
                    ORDER BY date_form
                    DESC LIMIT 1) 
                    AS last_weight''')
                last_weight = float(pretiffy(db_obj.fetchall()))
                db_obj.execute(f'SELECT sex FROM bot_users_list WHERE "user_id"={msg.from_user.id} ORDER BY ID DESC LIMIT 1')
                sex = pretiffy(db_obj.fetchall())
                db_obj.execute(f'SELECT age FROM bot_users_list WHERE "user_id"={msg.from_user.id} ORDER BY ID DESC LIMIT 1')
                age = int(pretiffy(db_obj.fetchall()))
                db_obj.execute(f'SELECT height FROM bot_users_list WHERE "user_id"={msg.from_user.id} ORDER BY ID DESC LIMIT 1')
                height = int(pretiffy(db_obj.fetchall()))
                postgre_con.commit()
                db_obj.close()
                if sex == 'М':
                    target_calories = round((1.5 * (10 * last_weight) + (6.25 * height) - (5 * age) + 5) - 200)
                    water_quantity = round((target_calories / 1000), 2)
                    fat_nutrient = round((0.45 * target_calories) / 9)
                    protein_nutrient = round((0.45 * target_calories) / 4)
                    carbs_nutrient = round((0.1 * target_calories) / 4)
                    last_weight_str = str(last_weight).replace('.', '\.')
                    water_quantity_str = str(water_quantity).replace('.', '\.')
                    bot.send_message(msg.chat.id, f'''
                    🤔 По моим данным твой текущий вес составляет *{last_weight_str}* кг{backslash}. Рост {backslash}= *{height}* cм{backslash}. Возраст {backslash}= *{age}*{backslash}. Пол {backslash}= *мужской*{backslash}.
                    \nЕсли это не так {backslash}- тебе нужно обновить информацию, в соответствующих командах, иначе расчет будет некорректным 😔{backslash}.
                    \nДля достижения цели тебе следует придерживаться следующих ежесуточных пропорций в питании:
                    \n★ *{fat_nutrient}* г жиров;
                    \n★ *{protein_nutrient}* г белков;
                    \n★ *{carbs_nutrient}* г углеводов{backslash}.
                    \n★ А также выпивать не меньше, чем *{water_quantity_str}* л чистой воды{backslash}!
                    \nИтого твой суммарный рацион за день составит *{target_calories}* калорий{backslash}.
                    \n{warning}
                    \nДля подсчета рациона тебе пригодятся соответствующие приложения и необходимо приобрести кухонные весы{backslash}. Подробнее про питание и тренировки узнаешь в *@fit{backslash}_o{backslash}_blog* 😎
                    \nУдачи{backslash}! Все получится ☺️
                    ''', parse_mode="MarkdownV2")
                    send_keyboard(msg)
                elif sex == 'Ж':
                    target_calories = round((1.5 * (10 * last_weight) + (6.25 * height) - (5 * age) + 5) - 350)
                    water_quantity = round((target_calories / 1000), 2)
                    fat_nutrient = round((0.45 * target_calories) / 9)
                    protein_nutrient = round((0.45 * target_calories) / 4)
                    carbs_nutrient = round((0.1 * target_calories) / 4)
                    last_weight_str = str(last_weight).replace('.', '\.')
                    water_quantity_str = str(water_quantity).replace('.', '\.')
                    bot.send_message(msg.chat.id, f'''
                    🤔 По моим данным твой текущий и последний записанный вес составляет *{last_weight_str}* кг{backslash}. Рост {backslash}= *{height}* cм{backslash}. Возраст {backslash}= *{age}*{backslash}. Пол {backslash}= *женский*{backslash}.
                    \nЕсли это не так {backslash}- тебе нужно обновить информацию, в соответствующих командах, иначе расчет будет некорректным 😔{backslash}.
                    \nДля достижения цели тебе следует придерживаться следующих ежесуточных пропорций в питании:
                    \n★ *{fat_nutrient}* г жиров;
                    \n★ *{protein_nutrient}* г белков;
                    \n★ *{carbs_nutrient}* г углеводов{backslash}.
                    \n★ А также выпивать не меньше, чем *{water_quantity_str}* л чистой воды{backslash}!
                    \nИтого твой суммарный рацион за день составит *{target_calories}* калорий{backslash}.
                    \n{warning}
                    \nДля подсчета рациона тебе пригодятся соответствующие приложения и необходимо приобрести кухонные весы{backslash}. Подробнее про питание и тренировки узнаешь в *@fit{backslash}_o{backslash}_blog* 😎
                    \nУдачи{backslash}! Все получится ☺️
                    ''', parse_mode="MarkdownV2")
                    send_keyboard(msg)
        elif msg.text == "Классика 🍝🍗🥙":
            with psycopg2.connect(db_URL, sslmode="require") as postgre_con:
                db_obj = postgre_con.cursor()
                db_obj.execute(f'''
                SELECT weight
                FROM
                    (
                    SELECT weight, to_date(date, 'DD/MM/YYYY') as date_form
                    FROM bot_users_weights_table
                    WHERE "user_id"={msg.from_user.id}
                    ORDER BY date_form
                    DESC LIMIT 1) 
                    AS last_weight''')
                last_weight = float(pretiffy(db_obj.fetchall()))
                db_obj.execute(f'SELECT sex FROM bot_users_list WHERE "user_id"={msg.from_user.id} ORDER BY ID DESC LIMIT 1')
                sex = pretiffy(db_obj.fetchall())
                db_obj.execute(f'SELECT age FROM bot_users_list WHERE "user_id"={msg.from_user.id} ORDER BY ID DESC LIMIT 1')
                age = int(pretiffy(db_obj.fetchall()))
                db_obj.execute(f'SELECT height FROM bot_users_list WHERE "user_id"={msg.from_user.id} ORDER BY ID DESC LIMIT 1')
                height = int(pretiffy(db_obj.fetchall()))
                postgre_con.commit()
                db_obj.close()
                if sex == 'М':
                    target_calories = round(0.9 * (13.397 * last_weight + 88.362 + 4.799 * height - 5.677 * age))
                    water_quantity = round(((target_calories/ 1000) * 1),2)
                    fat_nutrient = round((0.35 * target_calories) / 9)
                    protein_nutrient = round((0.25 * target_calories) / 4)
                    carbs_nutrient = round((0.4 * target_calories) / 4)
                    last_weight_str = str(last_weight).replace('.', '\.')
                    water_quantity_str = str(water_quantity).replace('.', '\.')
                    bot.send_message(msg.chat.id, f'''
                    🤔 По моим данным твой текущий и последний записанный вес составляет *{last_weight_str}* кг{backslash}. Рост {backslash}= *{height}* cм{backslash}. Возраст {backslash}= *{age}*{backslash}. Пол {backslash}= *мужской*{backslash}.
                    \nЕсли это не так {backslash}- тебе нужно обновить информацию, в соответствующих командах, иначе расчет будет некорректным 😔{backslash}.
                    \nДля достижения цели тебе следует придерживаться следующих ежесуточных пропорций в питании:
                    \n★ *{fat_nutrient}* г жиров;
                    \n★ *{protein_nutrient}* г белков;
                    \n★ *{carbs_nutrient}* г углеводов{backslash}.
                    \n★ А также выпивать не меньше, чем *{water_quantity_str}* л чистой воды{backslash}!
                    \nИтого твой суммарный рацион за день составит *{target_calories}* калорий{backslash}.
                    \n{warning}
                    \nДля подсчета рациона тебе пригодятся соответствующие приложения и необходимо приобрести кухонные весы{backslash}. Подробнее про питание и тренировки узнаешь в *@fit{backslash}_o{backslash}_blog* 😎
                    \nУдачи{backslash}! Все получится ☺️
                    ''', parse_mode="MarkdownV2")
                    send_keyboard(msg)
                elif sex == 'Ж':
                    target_calories = round(0.9 * (9.247 * last_weight + 447.593 + 3.098 * height - 4.33 * age))
                    water_quantity = round(((target_calories / 1000) * 1), 2)
                    fat_nutrient = round((0.35 * target_calories) / 9)
                    protein_nutrient = round((0.25 * target_calories) / 4)
                    carbs_nutrient = round((0.4 * target_calories) / 4)
                    last_weight_str = str(last_weight).replace('.', '\.')
                    water_quantity_str = str(water_quantity).replace('.', '\.')
                    bot.send_message(msg.chat.id, f'''
                    🤔 По моим данным твой текущий и последний записанный вес составляет *{last_weight_str}* кг{backslash}. Рост {backslash}= *{height}* cм{backslash}. Возраст {backslash}= *{age}*{backslash}. Пол {backslash}= *женский*{backslash}.
                    \nЕсли это не так {backslash}- тебе нужно обновить информацию, в соответствующих командах, иначе расчет будет некорректным 😔{backslash}.
                    \nДля достижения цели тебе следует придерживаться следующих ежесуточных пропорций в питании:
                    \n★ *{fat_nutrient}* г жиров;
                    \n★ *{protein_nutrient}* г белков;
                    \n★ *{carbs_nutrient}* г углеводов{backslash}.
                    \n★ А также выпивать не меньше, чем *{water_quantity_str}* л чистой воды{backslash}!
                    \nИтого твой суммарный рацион за день составит *{target_calories}* калорий{backslash}.
                    \n{warning}
                    \nДля подсчета рациона тебе пригодятся соответствующие приложения и необходимо приобрести кухонные весы{backslash}. Подробнее про питание и тренировки узнаешь в *@fit{backslash}_o{backslash}_blog* 😎
                    \nУдачи{backslash}! Все получится ☺️
                    ''', parse_mode="MarkdownV2")
                    send_keyboard(msg)
    except Exception as e:
        bot.send_message(msg.chat.id, '''
        Кажется, мне не достает данных, проверь был ли введен вес и первичные данные, которые я спрашивал на старте 😉
        ''')
        send_keyboard(msg)

def pretiffy(last_val):
    for val in last_val:
        last_v = val[0]
        return last_v

def increase_weight(msg):
    try:
        if msg.text == "Низкая активность 🐌":
            bot.send_message(msg.chat.id, '''
            Я даже боюсь представить, какая у тебя цель набора при малоактивном образе жизни 😱! Но это точно не в рамках моих компетенций 😂
            ''')
            send_keyboard(msg)
        elif msg.text == "Средняя активность 🏄‍♀️🏄‍♂️":
            with psycopg2.connect(db_URL, sslmode="require") as postgre_con:
                db_obj = postgre_con.cursor()
                db_obj.execute(f'''
                SELECT weight
                FROM
                    (
                    SELECT weight, to_date(date, 'DD/MM/YYYY') as date_form
                    FROM bot_users_weights_table
                    WHERE "user_id"={msg.from_user.id}
                    ORDER BY date_form
                    DESC LIMIT 1) 
                    AS last_weight''')
                last_weight = float(pretiffy(db_obj.fetchall()))
                db_obj.execute(f'SELECT sex FROM bot_users_list WHERE "user_id"={msg.from_user.id} ORDER BY ID DESC LIMIT 1')
                sex = pretiffy(db_obj.fetchall())
                db_obj.execute(f'SELECT age FROM bot_users_list WHERE "user_id"={msg.from_user.id} ORDER BY ID DESC LIMIT 1')
                age = int(pretiffy(db_obj.fetchall()))
                db_obj.execute(f'SELECT height FROM bot_users_list WHERE "user_id"={msg.from_user.id} ORDER BY ID DESC LIMIT 1')
                height = int(pretiffy(db_obj.fetchall()))
                postgre_con.commit()
                db_obj.close()
                if sex == 'М':
                    target_calories = round(1.2 * (13.397 * last_weight + 88.362 + 4.799 * height - 5.677 * age))
                    water_quantity = round(((target_calories/ 1000) * 1),2)
                    fat_nutrient = round((0.35 * target_calories) / 9)
                    protein_nutrient = round((0.25 * target_calories) / 4)
                    carbs_nutrient = round((0.4 * target_calories) / 4)
                    last_weight_str = str(last_weight).replace('.', '\.')
                    water_quantity_str = str(water_quantity).replace('.', '\.')
                    bot.send_message(msg.chat.id, f'''
                    🤔 По моим данным твой текущий и последний записанный вес составляет *{last_weight_str}* кг{backslash}. Рост {backslash}= *{height}* cм{backslash}. Возраст {backslash}= *{age}*{backslash}. Пол {backslash}= *мужской*{backslash}.
                    \nЕсли это не так {backslash}- тебе нужно обновить информацию, в соответствующих командах, иначе расчет будет некорректным 😔{backslash}.
                    \nДля достижения цели тебе следует придерживаться следующих ежесуточных пропорций в питании:
                    \n★ *{fat_nutrient}* г жиров;
                    \n★ *{protein_nutrient}* г белков;
                    \n★ *{carbs_nutrient}* г углеводов{backslash}.
                    \n★ А также выпивать не меньше, чем *{water_quantity_str}* л чистой воды{backslash}!
                    \nИтого твой суммарный рацион за день составит *{target_calories}* калорий{backslash}.
                    \n{warning}
                    \nДля подсчета рациона тебе пригодятся соответствующие приложения и необходимо приобрести кухонные весы{backslash}. Подробнее про питание и тренировки узнаешь в *@fit{backslash}_o{backslash}_blog* 😎
                    \nУдачи{backslash}! Все получится ☺️
                    ''', parse_mode="MarkdownV2")
                    send_keyboard(msg)
                elif sex == 'Ж':
                    target_calories = round(1.2 * (9.247 * last_weight + 447.593 + 3.098 * height - 4.33 * age))
                    water_quantity = round(((target_calories / 1000) * 1), 2)
                    fat_nutrient = round((0.35 * target_calories) / 9)
                    protein_nutrient = round((0.25 * target_calories) / 4)
                    carbs_nutrient = round((0.4 * target_calories) / 4)
                    last_weight_str = str(last_weight).replace('.', '\.')
                    water_quantity_str = str(water_quantity).replace('.', '\.')
                    bot.send_message(msg.chat.id, f'''
                    🤔 По моим данным твой текущий и последний записанный вес составляет *{last_weight_str}* кг{backslash}. Рост {backslash}= *{height}* cм{backslash}. Возраст {backslash}= *{age}*{backslash}. Пол {backslash}= *женский*{backslash}.
                    \nЕсли это не так {backslash}- тебе нужно обновить информацию, в соответствующих командах, иначе расчет будет некорректным 😔{backslash}.
                    \nДля достижения цели тебе следует придерживаться следующих ежесуточных пропорций в питании:
                    \n★ *{fat_nutrient}* г жиров;
                    \n★ *{protein_nutrient}* г белков;
                    \n★ *{carbs_nutrient}* г углеводов{backslash}.
                    \n★ А также выпивать не меньше, чем *{water_quantity_str}* л чистой воды{backslash}!
                    \nИтого твой суммарный рацион за день составит *{target_calories}* калорий{backslash}.
                    \n{warning}
                    \nДля подсчета рациона тебе пригодятся соответствующие приложения и необходимо приобрести кухонные весы{backslash}. Подробнее про питание и тренировки узнаешь в *@fit{backslash}_o{backslash}_blog* 😎
                    \nУдачи{backslash}! Все получится ☺️
                    ''', parse_mode="MarkdownV2")
                    send_keyboard(msg)
        elif msg.text == "Высокая активность 🏋️ 🔥 🏋️":
            with psycopg2.connect(db_URL, sslmode="require") as postgre_con:
                db_obj = postgre_con.cursor()
                db_obj.execute(f'''
                SELECT weight
                FROM
                    (
                    SELECT weight, to_date(date, 'DD/MM/YYYY') as date_form
                    FROM bot_users_weights_table
                    WHERE "user_id"={msg.from_user.id}
                    ORDER BY date_form
                    DESC LIMIT 1) 
                    AS last_weight''')
                last_weight = float(pretiffy(db_obj.fetchall()))
                db_obj.execute(f'SELECT sex FROM bot_users_list WHERE "user_id"={msg.from_user.id} ORDER BY ID DESC LIMIT 1')
                sex = pretiffy(db_obj.fetchall())
                db_obj.execute(f'SELECT age FROM bot_users_list WHERE "user_id"={msg.from_user.id} ORDER BY ID DESC LIMIT 1')
                age = int(pretiffy(db_obj.fetchall()))
                db_obj.execute(f'SELECT height FROM bot_users_list WHERE "user_id"={msg.from_user.id} ORDER BY ID DESC LIMIT 1')
                height = int(pretiffy(db_obj.fetchall()))
                postgre_con.commit()
                db_obj.close()
                if sex == 'М':
                    target_calories = round(1.4 * (13.397 * last_weight + 88.362 + 4.799 * height - 5.677 * age))
                    water_quantity = round(((target_calories/ 1000) * 1),2)
                    fat_nutrient = round((0.3 * target_calories) / 9)
                    protein_nutrient = round((0.3 * target_calories) / 4)
                    carbs_nutrient = round((0.4 * target_calories) / 4)
                    last_weight_str = str(last_weight).replace('.', '\.')
                    water_quantity_str = str(water_quantity).replace('.', '\.')
                    bot.send_message(msg.chat.id, f'''
                    🤔 По моим данным твой текущий и последний записанный вес составляет *{last_weight_str}* кг{backslash}. Рост {backslash}= *{height}* cм{backslash}. Возраст {backslash}= *{age}*{backslash}. Пол {backslash}= *мужской*{backslash}.
                    \nЕсли это не так {backslash}- тебе нужно обновить информацию, в соответствующих командах, иначе расчет будет некорректным 😔{backslash}.
                    \nДля достижения цели тебе следует придерживаться следующих ежесуточных пропорций в питании:
                    \n★ *{fat_nutrient}* г жиров;
                    \n★ *{protein_nutrient}* г белков;
                    \n★ *{carbs_nutrient}* г углеводов{backslash}.
                    \n★ А также выпивать не меньше, чем *{water_quantity_str}* л чистой воды{backslash}!
                    \nИтого твой суммарный рацион за день составит *{target_calories}* калорий{backslash}.
                    \n{warning}
                    \nДля подсчета рациона тебе пригодятся соответствующие приложения и необходимо приобрести кухонные весы{backslash}. Подробнее про питание и тренировки узнаешь в *@fit{backslash}_o{backslash}_blog* 😎
                    \nУдачи{backslash}! Все получится ☺️
                    ''', parse_mode="MarkdownV2")
                    cursor.close()
                    send_keyboard(msg)
                elif sex == 'Ж':
                    target_calories = round(1.4 * (9.247 * last_weight + 447.593 + 3.098 * height - 4.33 * age))
                    water_quantity = round(((target_calories / 1000) * 1), 2)
                    fat_nutrient = round((0.3 * target_calories) / 9)
                    protein_nutrient = round((0.3 * target_calories) / 4)
                    carbs_nutrient = round((0.4 * target_calories) / 4)
                    last_weight_str = str(last_weight).replace('.', '\.')
                    water_quantity_str = str(water_quantity).replace('.', '\.')
                    bot.send_message(msg.chat.id, f'''
                    🤔 По моим данным твой текущий и последний записанный вес составляет *{last_weight_str}* кг{backslash}. Рост {backslash}= *{height}* cм{backslash}. Возраст {backslash}= *{age}*{backslash}. Пол {backslash}= *женский*{backslash}.
                    \nЕсли это не так {backslash}- тебе нужно обновить информацию, в соответствующих командах, иначе расчет будет некорректным 😔{backslash}.
                    \nДля достижения цели тебе следует придерживаться следующих ежесуточных пропорций в питании:
                    \n★ *{fat_nutrient}* г жиров;
                    \n★ *{protein_nutrient}* г белков;
                    \n★ *{carbs_nutrient}* г углеводов{backslash}.
                    \n★ А также выпивать не меньше, чем *{water_quantity_str}* л чистой воды{backslash}!
                    \nИтого твой суммарный рацион за день составит *{target_calories}* калорий{backslash}.
                    \n{warning}
                    \nДля подсчета рациона тебе пригодятся соответствующие приложения и необходимо приобрести кухонные весы{backslash}. Подробнее про питание и тренировки узнаешь в *@fit{backslash}_o{backslash}_blog* 😎
                    \nУдачи{backslash}! Все получится ☺️
                    ''', parse_mode="MarkdownV2")
                    cursor.close()
                    send_keyboard(msg)
    except Exception as e:
        bot.send_message(msg.chat.id, '''
        Кажется, мне не достает данных, проверь был ли введен вес и первичные данные, которые вводились на старте 😉
        ''')
        send_keyboard(msg)

# def decrease_weight(msg):
#     try:
#         if msg.text == "Низкая активность 🐌":
#             with psycopg2.connect(db_URL, sslmode="require") as postgre_con:
#                 db_obj = postgre_con.cursor()
#                 db_obj.execute(f'''
#                 SELECT weight
#                 FROM
#                     (
#                     SELECT weight, to_date(date, 'DD/MM/YYYY') as date_form
#                     FROM bot_users_weights_table
#                     WHERE "user_id"={msg.from_user.id}
#                     ORDER BY date_form
#                     DESC LIMIT 1)
#                     AS last_weight''')
#                 last_weight = float(pretiffy(db_obj.fetchall()))
#                 db_obj.execute(f'SELECT sex FROM bot_users_list WHERE "user_id"={msg.from_user.id} ORDER BY ID DESC LIMIT 1')
#                 sex = pretiffy(db_obj.fetchall())
#                 db_obj.execute(f'SELECT age FROM bot_users_list WHERE "user_id"={msg.from_user.id} ORDER BY ID DESC LIMIT 1')
#                 age = int(pretiffy(db_obj.fetchall()))
#                 db_obj.execute(f'SELECT height FROM bot_users_list WHERE "user_id"={msg.from_user.id} ORDER BY ID DESC LIMIT 1')
#                 height = int(pretiffy(db_obj.fetchall()))
#                 postgre_con.commit()
#                 db_obj.close()
#                 if sex == 'М':
#                     target_calories = round(0.8 * (13.397 * last_weight + 88.362 + 4.799 * height - 5.677 * age))
#                     water_quantity = round(((target_calories/ 1000) * 1),2)
#                     fat_nutrient = round((0.35 * target_calories) / 9)
#                     protein_nutrient = round((0.25 * target_calories) / 4)
#                     carbs_nutrient = round((0.4 * target_calories) / 4)
#                     last_weight_str = str(last_weight).replace('.', '\.')
#                     water_quantity_str = str(water_quantity).replace('.', '\.')
#                     bot.send_message(msg.chat.id, f'''
#                     🤔 По моим данным твой текущий и последний записанный вес составляет *{last_weight_str}* кг{backslash}. Рост {backslash}= *{height}* cм{backslash}. Возраст {backslash}= *{age}*{backslash}. Пол {backslash}= *мужской*{backslash}.
#                     \nЕсли это не так {backslash}- тебе нужно обновить информацию, в соответствующих командах, иначе расчет будет некорректным 😔{backslash}.
#                     \nДля достижения цели тебе следует придерживаться следующих ежесуточных пропорций в питании:
#                     \n★ *{fat_nutrient}* г жиров;
#                     \n★ *{protein_nutrient}* г белков;
#                     \n★ *{carbs_nutrient}* г углеводов{backslash}.
#                     \n★ А также выпивать не меньше, чем *{water_quantity_str}* л чистой воды{backslash}!
#                     \nИтого твой суммарный рацион за день составит *{target_calories}* калорий{backslash}.
#                     \n{warning}
#                     \nДля подсчета рациона тебе пригодятся соответствующие приложения и необходимо приобрести кухонные весы{backslash}. Подробнее про питание и тренировки узнаешь в *@fit{backslash}_o{backslash}_blog* 😎
#                     \nУдачи{backslash}! Все получится ☺️
#                     ''', parse_mode="MarkdownV2")
#                     send_keyboard(msg)
#                 elif sex == 'Ж':
#                     target_calories = round(0.8 * (9.247 * last_weight + 447.593 + 3.098 * height - 4.33 * age))
#                     water_quantity = round(((target_calories / 1000) * 1), 2)
#                     fat_nutrient = round((0.35 * target_calories) / 9)
#                     protein_nutrient = round((0.25 * target_calories) / 4)
#                     carbs_nutrient = round((0.4 * target_calories) / 4)
#                     last_weight_str = str(last_weight).replace('.', '\.')
#                     water_quantity_str = str(water_quantity).replace('.', '\.')
#                     bot.send_message(msg.chat.id, f'''
#                     🤔 По моим данным твой текущий и последний записанный вес составляет *{last_weight_str}* кг{backslash}. Рост {backslash}= *{height}* cм{backslash}. Возраст {backslash}= *{age}*{backslash}. Пол {backslash}= *женский*{backslash}.
#                     \nЕсли это не так {backslash}- тебе нужно обновить информацию, в соответствующих командах, иначе расчет будет некорректным 😔{backslash}.
#                     \nДля достижения цели тебе следует придерживаться следующих ежесуточных пропорций в питании:
#                     \n★ *{fat_nutrient}* г жиров;
#                     \n★ *{protein_nutrient}* г белков;
#                     \n★ *{carbs_nutrient}* г углеводов{backslash}.
#                     \n★ А также выпивать не меньше, чем *{water_quantity_str}* л чистой воды{backslash}!
#                     \nИтого твой суммарный рацион за день составит *{target_calories}* калорий{backslash}.
#                     \n{warning}
#                     \nДля подсчета рациона тебе пригодятся соответствующие приложения и необходимо приобрести кухонные весы{backslash}. Подробнее про питание и тренировки узнаешь в *@fit{backslash}_o{backslash}_blog* 😎
#                     \nУдачи{backslash}! Все получится ☺️
#                     ''', parse_mode="MarkdownV2")
#                     send_keyboard(msg)
#         elif msg.text == "Средняя активность 🏄‍♀️🏄‍♂️":
#             with psycopg2.connect(db_URL, sslmode="require") as postgre_con:
#                 db_obj = postgre_con.cursor()
#                 db_obj.execute(f'''
#                 SELECT weight
#                 FROM
#                     (
#                     SELECT weight, to_date(date, 'DD/MM/YYYY') as date_form
#                     FROM bot_users_weights_table
#                     WHERE "user_id"={msg.from_user.id}
#                     ORDER BY date_form
#                     DESC LIMIT 1)
#                     AS last_weight''')
#                 last_weight = float(pretiffy(db_obj.fetchall()))
#                 db_obj.execute(f'SELECT sex FROM bot_users_list WHERE "user_id"={msg.from_user.id} ORDER BY ID DESC LIMIT 1')
#                 sex = pretiffy(db_obj.fetchall())
#                 db_obj.execute(f'SELECT age FROM bot_users_list WHERE "user_id"={msg.from_user.id} ORDER BY ID DESC LIMIT 1')
#                 age = int(pretiffy(db_obj.fetchall()))
#                 db_obj.execute(f'SELECT height FROM bot_users_list WHERE "user_id"={msg.from_user.id} ORDER BY ID DESC LIMIT 1')
#                 height = int(pretiffy(db_obj.fetchall()))
#                 postgre_con.commit()
#                 db_obj.close()
#                 if sex == 'М':
#                     target_calories = round(0.85 * (13.397 * last_weight + 88.362 + 4.799 * height - 5.677 * age))
#                     water_quantity = round(((target_calories/ 1000) * 1),2)
#                     fat_nutrient = round((0.35 * target_calories) / 9)
#                     protein_nutrient = round((0.25 * target_calories) / 4)
#                     carbs_nutrient = round((0.4 * target_calories) / 4)
#                     last_weight_str = str(last_weight).replace('.', '\.')
#                     water_quantity_str = str(water_quantity).replace('.', '\.')
#                     bot.send_message(msg.chat.id, f'''
#                     🤔 По моим данным твой текущий и последний записанный вес составляет *{last_weight_str}* кг{backslash}. Рост {backslash}= *{height}* cм{backslash}. Возраст {backslash}= *{age}*{backslash}. Пол {backslash}= *мужской*{backslash}.
#                     \nЕсли это не так {backslash}- тебе нужно обновить информацию, в соответствующих командах, иначе расчет будет некорректным 😔{backslash}.
#                     \nДля достижения цели тебе следует придерживаться следующих ежесуточных пропорций в питании:
#                     \n★ *{fat_nutrient}* г жиров;
#                     \n★ *{protein_nutrient}* г белков;
#                     \n★ *{carbs_nutrient}* г углеводов{backslash}.
#                     \n★ А также выпивать не меньше, чем *{water_quantity_str}* л чистой воды{backslash}!
#                     \nИтого твой суммарный рацион за день составит *{target_calories}* калорий{backslash}.
#                     \n{warning}
#                     \nДля подсчета рациона тебе пригодятся соответствующие приложения и необходимо приобрести кухонные весы{backslash}. Подробнее про питание и тренировки узнаешь в *@fit{backslash}_o{backslash}_blog* 😎
#                     \nУдачи{backslash}! Все получится ☺️
#                     ''', parse_mode="MarkdownV2")
#                     send_keyboard(msg)
#                 elif sex == 'Ж':
#                     target_calories = round(0.85 * (9.247 * last_weight + 447.593 + 3.098 * height - 4.33 * age))
#                     water_quantity = round(((target_calories / 1000) * 1), 2)
#                     fat_nutrient = round((0.35 * target_calories) / 9)
#                     protein_nutrient = round((0.25 * target_calories) / 4)
#                     carbs_nutrient = round((0.4 * target_calories) / 4)
#                     last_weight_str = str(last_weight).replace('.', '\.')
#                     water_quantity_str = str(water_quantity).replace('.', '\.')
#                     bot.send_message(msg.chat.id, f'''
#                     🤔 По моим данным твой текущий и последний записанный вес составляет *{last_weight_str}* кг{backslash}. Рост {backslash}= *{height}* cм{backslash}. Возраст {backslash}= *{age}*{backslash}. Пол {backslash}= *женский*{backslash}.
#                     \nЕсли это не так {backslash}- тебе нужно обновить информацию, в соответствующих командах, иначе расчет будет некорректным 😔{backslash}.
#                     \nДля достижения цели тебе следует придерживаться следующих ежесуточных пропорций в питании:
#                     \n★ *{fat_nutrient}* г жиров;
#                     \n★ *{protein_nutrient}* г белков;
#                     \n★ *{carbs_nutrient}* г углеводов{backslash}.
#                     \n★ А также выпивать не меньше, чем *{water_quantity_str}* л чистой воды{backslash}!
#                     \nИтого твой суммарный рацион за день составит *{target_calories}* калорий{backslash}.
#                     \n{warning}
#                     \nДля подсчета рациона тебе пригодятся соответствующие приложения и необходимо приобрести кухонные весы{backslash}. Подробнее про питание и тренировки узнаешь в *@fit{backslash}_o{backslash}_blog* 😎
#                     \nУдачи{backslash}! Все получится ☺️
#                     ''', parse_mode="MarkdownV2")
#                     send_keyboard(msg)
#         elif msg.text == "Высокая активность 🏋️ 🔥 🏋️":
#             with psycopg2.connect(db_URL, sslmode="require") as postgre_con:
#                 db_obj = postgre_con.cursor()
#                 db_obj.execute(f'''
#                 SELECT weight
#                 FROM
#                     (
#                     SELECT weight, to_date(date, 'DD/MM/YYYY') as date_form
#                     FROM bot_users_weights_table
#                     WHERE "user_id"={msg.from_user.id}
#                     ORDER BY date_form
#                     DESC LIMIT 1)
#                     AS last_weight''')
#                 last_weight = float(pretiffy(db_obj.fetchall()))
#                 db_obj.execute(f'SELECT sex FROM bot_users_list WHERE "user_id"={msg.from_user.id} ORDER BY ID DESC LIMIT 1')
#                 sex = pretiffy(db_obj.fetchall())
#                 db_obj.execute(f'SELECT age FROM bot_users_list WHERE "user_id"={msg.from_user.id} ORDER BY ID DESC LIMIT 1')
#                 age = int(pretiffy(db_obj.fetchall()))
#                 db_obj.execute(f'SELECT height FROM bot_users_list WHERE "user_id"={msg.from_user.id} ORDER BY ID DESC LIMIT 1')
#                 height = int(pretiffy(db_obj.fetchall()))
#                 postgre_con.commit()
#                 db_obj.close()
#                 if sex == 'М':
#                     target_calories = round(0.9 * (13.397 * last_weight + 88.362 + 4.799 * height - 5.677 * age))
#                     water_quantity = round(((target_calories/ 1000) * 1),2)
#                     fat_nutrient = round((0.35 * target_calories) / 9)
#                     protein_nutrient = round((0.4 * target_calories) / 4)
#                     carbs_nutrient = round((0.25 * target_calories) / 4)
#                     last_weight_str = str(last_weight).replace('.', '\.')
#                     water_quantity_str = str(water_quantity).replace('.', '\.')
#                     bot.send_message(msg.chat.id, f'''
#                     🤔 По моим данным твой текущий и последний записанный вес составляет *{last_weight_str}* кг{backslash}. Рост {backslash}= *{height}* cм{backslash}. Возраст {backslash}= *{age}*{backslash}. Пол {backslash}= *мужской*{backslash}.
#                     \nЕсли это не так {backslash}- тебе нужно обновить информацию, в соответствующих командах, иначе расчет будет некорректным 😔{backslash}.
#                     \nДля достижения цели тебе следует придерживаться следующих ежесуточных пропорций в питании:
#                     \n★ *{fat_nutrient}* г жиров;
#                     \n★ *{protein_nutrient}* г белков;
#                     \n★ *{carbs_nutrient}* г углеводов{backslash}.
#                     \n★ А также выпивать не меньше, чем *{water_quantity_str}* л чистой воды{backslash}!
#                     \nИтого твой суммарный рацион за день составит *{target_calories}* калорий{backslash}.
#                     \n{warning}
#                     \nДля подсчета рациона тебе пригодятся соответствующие приложения и необходимо приобрести кухонные весы{backslash}. Подробнее про питание и тренировки узнаешь в *@fit{backslash}_o{backslash}_blog* 😎
#                     \nУдачи{backslash}! Все получится ☺️
#                     ''', parse_mode="MarkdownV2")
#                     send_keyboard(msg)
#                 elif sex == 'Ж':
#                     target_calories = round(0.9 * (9.247 * last_weight + 447.593 + 3.098 * height - 4.33 * age))
#                     water_quantity = round(((target_calories / 1000) * 1), 2)
#                     fat_nutrient = round((0.35 * target_calories) / 9)
#                     protein_nutrient = round((0.4 * target_calories) / 4)
#                     carbs_nutrient = round((0.25 * target_calories) / 4)
#                     last_weight_str = str(last_weight).replace('.', '\.')
#                     water_quantity_str = str(water_quantity).replace('.', '\.')
#                     bot.send_message(msg.chat.id, f'''
#                     🤔 По моим данным твой текущий и последний записанный вес составляет *{last_weight_str}* кг{backslash}. Рост {backslash}= *{height}* cм{backslash}. Возраст {backslash}= *{age}*{backslash}. Пол {backslash}= *женский*{backslash}.
#                     \nЕсли это не так {backslash}- тебе нужно обновить информацию, в соответствующих командах, иначе расчет будет некорректным 😔{backslash}.
#                     \nДля достижения цели тебе следует придерживаться следующих ежесуточных пропорций в питании:
#                     \n★ *{fat_nutrient}* г жиров;
#                     \n★ *{protein_nutrient}* г белков;
#                     \n★ *{carbs_nutrient}* г углеводов{backslash}.
#                     \n★ А также выпивать не меньше, чем *{water_quantity_str}* л чистой воды{backslash}!
#                     \nИтого твой суммарный рацион за день составит *{target_calories}* калорий{backslash}.
#                     \n{warning}
#                     \nДля подсчета рациона тебе пригодятся соответствующие приложения и необходимо приобрести кухонные весы{backslash}. Подробнее про питание и тренировки узнаешь в *@fit{backslash}_o{backslash}_blog* 😎
#                     \nУдачи{backslash}! Все получится ☺️
#                     ''', parse_mode="MarkdownV2")
#                     send_keyboard(msg)
#     except Exception as e:
#         bot.send_message(msg.chat.id, '''
#         Кажется, мне не достает данных, проверь был ли введен вес и первичные данные, которые я спрашивал на старте 😉
#         ''')
#         send_keyboard(msg)

def variation(msg):
    variation_calories = round(200)
    fat_nutrient = round((0.35 * variation_calories) / 9)
    protein_nutrient = round((0.25 * variation_calories) / 4)
    carbs_nutrient = round((0.4 * variation_calories) / 4)
    fat_nutrient_lc = round((0.45 * variation_calories) / 9)
    protein_nutrient_lc = round((0.45 * variation_calories) / 4)
    carbs_nutrient_lc = round((0.1 * variation_calories) / 4)
    bot.send_message(msg.chat.id, f'''
    Каждый из нас индивидуален, поэтому если процесс не идет или идет слишком быстро \- попробуй изменить рекомендованный рацион на \+\- *200* калорий\.
    \nЕсли ты худеешь по классической схеме, то по белкам, жирам и углеводам это будет следующее количество:
    \n★ *{fat_nutrient}* г жиров;
    \n★ *{protein_nutrient}* г белков;
    \n★ *{carbs_nutrient}* г углеводов{backslash}.
    \nДля тех, кто использует низкоуглеводную схему:
    \n★ *{fat_nutrient_lc}* г жиров;
    \n★ *{protein_nutrient_lc}* г белков;
    \n★ *{carbs_nutrient_lc}* г углеводов{backslash}.   
    \nУспехов{backslash}! 😎
    ''', parse_mode="MarkdownV2")
    send_keyboard(msg)

def callback_worker(call):
    if call.text == "Хочу сообщить свой вес 😱":
        msg = bot.send_message(call.chat.id, f'''
        \nСупер! Можешь прислать текущий вес или исторический, я все отсортирую 😜
        \nОтправляй в формате "дата вес" разделение = пробел, мне нужно записать это в свой журнал:)
        \nПример формата: dd-mm-yyyy 85.4 
        \nПервая часть = дата (например: 31-12-2021), а вторая = вес (в нашем примере: 85.4)''')
        bot.register_next_step_handler(msg, add_weight)
    elif call.text == "Хочу согнать жирок 🥦":
        try:
            activity_keyboard(call, text = "Хочу согнать жирок 🥦")
        except Exception as e:
            bot.send_message(call.chat.id, 'Кажется, нет данных о твоем весе, необходимо сначала их ввести 😛')
            send_keyboard(call, "Чем еще могу помочь?")
    elif call.text == "Хочу поднабрать массы 💪":
        try:
            activity_keyboard(call, text = "Хочу поднабрать массы 💪")
        except Exception as e:
            bot.send_message(call.chat.id, 'Кажется, нет данных о твоем весе, необходимо сначала их ввести 😛')
            send_keyboard(call, "Чем еще могу помочь?")
    elif call.text == "Хочу посмотреть статистику своего веса 😈":
        try:
            weight_statistic(call)
        except Exception as e:
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
        except Exception as e:
            bot.send_message(call.chat.id, 'Кажется, нет данных, необходимо сначала их ввести 😛')
            send_keyboard(call, "Чем еще могу помочь?")
    elif call.text == "Не худею/не набираю 👿":
        try:
            variation(call)
        except:
            bot.send_message(call.chat.id, 'Произошла ошибка, повтори команду.')
    elif call.text == "Очистить данные из базы (имя, возраст, пол, рост)":
        try:
            delete_user_info(call)
        except Exception as e:
            bot.send_message(call.chat.id, 'Кажется, нет данных, необходимо сначала их ввести 😛')
            send_keyboard(call, "Чем еще могу помочь?")

def add_weight(msg):
    current_date = msg.text.split()[0]
    current_weight = msg.text.split()[1]
    try:
        float(current_weight)
        current_weight = float(current_weight)
        dt_obj = dt.datetime.strptime(f"{current_date}", "%d-%m-%Y").date()
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
    return ''.join(sorted(data_str))

def weight_statistic(msg):
    with psycopg2.connect(db_URL, sslmode="require") as postgre_con:
        db_obj = postgre_con.cursor()
        db_obj.execute(f'''SELECT to_date(date, 'DD/MM/YYYY') AS date_column, weight FROM bot_users_weights_table WHERE "user_id"={msg.from_user.id} ORDER BY date_column''')
        c = db_obj.fetchall()
        data_list = get_nice(c)
        postgre_con.commit()
        db_obj.close()
        bot.send_message(msg.chat.id, data_list)
        send_keyboard(msg, "Ох! Сначала подумал, что это пример геометрической прогрессии, а оказалось..")

def delete_last(msg):
    with psycopg2.connect(db_URL, sslmode="require") as postgre_con:
        db_obj = postgre_con.cursor()
        db_obj.execute(f'''
        DELETE FROM bot_users_weights_table 
        WHERE id = (SELECT MAX(id) as max_id 
            FROM bot_users_weights_table 
            WHERE user_id = {msg.from_user.id})
        ''')
        postgre_con.commit()
        db_obj.close()
        bot.send_message(msg.chat.id, 'Прошло успешно!')
        send_keyboard(msg, "Чем еще могу помочь?")

def delete_all(msg):
    with psycopg2.connect(db_URL, sslmode="require") as postgre_con:
        db_obj = postgre_con.cursor()
        db_obj.execute(f'DELETE FROM bot_users_weights_table WHERE "user_id"={msg.from_user.id}')
        postgre_con.commit()
        db_obj.close()
        bot.send_message(msg.chat.id, 'И начнем все с чистого листа! 🥂')
        send_keyboard(msg, "Чем еще могу помочь?")

def delete_user_info(msg):
    with psycopg2.connect(db_URL, sslmode="require") as postgre_con:
        db_obj = postgre_con.cursor()
        db_obj.execute(f'DELETE FROM bot_users_list WHERE "user_id"={msg.from_user.id}')
        postgre_con.commit()
        db_obj.close()
        bot.send_message(msg.chat.id, 'Все данные удалены 🥳')
        send_keyboard(msg, "Чем еще могу помочь?")

@bot.message_handler(commands=['help'])
def help(message):
    msg = bot.reply_to(message, "Выбирай интересующий тебя раздел! Если я еще не знаю твой возраст и рост - вызывай команду start 😉")
    send_keyboard(message)

@bot.message_handler(content_types=['text'])
def sorry(message):
    send_keyboard(message, text="Я не понимаю!🌚 Выбери один из пунктов меню:")


bot.infinity_polling()