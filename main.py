import telebot
from telebot import types
import statistics
import sqlite3
bot = telebot.TeleBot("5058162485:AAHGx9-XieFGAaHLb3cVumTcokI1RkwGJbg")
user_dict = {}
class User:
    def __init__(self, name):
        self.name = name
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    msg = bot.reply_to(message, "Хэй! Меня зовут Фитобот😊 А тебя как?")
    bot.register_next_step_handler(msg, user_name)
def send_keyboard(message, text = "Выбери интересующий раздел 😉"):
    keyboard = types.ReplyKeyboardMarkup(row_width=2)
    itembtn0 = types.KeyboardButton('Хочу сообщить свой текущий вес 😱')
    itembtn1 = types.KeyboardButton('Хочу поднабрать массы 💪')
    itembtn2 = types.KeyboardButton('Хочу согнать жирок 🥦')
    itembtn3 = types.KeyboardButton('Хочу посмотреть статистику своего веса 😈')
    itembtn4 = types.KeyboardButton('Удалить последнюю запись веса')
    itembtn5 = types.KeyboardButton("Удалить все записи")
    keyboard.add(itembtn0, itembtn1, itembtn2, itembtn3, itembtn4, itembtn5)
    msg = bot.send_message(message.from_user.id,
                     text=text, reply_markup=keyboard)
    bot.register_next_step_handler(msg, callback_worker)
def user_name(message):
    try:
        chat_id = message.chat.id
        name = message.text.title()
        user = User(name)
        user_dict[chat_id] = user
        msg = bot.send_message(message.from_user.id, f'''Привет! Приятно познакомиться, {name} 😜. Выбирай интересующую тебя тему:) И при первом использовании не забудь ввести свой текущий вес!)''')
        send_keyboard(message)
        bot.register_next_step_handler(msg, callback_worker)
    except Exception as e:
        bot.reply_to(message, 'Сорри, меня отвлекли, давай попробуем еще раз 🙏')
conn = sqlite3.connect('fit_o_bot.db')
cursor = conn.cursor()
try:
    query = "CREATE TABLE \"users_weights_table\" (\"ID\" INTEGER UNIQUE, \"user_id\" INTEGER,\"date\" DATE,\"weight\" FLOAT, PRIMARY KEY (\"ID\"))"
    cursor.execute(query)
except:
    pass
def add_weight(msg):
    current_date = msg.text.split()[0]
    current_weight = msg.text.split()[1]
    try:
        float(current_weight)
        with sqlite3.connect('fit_o_bot.db') as con:
            cursor = con.cursor()
            cursor.execute('INSERT INTO users_weights_table (user_id, date, weight) VALUES (?, ?, ?)',
                           (msg.from_user.id, current_date, current_weight))
            con.commit()
        bot.send_message(msg.chat.id, 'Как когда-то сказал Аристотель: \"Познание всегда начинается с удивления\"..')
        send_keyboard(msg)
    except:
        bot.send_message(msg.chat.id, 'Введен некорректный формат :(')
        send_keyboard(msg)
def get_nice(data_list):
    data_str = []
    for val in list(data_list):
        data_str.append(f'{val[0]} = {val[1]} кг\n')
    return ''.join(data_str)
def weight_statistic(msg):
    with sqlite3.connect('fit_o_bot.db') as con:
        cursor = con.cursor()
        cursor.execute(f'SELECT date, weight FROM users_weights_table WHERE user_id=={msg.from_user.id}')
        c = cursor.fetchall()
        data_list = get_nice(c)
        bot.send_message(msg.chat.id, data_list)
        send_keyboard(msg, "Ох! Сначала подумал, что это пример геометрической прогрессии, а оказалось..")
def pretiffy_weight(last_weight):
    for val in last_weight:
        last_w = val[0]
        return last_w
def increase_weight(msg):
    with sqlite3.connect('fit_o_bot.db') as con:
        cursor = con.cursor()
        cursor.execute(f'SELECT weight FROM users_weights_table WHERE user_id=={msg.from_user.id} ORDER BY ID DESC LIMIT 1')
        last_weight = pretiffy_weight(cursor.fetchall())
        target_weight = round((last_weight + 4), 2)
        fats_nutrient = round(target_weight * 1)
        protein_nutrient = round(target_weight * 2.2)
        carbs_nutrient = round(target_weight * 3.5)
        total_calories = round(fats_nutrient * 9) + (protein_nutrient * 4) + (carbs_nutrient * 4)
        bot.send_message(msg.chat.id, f'''
        Такс 🤔, судя по имеющимся у меня данным твой текущий и последний записанный вес составляет {last_weight} кг. 
        \nЕсли это не так - тебе нужно обновить информацию, сообщив свой текущий вес в соответствующей команде.
        \nВ целях комфортного набора ставим планку целевого веса в {target_weight} кг. Для достижения цели тебе следует придерживаться следующих ежесуточных пропорций в питании:
        \n- {fats_nutrient} г жиров;
        \n- {protein_nutrient} г белков;
        \n- {carbs_nutrient} г углеводов.
        \nИтого твой суммарный рацион за день составит {total_calories} ккал.
        \nДля подсчета и записи будут очень полезны соответствующие приложения, а также кухонные весы. Не забывай, что зачастую каллорийность продукта указана на сухой (не готовый) продукт. Поэтому взвешивать все проще до готовки. Заморачиваться до каждой каллории не рекомендую, так как разброс от заявленного может доходить до +- 10%. Мы скорее определяем вектор и правильное соотношение нутриентов. Углеводы постарайся использовать медленные, а жиры полезные (если не знакомо - гугл подскажет). 
        \nНу и не забывай об активности, ежедневная ходьба и желательно три тренировки в неделю, а также о соблюдении питьевого режима (именно чистой воды).
        \nПо достижении целевого веса, можешь обновить данные и я произведу перерасчет под новую цель. 
        \nУдачи! Все получится ☺️
''')
        send_keyboard(msg)
def decrease_weight(msg):
    with sqlite3.connect('fit_o_bot.db') as con:
        cursor = con.cursor()
        cursor.execute(f'SELECT weight FROM users_weights_table WHERE user_id=={msg.from_user.id} ORDER BY ID DESC LIMIT 1')
        last_weight = pretiffy_weight(cursor.fetchall())
        target_weight = round((last_weight - 4), 2)
        fats_nutrient = round(target_weight * 1.2)
        protein_nutrient = round(target_weight * 2.5)
        carbs_nutrient = round(target_weight * 1)
        total_calories = round((fats_nutrient * 9) + (protein_nutrient * 4) + (carbs_nutrient * 4))
        bot.send_message(msg.chat.id, f'''
        Хорошо 👍, судя по имеющимся у меня данным твой текущий и последний записанный вес составляет {last_weight} кг.
        \nЕсли это не так - тебе нужно обновить информацию, сообщив свой текущий вес в соответствующей команде.
        \nВ целях комфортного снижения веса обозначим целевое значение в {target_weight} кг. Для достижения цели тебе следует придерживаться следующих ежесуточных пропорций в питании:
        \n- {fats_nutrient} г жиров;
        \n- {protein_nutrient} г белков;
        \n- {carbs_nutrient} г углеводов.
        \nИтого твой суммарный рацион за день составит {total_calories} ккал.
        \nДля подсчета и записи будут очень полезны соответствующие приложения, а также кухонные весы. Не забывай, что зачастую каллорийность продукта указана на сухой (не готовый) продукт. Поэтому взвешивать все проще до готовки. Заморачиваться до каждой каллории не рекомендую, так как разброс от заявленного может доходить до +- 10%. Мы скорее определяем вектор и правильное соотношение нутриентов. Углеводы постарайся использовать медленные, а жиры полезные (если не знакомо - гугл подскажет).
        \nПоскольку твоя цель снижение веса - рекомендую использовать в рационе побольше клетчаки и особенно необходимо не забывать о соблюдении питьевого режима. Ежедневная ходьба и тренировки три раза в неделю - приветствуются!
        \nПомни, что снижение жира является стрессом для организма, поэтому перед данным процессом нужно проконсультироваться с врачом и убедиться, что у тебя нет противопоказаний к такому типу питания. 
        \nПредложенная мной пропорция нутриентов довольна эффективна для снижения подкожного жира, но ввиду малого количества углеводов надо быть готовым к плохому настроению и ощущению пониженной энергии, особенно в первое время. Однако, она включает в себя хорошее потребление жиров и белков, что является более важным. Поскольку жиры отвечают за гормональную систему, а белки выступают в качестве строительного материала для всего организма. Для психологического комфорта рекомендую попробовать следующее. Делать что-то вроде интервала, в течение 3 дней придерживаться данной пропорции, затем один день использовать следующую:
        \n- {round(target_weight * 1.2)} г жиров;
        \n- {round(target_weight * 1.5)} г белков;
        \n- {round(target_weight * 2)} г углеводов.
        \nКалорийоность будет той же, но в этот день мы снизим потребление белка и повысим потребление углеводов.
        \nПо достижении целевого веса, можешь обновить данные и я произведу перерасчет под новую цель. 
        \n Удачи! Все получится ☺️
        ''')
        send_keyboard(msg)
def delete_last(msg):
    with sqlite3.connect('fit_o_bot.db') as con:
        cursor = con.cursor()
        cursor.execute(f'DELETE FROM users_weights_table WHERE user_id=={msg.from_user.id} ORDER BY ID DESC LIMIT 1')
        bot.send_message(msg.chat.id, 'Прошло успешно!')
        send_keyboard(msg, "Чем еще могу помочь?")
def delete_all(msg):
    with sqlite3.connect('fit_o_bot.db') as con:
        cursor = con.cursor()
        cursor.execute(f'DELETE FROM users_weights_table WHERE user_id=={msg.from_user.id}')
        con.commit()
    bot.send_message(msg.chat.id, 'И начнем все с чистого листа! 🥂')
    send_keyboard(msg, "Чем еще могу помочь?")
def callback_worker(call):
    if call.text == "Хочу сообщить свой текущий вес 😱":
        msg = bot.send_message(call.chat.id, '''
            Не бойся, отправляй свой текущий вес, на своем веку я видал многое..
        Присылай в формате текущей даты и веса разделенных пробелом, мне нужно записать это в свой журнал:)
        Например: 05.12.2021 87.77 (где первая часть - дата, а вторая - вес).''')
        bot.register_next_step_handler(msg, add_weight)

    elif call.text == "Хочу поднабрать массы 💪":
        try:
            increase_weight(call)
        except:
            bot.send_message(call.chat.id, 'Кажется, нет данных о твоем весе, необходимо сначала их ввести 😛')
            send_keyboard(call, "Чем еще могу помочь?")

    elif call.text == "Хочу согнать жирок 🥦":
        try:
            decrease_weight(call)
        except:
            bot.send_message(call.chat.id, 'Кажется, нет данных о твоем весе, необходимо сначала их ввести 😛')
            send_keyboard(call, "Чем еще могу помочь?")

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
    elif call.text == "Удалить все записи":
        try:
            delete_all(call)
        except:
            bot.send_message(call.chat.id, 'Кажется, нет данных о твоем весе, необходимо сначала их ввести 😛')
            send_keyboard(call, "Чем еще могу помочь?")
@bot.message_handler(content_types=['text'])
def handle_docs_audio(message):
    send_keyboard(message, text="Я не понимаю :-( Выбери один из пунктов меню:")
bot.infinity_polling()
